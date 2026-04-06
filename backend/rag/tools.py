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
def extract_document_names(query: str, messages: list = None, summary: str = "") -> list:
    """
    Extracts two document names for comparison.
    Looks at both conversation summary AND recent messages.
    Does not modify or shorten document names.
    """
    # Build full conversation context — summary first then messages
    context = ""
    if summary:
        context += f"Conversation summary:\n{summary}\n\n"
    if messages:
        context += "Recent messages:\n"
        for msg in messages[-6:]:
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")[:200]
            context += f"{role}: {content}\n"
        context += "\n"

    prompt = f"""You are extracting two document names that a user wants to compare.

    {context}
    Current query: {query}

    Your task:
    - If the query explicitly names two documents → extract those names
    - If the query is vague (uses words like "both", "these", "them",
      "the two", "both policies") → look at the conversation summary 
      AND recent messages above to find the two most recently 
      discussed document names

    Rules for extraction:
    - Extract the CORE document title only
    - Remove company names (like "Turabit LLC", "Turbait LLC")
    - Remove phrases like "document", "for the company", "policy document"
    - Keep only the essential title — 2 to 5 words maximum
    - Always return exactly 2 names
    - If you cannot find 2 document names → return ["", ""]

    Return ONLY a valid Python list with exactly 2 strings.
    No explanation, no extra text, just the list.

    Your response:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    try:
        import ast
        result = response.choices[0].message.content.strip()
        names = ast.literal_eval(result)
        if isinstance(names, list) and len(names) == 2 and all(names):
            logger.info(f"Extracted document names: {names}")
            return names
        else:
            logger.warning(f"Invalid extraction result: {names}")
            return []
    except:
        logger.warning("Could not extract document names")
        return []

######## tool for the searching the relevant document for the user query. ########
def search_tool(query: str, filters: dict = None,
                messages: list = None, summary: str = "") -> dict:
    logger.info(f"Search tool called with query: {query}")

    query_vector = embed_text(query)
    chunks = search_chunk(
        query_vector=query_vector,
        top_k=10,
        filters=filters
    )

    # ── Build conversation context from memory ──
    conversation_context = ""
    if summary:
        conversation_context += f"Previous conversation summary:\n{summary}\n\n"
    if messages:
        conversation_context += "Recent conversation:\n"
        for msg in messages[-4:]:
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            conversation_context += f"{role}: {content}\n"
        conversation_context += "\n"

    # ── Build document context from chunks ──
    context = ""
    if chunks:
        for i, chunk in enumerate(chunks):
            doc_name = chunk["metadata"]["document_name"]
            doc_type = chunk["metadata"]["document_type"]
            context += f"\n\n--- Source {i+1}: {doc_name} ({doc_type}) ---\n"
            context += chunk["text"]

    # ── If no chunks AND no conversation context ──
    if not chunks and not conversation_context:
        return {
            "answer": "I could not find relevant information in the documents.",
            "citations": []
        }

    prompt = f"""You are a helpful assistant for a SaaS company.
    
    {conversation_context}
    Answer the question using EITHER the provided document context
    OR the conversation history above if the answer is already there.
    
    Document Context:
    {context if context else "No relevant document chunks found."}
    
    Question: {query}
    
    Rules:
    - If answer is in conversation history → use that directly
    - If answer is in document context → use that
    - If answer requires calculation from previous response → calculate it
    - If answer is truly not available in either source → say "I could not find relevant information in the documents."
    - Always mention source (document name or "based on our conversation")
    - Answer clearly and professionally
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


def handle_general_query(query: str,
                         messages: list = None,
                         summary: str = "") -> str:
    """
    Generates a friendly response for GENERAL_CHAT queries.
    Classification is already done by classify_and_followup_node.
    This function ONLY generates the response — no classification.

    Returns: response string directly (not tuple anymore)
    """
    logger.info(f"Handling general query: {query[:50]}")

    # Build conversation context
    context = ""
    if summary:
        context += f"Previous conversation summary:\n{summary}\n\n"
    if messages:
        context += "Recent conversation:\n"
        for msg in messages[-4:]:
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            context += f"{role}: {content}\n"
        context += "\n"

    prompt = f"""You are an AI document assistant for a SaaS company.
    You have access to 92 company documents including Policies, 
    Procedures, Guides, Plans, Agreements and Records.
    
    {context}
    Current message from user: "{query}"
    
    Respond naturally and helpfully using the conversation 
    history above if relevant.
    
    Rules:
    - Be friendly and professional
    - Use conversation history to answer personal questions
      (like remembering user's name)
    - Mention you can search company documents
    - Mention you can compare two documents
    - Keep response concise — 2 to 3 sentences maximum
    - Never say you are an AI language model
    - Say you are a document assistant
    
    Response:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

######## classifier of the query type ########
def classify_query(query: str) -> str:
    """
    Classifies query into 3 types:
    GENERAL_CHAT      → greetings, casual conversation
    GENERAL_KNOWLEDGE → general world knowledge questions
    COMPANY_QUERY     → company document related questions

    Returns: "GENERAL_CHAT", "GENERAL_KNOWLEDGE", or "COMPANY_QUERY"
    """
    logger.info(f"Classifying query: {query[:50]}")

    prompt = f"""You are a query classifier for a company document assistant.

    Classify the following query into exactly one of these 3 categories:

    GENERAL_CHAT      → greetings, casual conversation, personal questions
                        Intent: user is just chatting, not looking for information

    GENERAL_KNOWLEDGE → any query that falls outside company document scope:
                        - general world knowledge or famous people
                        - sensitive or confidential system information
                        - technical system details like code, configs, 
                          credentials, files, passwords, server details
                        - anything not related to company policies,
                          procedures or business documents
                        Intent: user is asking something that company 
                        documents would never contain

    COMPANY_QUERY     → questions about company policies, procedures,
                        guides, agreements, HR, legal, engineering,
                        finance, sales, product documents
                        Intent: user is looking for information that 
                        would be found in company documents

    Query: {query}

    Reply with ONLY one of these exact words:
    GENERAL_CHAT
    GENERAL_KNOWLEDGE
    COMPANY_QUERY"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    result = response.choices[0].message.content.strip().upper()

    # Safety check — if unexpected response default to COMPANY_QUERY
    if result not in ["GENERAL_CHAT", "GENERAL_KNOWLEDGE", "COMPANY_QUERY"]:
        logger.warning(f"Unexpected classification: {result} — defaulting to COMPANY_QUERY")
        result = "COMPANY_QUERY"

    logger.info(f"Query classified as: {result}")
    return result


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

