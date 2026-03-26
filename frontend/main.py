import streamlit as st
from sidebar_style import apply_sidebar_style

pg = st.navigation([
    st.Page("new_app.py",              title="Generate Document",      icon="📄"),
    st.Page("pages/rag_evaluate.py",   title="Evaluate RAG Quality",   icon="📊"),
    st.Page("pages/rag_search.py",     title="Ask Your Documents",     icon="💬"),
    st.Page("pages/view_documents.py", title="View Notion Documents",  icon="📁"),
])

apply_sidebar_style()
pg.run()