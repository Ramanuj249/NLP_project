import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict
from langgraph.graph import StateGraph, END
from rag.logger import logger
from .tools import handle_general_query, refine_query, is_compare_query, extract_document_names, search_tool, compare_tool, check_answer_quality, summarize_messages, classify_query, is_followup_query, answer_from_memory
from notion_service import create_ticket

class AgentState(TypedDict):
    user_query: str
    refined_query: str
    is_compare: bool
    is_followup: bool
    doc_names: list
    filters: dict
    answer: str
    citations: list
    tool_used: str
    answer_found: bool
    ticket_created: bool
    ticket_id: str
    ticket_url: str
    messages: list
    summary: str
    query_type: str


def memory_update_node(state: AgentState) -> AgentState:
    """
    Runs at start of every query.
    If messages >= 6 → summarize oldest 4 → keep latest 2.
    This keeps conversation memory clean and efficient.
    """
    logger.info("Running memory update node...")
    messages = state.get("messages", [])

    if len(messages) >= 6:
        logger.info(f"Messages threshold reached ({len(messages)}) — summarizing...")
        existing_summary = state.get("summary", "")

        # Summarize oldest 4 messages
        new_summary = summarize_messages(messages[:4], existing_summary)

        # Keep only latest 2 messages
        state["summary"] = new_summary
        state["messages"] = messages[4:]
        logger.info("Memory updated — oldest 4 messages summarized")
    else:
        logger.info(f"Memory OK — {len(messages)} messages in history")

    return state

def classify_and_followup_node(state: AgentState) -> AgentState:
    logger.info("Running classify and followup node...")

    # Step 1 — check if follow-up
    is_followup = is_followup_query(
        state["user_query"],
        state.get("messages", [])
    )
    state["is_followup"] = is_followup

    # Step 2 — only classify if NOT a follow-up
    if not is_followup:
        query_type = classify_query(state["user_query"])
        state["query_type"] = query_type
        logger.info(f"Query classified as: {query_type}")
    else:
        logger.info("Follow-up query detected — skipping classification")

    return state

def route_after_classify_and_followup(state: AgentState) -> str:
    """
    Routes based on followup check and classification.
    Handles all 4 possible routes in one function.
    """
    if state.get("is_followup", False):
        return "memory"

    query_type = state.get("query_type", "COMPANY_QUERY")
    if query_type == "GENERAL_CHAT":
        return "general"
    elif query_type == "GENERAL_KNOWLEDGE":
        return "decline"
    else:
        return "refine"

def decline_node(state: AgentState) -> AgentState:
    logger.info("Running decline node...")

    # LLM generates dynamic polite decline
    # based on what user actually asked
    from .tools import client, DEPLOYMENT_NAME

    prompt = f"""You are a company document assistant.

    The user asked: "{state['user_query']}"
    
    This question is about general knowledge and is outside 
    your scope as a company document assistant.
    
    Politely decline to answer and:
    - Acknowledge what they asked
    - Explain you can only help with company documents
    - Suggest they use a search engine for this type of question
    - Invite them to ask about company documents instead
    
    Keep response friendly and concise — 3 sentences maximum."""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    state["answer"] = response.choices[0].message.content.strip()
    state["citations"] = []
    state["tool_used"] = "decline"
    state["refined_query"] = state["user_query"]
    state["answer_found"] = True
    state["ticket_created"] = False
    return state

def answer_from_memory_node(state: AgentState) -> AgentState:
    """
    Answers the follow-up using only conversation history.
    No document search, no ticket.
    """
    logger.info("Running answer_from_memory node...")
    answer = answer_from_memory(
        query=state["user_query"],
        messages=state.get("messages", []),
        summary=state.get("summary", "")
    )
    state["answer"] = answer
    state["citations"] = []
    state["tool_used"] = "memory"
    state["answer_found"] = True
    state["ticket_created"] = False
    state["refined_query"] = state["user_query"]
    return state

