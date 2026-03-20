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
    prompt = f"""Extract the two document names the user wants to compare.
    Return ONLY a Python list: ["Document A", "Document B"]
    Rules:
    - Extract core name only — remove words like "policy", "document", "the"
    - Keep names short — 2 to 4 words maximum
    - Return ONLY the Python list — nothing else
    
    Examples:
    "Compare Code of Conduct and Work from Home" → ["Code of Conduct", "Work from Home"]
    "Compare testing strategy and A/B testing" → ["testing strategy", "A/B testing"]
    "Compare Remote Work Policy and Leave Policy" → ["Remote Work", "Leave"]

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

    # Step 1 — find exact document names in Milvus
    match_1 = milvus_client.query(
        collection_name=COLLECTION_NAME,
        filter=f'document_name like "%{doc_name_1}%"',
        output_fields=["document_name", "document_type", "category", "page_id"],
        limit=1
    )

    match_2 = milvus_client.query(
        collection_name=COLLECTION_NAME,
        filter=f'document_name like "%{doc_name_2}%"',
        output_fields=["document_name", "document_type", "category", "page_id"],
        limit=1
    )

    if not match_1:
        return {
            "answer": f"Could not find document matching: {doc_name_1}",
            "citations": []
        }

    if not match_2:
        return {
            "answer": f"Could not find document matching: {doc_name_2}",
            "citations": []
        }

    exact_name_1 = match_1[0]["document_name"]
    exact_name_2 = match_2[0]["document_name"]
    logger.info(f"Exact names — Doc1: {exact_name_1} | Doc2: {exact_name_2}")

    # Step 2 — use document name as search query
    # embed the name and search within that specific document
    query_vector_1 = embed_text(doc_name_1)
    query_vector_2 = embed_text(doc_name_2)

    # Step 3 — search Milvus with vector + document name filter
    chunks_1 = search_chunk(
        query_vector=query_vector_1,
        top_k=10,
        filters={"document_name_exact": exact_name_1}
    )

    chunks_2 = search_chunk(
        query_vector=query_vector_2,
        top_k=10,
        filters={"document_name_exact": exact_name_2}
    )

    logger.info(f"Retrieved {len(chunks_1)} chunks for {exact_name_1}")
    logger.info(f"Retrieved {len(chunks_2)} chunks for {exact_name_2}")

    # Step 4 — build context
    context_1 = f"=== Document 1: {exact_name_1} ===\n"
    for chunk in chunks_1:
        context_1 += chunk["text"] + "\n\n"

    context_2 = f"=== Document 2: {exact_name_2} ===\n"
    for chunk in chunks_2:
        context_2 += chunk["text"] + "\n\n"

    # Step 5 — LLM compares
    prompt = f"""You are a helpful assistant for a SaaS company.
    Compare the following two documents in detail based on their content.
    
    {context_1}
    
    {context_2}
    
    Provide a comprehensive structured comparison covering:
    1. **Purpose & Scope** — What is each document about?
    2. **Key Similarities** — What do both documents have in common?
    3. **Key Differences** — How are they different?
    4. **Summary** — Key takeaways
    
    Be specific and reference actual content from both documents."""

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
            {
                "document_name": exact_name_1,
                "document_type": match_1[0].get("document_type", ""),
                "category": match_1[0].get("category", ""),
                "page_id": match_1[0].get("page_id", "")
            },
            {
                "document_name": exact_name_2,
                "document_type": match_2[0].get("document_type", ""),
                "category": match_2[0].get("category", ""),
                "page_id": match_2[0].get("page_id", "")
            }
        ]
    }