def is_followup_query(query: str, messages: list) -> bool:
    """
    Detects if the user is asking a follow-up about
    the assistant's PREVIOUS response (summarize, rephrase,
    explain more, etc.) rather than asking a new document question.
    Returns True if it's a follow-up, False if it's a new query.
    """
    if not messages:
        return False

    # Get last assistant message to give LLM context
    last_assistant = ""
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            last_assistant = msg.get("content", "")[:300]
            break

    if not last_assistant:
        return False

    prompt = f"""You are deciding if a user's message requires 
    searching for new information or is only about reformatting 
    the assistant's previous response.

    Previous assistant response:
    \"\"\"{last_assistant}\"\"\"

    User's new message: "{query}"

    STRICT RULES:

    Reply YES only if the user's intent is PURELY about:
    - Changing the FORMAT of the previous response
    - Changing the LENGTH of the previous response
    - Changing the STYLE of the previous response
    - No new information is needed to answer

    Reply NO if the user's intent involves:
    - Getting any new or specific information
    - Asking about any policy, procedure or document
    - Requesting facts, numbers, dates or details
    - Any question that requires searching documents
    - Any topic not already fully covered in previous response
    - Any ambiguity about whether new info is needed

    IMPORTANT:
    - When in doubt → always reply NO
    - NO means search documents for fresh answer
    - YES means reformat previous response only

    Reply with only YES or NO:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    result = response.choices[0].message.content.strip().upper()
    logger.info(f"is_followup_query result: {result}")
    return result == "YES"


def answer_from_memory(query: str, messages: list, summary: str = "") -> str:
    """
    Answers a follow-up question using ONLY the conversation
    history — no document search needed.
    """
    context = ""
    if summary:
        context += f"Previous conversation summary:\n{summary}\n\n"
    if messages:
        context += "Recent conversation:\n"
        for msg in messages[-6:]:
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            context += f"{role}: {content}\n"

    prompt = f"""You are a helpful document assistant.
    The user is asking a follow-up about your previous response.
    Answer ONLY using the conversation history below — do not make up new information.
    
    {context}
    
    User follow-up: "{query}"
    
    Answer clearly and concisely:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content.strip()


def is_duplicate_ticket(new_query: str, open_tickets: list) -> tuple[bool, str]:
    """
    Checks if new query is asking for identical information
    as any existing open ticket.
    Uses loose approach — matches only on exact same intent.

    Returns:
        (True, ticket_id)  → duplicate found
        (False, "")        → not a duplicate
    """
    if not open_tickets:
        return False, ""

    # Format existing tickets for LLM
    tickets_text = ""
    for ticket in open_tickets:
        tickets_text += f"Ticket ID: {ticket['ticket_id']}\n"
        tickets_text += f"Query: {ticket['query']}\n\n"

    prompt = f"""You are checking if a new support query is asking 
    for the EXACT same specific information as an existing ticket.
    
    Existing open tickets:
    {tickets_text}
    
    New query: "{new_query}"
    
    Rules for DUPLICATE (reply with ticket ID):
    - Both queries are asking for identical specific information
    - Same exact question just worded slightly differently
    - A user reading both would think they are the same question
    
    Rules for NOT DUPLICATE (reply with NONE):
    - Queries are about same topic but different specific aspects
    - One is more specific than the other
    - They need different information to answer
    - When in doubt → NOT DUPLICATE
    
    Reply with ONLY the ticket ID if duplicate (e.g. TK-0001)
    Or reply with ONLY the word NONE if not duplicate:"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    result = response.choices[0].message.content.strip().upper()
    logger.info(f"Duplicate ticket check result: {result}")

    if result == "NONE":
        return False, ""
    else:
        return True, result