def refine_node(state: AgentState) -> AgentState:
    logger.info("Running refine node...")
    user_query = state["user_query"]
    refined = refine_query(user_query)
    state["refined_query"] = refined
    return state

def router_node(state: AgentState) -> AgentState:
    logger.info("Running router node...")
    refined_query = state["refined_query"]
    compare = is_compare_query(refined_query)
    state["is_compare"] = compare

    if compare:
        doc_names = extract_document_names(refined_query, messages=state.get("messages", []))
        state["doc_names"] = doc_names
        logger.info(f"Router decided: Compare — documents: {doc_names}")
    else:
        logger.info("Router decided: Search")

    return state

def search_node(state: AgentState) -> AgentState:
    logger.info("Running search node...")
    refined_query = state["refined_query"]
    filters = state.get("filters", None)

    result = search_tool(
        query=refined_query,
        filters=filters,
        messages=state.get("messages", []),
        summary=state.get("summary", "")
    )

    state["answer"] = result["answer"]
    state["citations"] = result["citations"]
    state["tool_used"] = "search"
    logger.info("Search node complete")
    return state

def compare_node(state: AgentState) -> AgentState:
    logger.info("Running compare node...")
    doc_names = state.get("doc_names", [])

    if len(doc_names) < 2:
        logger.warning("Less than 2 document names found for comparison")
        state["answer"] = "Please specify two document names to compare. For example: 'Compare Remote Work Policy and Leave Policy'"
        state["citations"] = []
        state["tool_used"] = "compare"
        return state

    result = compare_tool(
        doc_name_1=doc_names[0],
        doc_name_2=doc_names[1]
    )

    state["answer"] = result["answer"]
    state["citations"] = result["citations"]
    state["tool_used"] = "compare"
    logger.info("Compare node complete")
    return state

def check_answer_node(state: AgentState) -> AgentState:
    """
    Runs after search or compare.
    LLM decides if answer properly addresses the question.
    Sets answer_found = True or False.
    """
    logger.info("Running check answer node...")

    is_good = check_answer_quality(
        question=state["user_query"],
        answer=state["answer"]
    )

    state["answer_found"] = is_good
    logger.info(f"Answer quality: {'GOOD' if is_good else 'BAD — ticket will be created'}")
    return state

def create_ticket_node(state: AgentState) -> AgentState:
    """
    Runs when answer_found = False.
    Creates support ticket in Notion.
    Updates answer to inform user about ticket.
    """
    logger.info("Running create ticket node...")

    try:
        result = create_ticket(
            user_query=state["user_query"],
            refined_query=state["refined_query"],
            messages=state.get("messages", []),
            summary=state.get("summary", "")
        )

        state["ticket_created"] = True
        state["ticket_id"] = result["ticket_id"]
        state["ticket_url"] = result["ticket_url"]
        state["answer"] = (
            "I could not find relevant information "
            "for your query in the documents.\n\n"
            "🎫 A support ticket has been raised for your query. "
            "Our team will get back to you shortly."
        )

        logger.info(f"Ticket created — id: {result['ticket_id']}")
    except Exception as e:
        logger.error(f"Ticket creation failed: {e}")
        state["ticket_created"] = False
        state["ticket_id"] = ""
        state["ticket_url"] = ""

    return state

def general_node(state: AgentState) -> AgentState:
    logger.info("Running general node...")

    # No classification needed — already done
    # Just generate response directly
    response = handle_general_query(
        state["user_query"],
        messages=state.get("messages", []),
        summary=state.get("summary", "")
    )

    state["answer"] = response
    state["citations"] = []
    state["tool_used"] = "general"
    state["refined_query"] = state["user_query"]
    return state

