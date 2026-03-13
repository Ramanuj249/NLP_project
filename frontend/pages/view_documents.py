import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

st.title("📚 Notion Documents")
st.caption("Click on any document to view its content.")
st.divider()

# ─────────────────────────────────────────────
# Fetch all documents
# ─────────────────────────────────────────────
with st.spinner("Loading..."):
    res = requests.get(f"{BACKEND_URL}/notion-documents")
    try:
        documents = res.json()
    except Exception:
        st.error(f"Error loading documents: {res.text}")
        st.stop()

if not documents:
    st.info("No documents found in Notion yet.")
    st.stop()

st.caption(f"{len(documents)} documents found")

# ─────────────────────────────────────────────
# Column Headers
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    st.markdown("**Document Name**")
with col2:
    st.markdown("**Category**")
with col3:
    st.markdown("**Type**")
with col4:
    st.markdown("**Date**")

st.divider()

# ─────────────────────────────────────────────
# Document List with Expander
# ─────────────────────────────────────────────
for doc in documents:
    with st.expander(f"📄 {doc['name']}  |  {doc.get('type', '-')}  |  {doc.get('created_date', '-')}"):

        # Metadata row
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            st.caption(f"**Name:** {doc['name']}")
        with col2:
            st.caption(f"**Category:** {doc.get('category', '-')}")
        with col3:
            st.caption(f"**Type:** {doc.get('type', '-')}")
        with col4:
            st.caption(f"**Date:** {doc.get('created_date', '-')}")

        st.divider()

        # Load content button
        key = f"load_{doc['page_id']}"
        if key not in st.session_state:
            st.session_state[key] = None

        if st.session_state[key] is None:
            if st.button("Load Content", key=f"btn_{doc['page_id']}"):
                with st.spinner("Loading content..."):
                    content_res = requests.get(f"{BACKEND_URL}/notion-document/{doc['page_id']}")
                    st.session_state[key] = content_res.json().get("content", "")
                st.rerun()
        else:
            st.markdown(st.session_state[key])