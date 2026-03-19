import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from openai import AzureOpenAI
from .embedder import embed_text
from .vector_store import search_chunk, get_client, COLLECTION_NAME
from rag.logger import logger

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPEN_API_KEY"),
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

######## refine query part ########
def refine_query(user_query: str) -> str:
    logger.info(f"Refining query: {user_query}")

    prompt = f"""You are a search query optimizer for a SaaS document management system.

    Your job is to rewrite the user's query into a better search query that will find the most relevant documents.
    
    Rules:
    - Make the query more specific and clear
    - Remove vague words like "tell me about" or "what is"
    - Keep important keywords
    - If the query is about comparing two documents extract both document names clearly
    - Return ONLY the refined query — nothing else
    
    User query: {user_query}
    
    Refined query:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    refined = response.choices[0].message.content.strip()
    logger.info(f"Refined query: {refined}")
    return refined


#######  check of the query is for the comparing or not. #######
def is_compare_query(query: str) -> bool:
    prompt = f"""Does the following query ask to compare two or more documents?
Answer with only YES or NO.

Query: {query}"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    answer = response.choices[0].message.content.strip().upper()
    return answer == "YES"

#### Extract the Document for the comparing part.
def extract_document_names(query: str) -> list:
    prompt = f"""Extract the document names that the user wants to compare from the query below.
    Return ONLY a Python list of document names like: ["Document A", "Document B"]
    If no specific document names are mentioned return an empty list: []

    Query: {query}"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    try:
        import ast
        result = response.choices[0].message.content.strip()
        names = ast.literal_eval(result)
        logger.info(f"Extracted document names: {names}")
        return names
    except:
        logger.warning("Could not extract document names")
        return []

######## tool for he searching the relevant document for the user query. ########
def search_tool(query: str, filters: dict = None) -> dict:
    logger.info(f"Search tool called with query: {query}")

    query_vector = embed_text(query)
    chunks = search_chunk(
        query_vector=query_vector,
        top_k=10,
        filters=filters
    )
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}: {chunk['metadata']['document_name']} — score: {chunk['score']}")
        print(f"Text preview: {chunk['text'][:200]}")
        print("─" * 30)

    if not chunks:
        return {
            "answer": "No relevant documents found.",
            "citations": []
        }

    context = ""
    for i, chunk in enumerate(chunks):
        doc_name = chunk["metadata"]["document_name"]
        doc_type = chunk["metadata"]["document_type"]
        context += f"\n\n--- Source {i+1}: {doc_name} ({doc_type}) ---\n"
        context += chunk["text"]

    prompt = f"""You are a helpful assistant for a SaaS company.
    Answer the question based ONLY on the provided context.
    If the answer is not in the context say "I could not find relevant information in the documents."
    
    Context:
    {context}
    
    Question: {query}
    
    Rules:
    - Answer clearly and professionally
    - Always mention which document the information came from
    - Do not make up any information
    
    Answer:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    answer = response.choices[0].message.content

    citations = []
    seen = set()
    for chunk in chunks:
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

    logger.info(f"Search complete — {len(citations)} documents cited")
    return {
        "answer": answer,
        "citations": citations
    }

######## this tool is for the comparing the 2 documents ########
def compare_tool(doc_name_1: str, doc_name_2: str) -> dict:
    logger.info(f"Compare tool called: {doc_name_1} vs {doc_name_2}")

    milvus_client = get_client()

    # Fetch chunks from document 1
    results_1 = milvus_client.query(
        collection_name=COLLECTION_NAME,
        filter=f'document_name == "{doc_name_1}"',
        output_fields=["text", "document_name", "document_type", "category", "page_id"]
    )

    # Fetch chunks from document 2
    results_2 = milvus_client.query(
        collection_name=COLLECTION_NAME,
        filter=f'document_name == "{doc_name_2}"',
        output_fields=["text", "document_name", "document_type", "category", "page_id"]
    )

    if not results_1 and not results_2:
        return {
            "answer": f"Could not find documents: {doc_name_1} and {doc_name_2}",
            "citations": []
        }

    # Build context for doc 1
    context_1 = f"--- Document 1: {doc_name_1} ---\n"
    for r in results_1[:5]:
        context_1 += r["text"] + "\n"

    # Build context for doc 2
    context_2 = f"--- Document 2: {doc_name_2} ---\n"
    for r in results_2[:5]:
        context_2 += r["text"] + "\n"

    prompt = f"""You are a helpful assistant for a SaaS company.
    Compare the following two documents clearly and professionally.
    Highlight key similarities and differences.
    Structure your comparison with clear sections.
    
    {context_1}
    
    {context_2}
    
    Provide a structured comparison covering:
    1. Purpose and scope
    2. Key similarities
    3. Key differences
    4. Summary"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    answer = response.choices[0].message.content
    logger.info("Comparison generated successfully")

    return {
        "answer": answer,
        "citations": [
            {"document_name": doc_name_1},
            {"document_name": doc_name_2}
        ]
    }