def build_agent():
    graph = StateGraph(AgentState)

    # ── Add all nodes ──
    graph.add_node("memory_update", memory_update_node)
    graph.add_node("classify_and_followup", classify_and_followup_node)
    graph.add_node("answer_from_memory", answer_from_memory_node)
    graph.add_node("decline", decline_node)
    graph.add_node("general", general_node)
    graph.add_node("refine", refine_node)
    graph.add_node("router", router_node)
    graph.add_node("search", search_node)
    graph.add_node("compare", compare_node)
    graph.add_node("check_answer", check_answer_node)
    graph.add_node("create_ticket", create_ticket_node)

    # ── Entry point ──
    graph.set_entry_point("memory_update")

    # ── memory_update → check_followup first, before anything else ──
    graph.add_edge("memory_update", "classify_and_followup")

    # ── check_followup branches: answer from memory OR continue to classify ──
    graph.add_conditional_edges(
        "classify_and_followup",
        route_after_classify_and_followup,
        {
            "memory": "answer_from_memory",
            "general": "general",
            "decline": "decline",
            "refine": "refine"
        }
    )

    graph.add_edge("answer_from_memory", END)

    graph.add_edge("general", END)
    graph.add_edge("decline", END)
    graph.add_edge("refine", "router")

    graph.add_conditional_edges(
        "router",
        lambda state: "compare" if state["is_compare"] else "search",
        {
            "search": "search",
            "compare": "compare"
        }
    )

    graph.add_edge("search", "check_answer")
    graph.add_edge("compare", "check_answer")

    graph.add_conditional_edges(
        "check_answer",
        lambda state: "end" if state["answer_found"] else "ticket",
        {
            "end": END,
            "ticket": "create_ticket"
        }
    )

    graph.add_edge("create_ticket", END)

    return graph.compile()

def run_agent(user_query: str, filters: dict = None,
              messages: list = None, summary: str = "") -> dict:
    logger.info(f"Agent started for query: {user_query}")

    agent = build_agent()

    initial_state = AgentState(
        user_query=user_query,
        refined_query="",
        is_compare=False,
        is_followup=False,
        doc_names=[],
        filters=filters or {},
        answer="",
        citations=[],
        tool_used="",
        answer_found=False,
        ticket_created=False,
        ticket_id="",
        ticket_url="",
        messages=messages or [],
        summary=summary
    )

    final_state = agent.invoke(initial_state)

    # ── Log graph path ──
    logger.info(
        f"[GRAPH] query='{user_query[:50]}' | "
        f"tool={final_state['tool_used']} | "
        f"answer_found={final_state['answer_found']} | "
        f"ticket_created={final_state['ticket_created']}"
    )

    # ── Append this Q&A to messages ──
    updated_messages = final_state.get("messages", [])
    updated_messages.append({
        "role": "user",
        "content": user_query
    })
    updated_messages.append({
        "role": "assistant",
        "content": final_state["answer"]
    })

    # ── Log memory state after every query ──
    logger.info("=" * 60)
    logger.info(f"[MEMORY] Total messages in history: {len(updated_messages)}")
    for i, msg in enumerate(updated_messages):
        role = msg.get("role", "").upper()
        content = msg.get("content", "")[:80]  # first 80 chars only
        logger.info(f"[MEMORY] msg[{i}] {role}: {content}")

    current_summary = final_state.get("summary", "")
    if current_summary:
        logger.info(f"[MEMORY] Summary: {current_summary[:200]}")
    else:
        logger.info("[MEMORY] Summary: (empty — not yet summarized)")
    logger.info("=" * 60)

    return {
        "answer": final_state["answer"],
        "citations": final_state["citations"],
        "tool_used": final_state["tool_used"],
        "refined_query": final_state["refined_query"],
        "answer_found": final_state["answer_found"],
        "ticket_created": final_state["ticket_created"],
        "ticket_id": final_state["ticket_id"],
        "ticket_url": final_state["ticket_url"],
        "messages": updated_messages,
        "summary": final_state.get("summary", "")
    }

if __name__ == "__main__":
    # Test search
    print("Testing search...")
    result = run_agent("What is the remote work policy?")
    print(f"Tool used: {result['tool_used']}")
    print(f"Refined query: {result['refined_query']}")
    print(f"Answer: {result['answer'][:200]}")
    print(f"Citations: {result['citations']}")