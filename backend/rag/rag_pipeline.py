import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
from openai import AzureOpenAI
from .notions_loader import load_all_documents
from .chunker import  chunk_all_documents
from .embedder import embed_chunks, embed_text
from .vector_store import create_collection, insert_chunks, search_chunk

from rag.logger import logger
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPEN_API_KEY"),
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")


###### Ingestion Functions ######
def ingest_documents(limit: int=None):
    try:
        logger.info("Ingestion started")

        logger.info("Step 1 — Creating Milvus collection...")
        create_collection()

        logger.info("Step 2 — Loading documents from Notion...")
        documents = load_all_documents()
        print(f"DEBUG — Documents loaded before limit: {len(documents)}")

        if limit:
            documents = documents[:limit]
            logger.info(f"Limited to {limit} documents for testing")

        logger.info(f"Loaded {len(documents)} documents")

        logger.info("Step 3 — Chunking documents...")
        chunks = chunk_all_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")

        logger.info("Step 4 — Embedding chunks...")
        embedded = embed_chunks(chunks)
        logger.info(f"Embedded {len(embedded)} chunks")

        logger.info("Step 5 — Storing in Milvus...")
        insert_chunks(embedded)

        logger.info("Ingestion complete!")
        return {
            "documents": len(documents),
            "chunks": len(chunks)
        }
    except Exception as e:
        logger.error(f"Ingestion failed — {str(e)}")
        raise


###### Build prompt with retrieved chunks #######
def build_rag_prompt(question: str, chunks: list) -> str:
    context = ""
    for i, chunk in enumerate(chunks):
        doc_name = chunk["metadata"]["document_name"]
        doc_type = chunk["metadata"]["document_type"]
        context += f"\n\n--- Source {i+1}: {doc_name} ({doc_type}) ---\n"
        context += chunk["text"]

    prompt = f"""You are a helpful assistant for a SaaS company.
    Answer the user's question based ONLY on the provided context below.
    If the answer is not in the context, say "I could not find relevant information in the documents."

    Context:
    {context}

    Question: {question}

    Rules:
    - Answer clearly and professionally
    - Always mention which document you got the information from
    - If multiple documents are relevant mention all of them
    - Do not make up information that is not in the context

    Answer:"""
    return prompt

######## Query function ########
def query(question: str, filters: dict = None, top_k: int = 5) -> dict:
    try:
        logger.info(f"Query received: {question}")

        # Convert question to vector
        question_vector = embed_text(question)
        logger.info("Question embedded successfully")

        # Search Milvus for relevant chunks
        relevant_chunks = search_chunk(
            query_vector=question_vector,
            top_k=top_k,
            filters=filters
        )
        logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks")

        if not relevant_chunks:
            logger.warning("No relevant chunks found for the query")
            return {
                "answer": "No relevant documents found.",
                "citations": []
            }

        # Build prompt with context
        prompt = build_rag_prompt(question, relevant_chunks)

        # Generate answer using LLM
        logger.info("Generating answer using LLM...")
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        answer = response.choices[0].message.content
        logger.info("Answer generated successfully")

        # Build citations
        citations = []
        seen = set()
        for chunk in relevant_chunks:
            doc_name = chunk["metadata"]["document_name"]
            if doc_name not in seen:
                seen.add(doc_name)
                citations.append({
                    "document_name": doc_name,
                    "document_type": chunk["metadata"]["document_type"],
                    "category": chunk["metadata"]["category"],
                    "page_id": chunk["metadata"]["page_id"],
                    "score": round(chunk["score"], 4)
                })

        logger.info(f"Citations built — {len(citations)} unique documents referenced")
        return {
            "answer": answer,
            "citations": citations
        }

    except Exception as e:
        logger.error(f"Query failed — {str(e)}")
        raise

######## Compare Functions ########
def compare(question: str, filters: dict = None) -> dict:
    try:
        logger.info(f"Compare request received: {question}")

        question_vector = embed_text(question)
        logger.info("Question embedded successfully")

        relevant_chunks = search_chunk(
            query_vector=question_vector,
            top_k=10,
            filters=filters
        )
        logger.info(f"Retrieved {len(relevant_chunks)} chunks for comparison")

        if not relevant_chunks:
            logger.warning("No relevant chunks found for comparison")
            return {
                "answer": "No relevant documents found for comparison.",
                "citations": []
            }

        context = ""
        for i, chunk in enumerate(relevant_chunks):
            doc_name = chunk["metadata"]["document_name"]
            doc_type = chunk["metadata"]["document_type"]
            context += f"\n\n--- Document {i+1}: {doc_name} ({doc_type}) ---\n"
            context += chunk["text"]

        prompt = f"""You are a helpful assistant for a SaaS company.
        Compare the information across the following documents and provide a clear comparison.
        Highlight similarities and differences between the documents.

        Documents:
        {context}

        Question: {question}

        Provide a structured comparison with clear headings for each document."""

        logger.info("Generating comparison using LLM...")
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        answer = response.choices[0].message.content
        logger.info("Comparison generated successfully")

        citations = []
        seen = set()
        for chunk in relevant_chunks:
            doc_name = chunk["metadata"]["document_name"]
            if doc_name not in seen:
                seen.add(doc_name)
                citations.append({
                    "document_name": doc_name,
                    "document_type": chunk["metadata"]["document_type"],
                    "category": chunk["metadata"]["category"],
                })

        logger.info(f"Comparison complete — {len(citations)} documents compared")
        return {
            "answer": answer,
            "citations": citations
        }

    except Exception as e:
        logger.error(f"Compare failed — {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        logger.info("Starting ingestion process...")
        result = ingest_documents()
        logger.info(f"Ingestion complete — {result['documents']} documents, {result['chunks']} chunks")
    else:
        logger.info("Starting query test...")
        result = query("What is the remote work policy?")
        print(f"Answer: {result['answer']}")
        print(f"Citations: {result['citations']}")