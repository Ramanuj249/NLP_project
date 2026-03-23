import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict
from langgraph.graph import StateGraph, END
from .tools import (
    refine_query,
    is_compare_query,
    extract_document_names,
    search_tool,
    compare_tool
)
from rag.logger import logger
from .tools import handle_general_query, refine_query, is_compare_query, extract_document_names, search_tool, compare_tool

class AgentState(TypedDict):
    user_query: str
    refined_query: str
    is_compare: bool
    doc_names: list
    filters: dict
    answer: str
    citations: list
    tool_used: str

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
        doc_names = extract_document_names(refined_query)
        state["doc_names"] = doc_names
        logger.info(f"Router decided: Compare — documents: {doc_names}")
    else:
        logger.info("Router decided: Search")

    return state

def route_decision(state: AgentState) -> str:
    if state["is_compare"]:
        return "compare"
    return "search"

def search_node(state: AgentState) -> AgentState:
    logger.info("Running search node...")
    refined_query = state["refined_query"]
    filters = state.get("filters", None)

    result = search_tool(
        query=refined_query,
        filters=filters
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


def general_node(state: AgentState) -> AgentState:
    logger.info("Running general node...")
    is_general, response = handle_general_query(state["user_query"])

    if is_general:
        state["answer"] = response
        state["citations"] = []
        state["tool_used"] = "general"
        state["refined_query"] = state["user_query"]

    return state

def check_general(state: AgentState) -> str:
    is_general, response = handle_general_query(state["user_query"])
    if is_general:
        state["answer"] = response
        state["citations"] = []
        state["tool_used"] = "general"
        state["refined_query"] = state["user_query"]
        return "general"
    return "refine"

def build_agent():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("general", general_node)
    graph.add_node("refine", refine_node)
    graph.add_node("router", router_node)
    graph.add_node("search", search_node)
    graph.add_node("compare", compare_node)

    # Set entry point
    graph.set_entry_point("check_general")
    graph.add_node("check_general", lambda state: state)

    # Add edges
    graph.add_conditional_edges(
        "check_general",
        check_general,
        {
            "general": "general",
            "refine": "refine"
        }
    )
    graph.add_edge("general", END)
    graph.add_edge("refine", "router")
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "search": "search",
            "compare": "compare"
        }
    )
    graph.add_edge("search", END)
    graph.add_edge("compare", END)

    return graph.compile()

def run_agent(user_query: str, filters: dict = None) -> dict:
    logger.info(f"Agent started for query: {user_query}")

    agent = build_agent()

    initial_state = AgentState(
        user_query=user_query,
        refined_query="",
        is_compare=False,
        doc_names=[],
        filters=filters or {},
        answer="",
        citations=[],
        tool_used=""
    )

    final_state = agent.invoke(initial_state)

    logger.info(f"Agent complete — tool used: {final_state['tool_used']}")

    return {
        "answer": final_state["answer"],
        "citations": final_state["citations"],
        "tool_used": final_state["tool_used"],
        "refined_query": final_state["refined_query"]
    }

if __name__ == "__main__":
    # Test search
    print("Testing search...")
    result = run_agent("What is the remote work policy?")
    print(f"Tool used: {result['tool_used']}")
    print(f"Refined query: {result['refined_query']}")
    print(f"Answer: {result['answer'][:200]}")
    print(f"Citations: {result['citations']}")