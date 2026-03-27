import requests
import streamlit as st
from sidebar_style import apply_sidebar_style

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Ask Your Documents", page_icon="💬", layout="wide")
apply_sidebar_style()

# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "rag_documents" not in st.session_state:
    st.session_state.rag_documents = []

if "default_scores" not in st.session_state:
    st.session_state.default_scores = None

if "default_scores_loaded" not in st.session_state:
    st.session_state.default_scores_loaded = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = ""

if not st.session_state.rag_documents:
    try:
        res = requests.get(f"{BACKEND_URL}/rag/documents", timeout=5)
        if res.status_code == 200:
            st.session_state.rag_documents = res.json()
    except:
        pass

if not st.session_state.default_scores_loaded:
    try:
        res = requests.get(f"{BACKEND_URL}/rag/evaluate/default", timeout=900)
        if res.status_code == 200:
            data = res.json()
            st.session_state.default_scores = data["scores"]
        st.session_state.default_scores_loaded = True
    except:
        st.session_state.default_scores_loaded = True

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    st.title("💬 Ask Your Documents")
    st.caption("Ask anything about your documents — powered by RAG.")
with col2:
    st.write("")
    st.write("")
    if st.button("🔄 Retrain", use_container_width=True):
        with st.spinner("Retraining..."):
            res = requests.post(f"{BACKEND_URL}/rag/ingest", timeout=900)
            if res.status_code == 200:
                data = res.json()
                st.toast(f"Retrained on {data['documents']} documents!", icon="✅")
                st.rerun()
            else:
                st.error("Retraining failed.")

st.divider()

# ─────────────────────────────────────────────
# Main Layout — Chat (75%) | Evaluation (25%)
# ─────────────────────────────────────────────
chat_col, eval_col = st.columns([3, 1])

# ─────────────────────────────────────────────
# LEFT — CHAT SECTION
# ─────────────────────────────────────────────
with chat_col:
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])

        if chat["result"] is None:
            with st.chat_message("assistant"):
                st.markdown("⏳ Searching your documents...")
        else:
            with st.chat_message("assistant"):
                result = chat["result"]
                st.markdown(result.get("answer", ""))

                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"🛠️ Tool: {result.get('tool_used', '').upper()}")
                with col2:
                    st.caption(f"🔎 Refined: {result.get('refined_query', '')[:60]}")

                citations = result.get("citations", [])
                if citations:
                    with st.expander("📚 Citations"):
                        for cite in citations:
                            doc_name = cite.get("document_name", "")
                            doc_type = cite.get("document_type", "")
                            page_id = cite.get("page_id", "")
                            score = cite.get("score", "")

                            if page_id:
                                notion_url = f"https://notion.so/{page_id.replace('-', '')}"
                                st.markdown(f"📄 [{doc_name}]({notion_url}) — {doc_type}")
                            else:
                                st.markdown(f"📄 {doc_name} — {doc_type}")

                            if score:
                                st.progress(float(score), text=f"Relevance: {score}")

                if result.get("ticket_created"):
                    ticket_url = result.get("ticket_url", "")
                    st.warning(
                        f"🎫 Support ticket raised for this query. "
                        f"[View Ticket in Notion]({ticket_url})"
                    )

    st.divider()

    # ── Single chat input with unique key ──
    query = st.chat_input("Ask anything about your documents...", key="chat_input")

    if query:
        st.session_state.chat_history.append({"question": query, "result": None})
        st.rerun()

    if st.session_state.chat_history and st.session_state.chat_history[-1]["result"] is None:
        with st.spinner("Thinking..."):
            last = st.session_state.chat_history[-1]
            payload = {
                "query": last["question"],
                "filters": None,
                "messages": st.session_state.messages,
                "summary": st.session_state.summary
            }
            res = requests.post(f"{BACKEND_URL}/rag/chat", json=payload, timeout=60)
            if res.status_code == 200:
                result = res.json()
                st.session_state.chat_history[-1]["result"] = result
                st.session_state.messages = result.get("messages", [])
                st.session_state.summary = result.get("summary", "")
                st.rerun()
            else:
                st.session_state.chat_history[-1]["result"] = {
                    "answer": "Search failed. Please try again.",
                    "citations": [], "tool_used": "", "refined_query": "",
                    "messages": st.session_state.messages,
                    "summary": st.session_state.summary
                }
                st.rerun()

# ─────────────────────────────────────────────
# RIGHT — EVALUATION SCORES SIDEBAR PANEL
# ─────────────────────────────────────────────
with eval_col:
    st.subheader("📊 RAG Health")
    st.caption("Live evaluation scores")
    st.divider()

    if st.session_state.default_scores:
        scores = st.session_state.default_scores
        st.metric("Faithfulness", f"{scores['faithfulness']:.2f}")
        st.metric("Answer Relevancy", f"{scores['answer_relevancy']:.2f}")
        st.metric("Context Precision", f"{scores['context_precision']:.2f}")
        st.metric("Context Recall", f"{scores['context_recall']:.2f}")
        st.caption(f"Based on {scores.get('num_questions', 10)} questions")
    else:
        st.info("No evaluation scores yet.")

    st.divider()
    st.caption("Run a custom evaluation:")
    st.page_link(
        "pages/rag_evaluate.py",
        label="📊 Evaluate RAG Quality",
        use_container_width=True
    )