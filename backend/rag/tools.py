import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from openai import AzureOpenAI
from rag.embedder import embed_text
from rag.vector_store import search_chunk, get_client, COLLECTION_NAME
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

######## tool for the searching the relevant document for the user query. ########
def search_tool(query: str, filters: dict = None) -> dict:
    logger.info(f"Search tool called with query: {query}")

    query_vector = embed_text(query)
    chunks = search_chunk(
        query_vector=query_vector,
        top_k=10,
        filters=filters
    )
    # for i, chunk in enumerate(chunks):
    #     print(f"Chunk {i + 1}: {chunk['metadata']['document_name']} — score: {chunk['score']}")
    #     print(f"Text preview: {chunk['text'][:200]}")
    #     print("─" * 30)

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

    score_1 = round(chunks_1[0]["score"], 4) if chunks_1 else 1.0
    score_2 = round(chunks_2[0]["score"], 4) if chunks_2 else 1.0

    return {
        "answer": answer,
        "citations": [
            {
                "document_name": exact_name_1,
                "document_type": match_1[0].get("document_type", ""),
                "category": match_1[0].get("category", ""),
                "page_id": match_1[0].get("page_id", ""),
                "score": score_1
            },
            {
                "document_name": exact_name_2,
                "document_type": match_2[0].get("document_type", ""),
                "category": match_2[0].get("category", ""),
                "page_id": match_2[0].get("page_id", ""),
                "score": score_2
            }
        ]
    }


def handle_general_query(query: str, messages: list = None, summary: str = "") -> tuple[bool, str]:
    # Build conversation context from memory
    context = ""
    if summary:
        context += f"Previous conversation summary:\n{summary}\n\n"

    if messages:
        context += "Recent conversation:\n"
        for msg in messages[-4:]:  # last 4 messages only
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            context += f"{role}: {content}\n"
        context += "\n"

    prompt = f"""You are an AI document assistant for a SaaS company.
    You have access to 92 company documents including Policies, Procedures, Guides, Plans, Agreements and Records.
    
    {context}
    Current message from user: "{query}"
    
    First decide — is this a general greeting or casual 
    conversation OR is it a question that requires searching 
    company documents?
    
    IMPORTANT RULES for classification:
    - If the message asks about company policies, procedures,
      counts, numbers, details → DOCUMENT_QUERY
    - If the message is a greeting, introduction, or casual 
      chat → general response
    - If the message asks a follow up question about documents
      or information → DOCUMENT_QUERY
    - When in doubt → DOCUMENT_QUERY

    If it is a general greeting or conversation — respond naturally and helpfully using the conversation history above.
    If it is a document question — respond with exactly: DOCUMENT_QUERY
    
    Rules for general response:
    - Be friendly and professional
    - Use conversation history to answer personal questions (like remembering user's name)
    - Mention you can search company documents
    - Mention you can compare two documents
    - Keep response concise — 2 to 3 sentences maximum
    - Never say you are an AI language model
    - Say you are a document assistant
    
    Respond with either DOCUMENT_QUERY or your friendly response."""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    answer = response.choices[0].message.content.strip()

    if answer == "DOCUMENT_QUERY":
        return False, ""
    else:
        return True, answer

######## This is for the checking the message is available or not ########
def check_answer_quality(question: str, answer: str) -> bool:
    """
    Uses LLM to judge if the answer properly addresses
    the user's question.

    Why LLM instead of hardcoded phrases:
    - Understands meaning not just exact phrases
    - Catches any form of "no answer found"
    - Works even if LLM phrases response differently
    - More intelligent and flexible

    Args:
        question : original user question
        answer   : answer returned by search_tool

    Returns:
        True  → answer is good → return to user
        False → answer is bad  → create ticket
    """
    logger.info(f"Checking answer quality for: {question[:50]}")

    prompt = f"""You are evaluating whether an answer properly addresses a user's question.

    Question: {question}
    
    Answer: {answer}
    
    Carefully evaluate:
    - Does the answer contain relevant information about the question?
    - Or does it say it could not find information?
    - Or is it vague and does not address the question at all?
    
    Reply with ONLY one word:
    YES — if the answer properly addresses the question
    NO  — if the answer could not find relevant information or is vague
    
    Your reply:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    result = response.choices[0].message.content.strip().upper()
    is_good = result == "YES"

    logger.info(f"Answer quality check: {'GOOD' if is_good else 'BAD — will create ticket'}")
    return is_good

######## This funstions is for the summarizing the history ########
def summarize_messages(messages: list, existing_summary: str = "") -> str:
    """
    Summarizes the oldest 4 messages into a compact summary.
    Combines with existing summary if one exists.

    How it works:
    - Takes messages list (at least 4 messages)
    - Formats them as readable conversation
    - Sends to LLM with existing summary
    - LLM creates updated compact summary
    - Returns updated summary string

    Args:
        messages         : list of message dicts
                           each dict has 'role' and 'content'
        existing_summary : previous summary (empty on first call)

    Returns:
        updated summary string (max ~200 words)
    """
    logger.info("Summarizing conversation messages...")

    # Format oldest 4 messages into readable text
    messages_text = ""
    for msg in messages[:4]:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        messages_text += f"{role}: {content}\n\n"

    # Build prompt — combines existing summary with new messages
    if existing_summary:
        prompt = f"""You are summarizing a conversation between a user and a document assistant.

    Existing summary of earlier conversation:
    {existing_summary}
    
    New messages to add to the summary:
    {messages_text}
    
    Create an updated summary that:
    - Combines the existing summary with the new messages
    - Captures key topics discussed
    - Captures questions asked and answers given
    - Is concise — maximum 200 words
    - Written in third person (e.g. "User asked about...")
    
    Updated summary:"""
    else:
        prompt = f"""You are summarizing a conversation between a user and a document assistant.

    Conversation to summarize:
    {messages_text}
    
    Create a summary that:
    - Captures key topics discussed
    - Captures questions asked and answers given
    - Is concise — maximum 200 words
    - Written in third person (e.g. "User asked about...")
    
    Summary:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    summary = response.choices[0].message.content.strip()
    logger.info(f"Summary generated: {summary[:100]}...")
    return summary
