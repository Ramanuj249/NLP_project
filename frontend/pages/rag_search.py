import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG Search", page_icon="🔍", layout="wide")
st.title("🔍 RAG Document Search")
st.caption("AI powered search across your document library.")
st.divider()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "rag_documents" not in st.session_state:
    st.session_state.rag_documents = []

if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

if not st.session_state.rag_documents:
    try:
        res = requests.get(f"{BACKEND_URL}/rag/documents")
        if res.status_code == 200:
            st.session_state.rag_documents = res.json()
    except:
        pass

with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)

    try:
        res = requests.get(f"{BACKEND_URL}/rag/documents", timeout=5)
        if res.status_code == 200:
            st.session_state.rag_documents = res.json()
    except:
        pass

    total_docs = len(set([d["document_name"] for d in st.session_state.rag_documents]))

    with col1:
        st.metric("📄 Total Documents", total_docs)
    with col2:
        total_chunks = total_docs * 11
        st.metric("🧩 Est. Chunks", total_chunks)
    with col3:
        if total_docs > 0:
            st.metric("⚡ Status", "Ready ✅")
        else:
            st.metric("⚡ Status", "Not Ingested ❌")
    with col4:
        if st.button("🔁 Refresh Stats"):
            st.rerun()

st.divider()

with st.container(border=True):
    st.subheader("📥 Ingest Documents")
    st.caption("Only run this when new documents have been added to Notion.")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.warning("⚠️ Only ingest when new documents are added to Notion. This process may take time to complete")
    with col2:
        if st.button("🔄 Start Ingest", use_container_width=True, type="primary"):
            with st.status("Ingesting documents...", expanded=True) as status:
                st.write("📤 Connecting to Notion...")
                st.write("📄 Fetching all documents...")
                res = requests.post(
                    f"{BACKEND_URL}/rag/ingest",
                    timeout=900
                )
                if res.status_code == 200:
                    data = res.json()
                    st.write(f"✅ {data['documents']} documents loaded")
                    st.write(f"✅ {data['chunks']} chunks embedded")
                    st.write("✅ Stored in Milvus successfully")
                    status.update(label="✅ Ingestion complete!", state="complete")
                    st.toast(f"Ingested {data['documents']} documents!", icon="✅")
                    st.rerun()
                else:
                    st.error("Ingestion failed. Check backend logs.")
                    status.update(label="❌ Ingestion failed", state="error")


st.divider()

with st.container(border=True):
    st.subheader("❓ Ask Anything")
    st.caption("Ask any question about your documents. The AI will automatically search or compare.")

    query = st.text_input(
        "Your Question",
        placeholder="e.g. What is the remote work policy? or Compare Code of Conduct and Remote Work Policy",
        key="search_query"
    )

    if st.button("🔍 Ask", use_container_width=True, type="primary"):
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                payload = {
                    "query": query,
                    "filters": None
                }

                res = requests.post(
                    f"{BACKEND_URL}/rag/chat",
                    json=payload,
                    timeout=60
                )

                if res.status_code == 200:
                    result = res.json()
                    st.session_state.chat_history.append({
                        "question": query,
                        "result": result
                    })
                    st.rerun()
                else:
                    st.error("Search failed. Please try again.")

st.divider()

with st.container(border=True):
    st.subheader("🔀 Compare Two Documents")
    st.caption("Select two documents to compare side by side.")

    doc_names = [d["document_name"] for d in st.session_state.rag_documents]

    if not doc_names:
        st.warning("No documents found. Please ingest documents first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            doc1 = st.selectbox("📄 Document 1", options=doc_names, key="doc1")
        with col2:
            doc2 = st.selectbox("📄 Document 2", options=doc_names, key="doc2")

        if st.button("🔀 Compare", use_container_width=True, type="primary"):
            if doc1 == doc2:
                st.warning("Please select two different documents.")
            else:
                with st.spinner("Comparing documents..."):
                    payload = {
                        "query": f"Compare {doc1} and {doc2}",
                        "mode": "compare",
                        "doc_name_1": doc1,
                        "doc_name_2": doc2
                    }
                    res = requests.post(
                        f"{BACKEND_URL}/rag/chat",
                        json=payload,
                        timeout=60
                    )
                    if res.status_code == 200:
                        result = res.json()
                        st.session_state.chat_history.append({
                            "question": f"Compare {doc1} and {doc2}",
                            "result": result
                        })
                        st.rerun()
                    else:
                        st.error("Comparison failed. Please try again.")