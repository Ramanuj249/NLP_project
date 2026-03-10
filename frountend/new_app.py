import requests
from datetime import date
from callback import fetch_questions_for_document, render_questions, build_request_json
import streamlit as st

BACKEND_URL = "http://localhost:8000"

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Documentation Generator",
    page_icon="📄",
    layout="wide"
)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("📄 Documentation Generator")
st.caption("Generate professional, publication-ready documents powered by AI.")

# ─────────────────────────────────────────────
# Initialize Session State
# ─────────────────────────────────────────────
if "documents" not in st.session_state:
    st.session_state.documents = []

if "categories" not in st.session_state:
    st.session_state.categories = requests.get(f"{BACKEND_URL}/categories").json()

if "doc_types" not in st.session_state:
    st.session_state.doc_types = requests.get(f"{BACKEND_URL}/document-types").json()

if "questions" not in st.session_state:
    st.session_state.questions = []

if "last_doc_id" not in st.session_state:
    st.session_state.last_doc_id = None

if "sections" not in st.session_state:
    st.session_state.sections = []

if "instructions" not in st.session_state:
    st.session_state.instructions = []

if "current_section_index" not in st.session_state:
    st.session_state.current_section_index = 0

if "review_mode" not in st.session_state:
    st.session_state.review_mode = False

if "final_doc_ready" not in st.session_state:
    st.session_state.final_doc_ready = False

if "document_saved" not in st.session_state:
    st.session_state.document_saved = False

if "notion_pushed" not in st.session_state:
    st.session_state.notion_pushed = False

if "doc_version" not in st.session_state:
    st.session_state.doc_version = None

if "author_name" not in st.session_state:
    st.session_state.author_name = None

# ─────────────────────────────────────────────
# Maps
# ─────────────────────────────────────────────
category_map = {c["category_name"]: c["id"] for c in st.session_state.categories}
doc_type_map = {
    d["document_type_name"]: {"id": d["id"], "components": d.get("components", [])}
    for d in st.session_state.doc_types
}

def update_components():
    selected_type = st.session_state.selected_doc_type
    st.session_state.components = doc_type_map.get(selected_type, {}).get("components", [])

if "selected_category" not in st.session_state:
    st.session_state.selected_category = list(category_map.keys())[0]

if "selected_doc_type" not in st.session_state:
    st.session_state.selected_doc_type = list(doc_type_map.keys())[0]

if "components" not in st.session_state or not st.session_state.components:
    update_components()

def split_by_divider(text: str) -> list[str]:
    raw_chunks = text.split("\n---\n")
    cleaned = [chunk.strip() for chunk in raw_chunks]
    return [c for c in cleaned if c]

def reset_review():
    st.session_state.sections = []
    st.session_state.instructions = []
    st.session_state.current_section_index = 0
    st.session_state.review_mode = False
    st.session_state.final_doc_ready = False
    st.session_state.document_saved = False
    st.session_state.notion_pushed = False
    st.session_state.doc_version = None
    st.session_state.author_name = None


# ─────────────────────────────────────────────
# Step 1 — Select Document
# ─────────────────────────────────────────────
with st.container(border=True):
    st.subheader("🗂️ Step 1 — Select Document")
    st.caption("Choose the category and type of document you want to generate.")

    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox(
            "📁 Document Category",
            list(category_map.keys()),
            index=list(category_map.keys()).index(st.session_state.selected_category),
            key="selected_category",
            help="Select the department or domain this document belongs to."
        )
    with col2:
        selected_doc_type = st.selectbox(
            "📋 Document Type",
            list(doc_type_map.keys()),
            index=list(doc_type_map.keys()).index(st.session_state.selected_doc_type),
            key="selected_doc_type",
            on_change=update_components,
            help="Select the type of document — Policy, Procedure, Guide etc."
        )

    if st.button("🔍 Get Documents", use_container_width=True, type="primary"):
        with st.spinner("Fetching documents..."):
            params = {
                "category_id": category_map[selected_category],
                "document_type_id": doc_type_map[selected_doc_type]["id"]
            }
            res = requests.get(f"{BACKEND_URL}/documents", params=params)
            st.session_state.documents = res.json()
            reset_review()
        if st.session_state.documents:
            st.toast(f"✅ {len(st.session_state.documents)} documents found!", icon="✅")
        else:
            st.toast("No documents found for this selection.", icon="⚠️")

# ─────────────────────────────────────────────
# Step 2 — Select & Answer Questions
# ─────────────────────────────────────────────
documents = st.session_state.documents

if documents:
    doc_map = {doc["title"]: doc for doc in documents}
    st.session_state.doc_map = doc_map

    placeholder = "-- Select a document --"
    doc_titles = [placeholder] + list(doc_map.keys())

    if "selected_doc_title" not in st.session_state:
        st.session_state.selected_doc_title = placeholder

    st.divider()
    with st.container(border=True):
        st.subheader("📝 Step 2 — Answer Questions")
        st.caption("Select a document template and answer the guided questions.")

        selected_doc_title = st.selectbox(
            "📄 Select a Document Template",
            doc_titles,
            index=doc_titles.index(st.session_state.selected_doc_title),
            key="selected_doc_title",
            on_change=fetch_questions_for_document
        )

        if st.session_state.questions:
            total_questions = len(st.session_state.questions)
            st.metric(label="Total Questions", value=total_questions)
            st.divider()
            render_questions(st.session_state.questions)
            st.divider()

            if st.button("🚀 Generate Document", use_container_width=True, type="primary"):
                with st.status("Generating your document...", expanded=True) as status:
                    st.write("📤 Sending your answers to the AI...")
                    payload = build_request_json()
                    res = requests.post(f"{BACKEND_URL}/generate-document", json=payload)
                    st.write("✍️ AI is writing your document...")
                    data = res.json()
                    raw_text = data["response"]
                    st.write("✂️ Splitting into sections...")
                    reset_review()
                    st.session_state.sections = split_by_divider(raw_text)
                    st.session_state.instructions = [""] * len(st.session_state.sections)
                    st.session_state.review_mode = True
                    status.update(label="✅ Document generated successfully!", state="complete")
                st.rerun()


# ─────────────────────────────────────────────
# Step 3 — Section Review
# ─────────────────────────────────────────────
if st.session_state.review_mode and st.session_state.sections and not st.session_state.final_doc_ready:
    sections = st.session_state.sections
    idx = st.session_state.current_section_index
    total = len(sections)

    st.divider()
    with st.container(border=True):
        st.subheader("✏️ Step 3 — Review & Edit Sections")
        st.caption("Review each section, request AI rewrites, and finalize before saving.")

        # Progress
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Section", f"{idx + 1} of {total}")
        with col2:
            st.metric("Sections Remaining", total - idx - 1)
        with col3:
            st.metric("Progress", f"{int(((idx + 1) / total) * 100)}%")

        st.progress((idx + 1) / total)
        st.divider()

        # Current section content
        with st.container(border=True):
            st.markdown(sections[idx])

        st.divider()

        # Instruction box
        instruction = st.text_area(
            label="✏️ Describe the changes you want for this section",
            value=st.session_state.instructions[idx],
            placeholder="e.g. 'Make this more formal' or 'Add a point about data privacy'",
            height=100,
            key=f"instruction_{idx}"
        )
        st.session_state.instructions[idx] = instruction

        # Rewrite button
        if st.button("✨ Rewrite with AI", use_container_width=True):
            if instruction.strip() == "":
                st.warning("Please write an instruction before requesting a rewrite.")
            else:
                with st.status("Rewriting section with AI...", expanded=True) as status:
                    st.write("🤖 AI is rewriting your section...")
                    payload = {
                        "section_text": sections[idx],
                        "instruction": instruction
                    }
                    res = requests.post(f"{BACKEND_URL}/refine-section", json=payload)
                    refined = res.json().get("refined_section", "")
                    if refined:
                        st.session_state.sections[idx] = refined
                        st.session_state.instructions[idx] = ""
                        status.update(label="✅ Section rewritten successfully!", state="complete")
                st.rerun()

        st.divider()

        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if idx > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.current_section_index -= 1
                    st.rerun()
        with col3:
            if idx < total - 1:
                if st.button("Finalize & Next ➡️", use_container_width=True, type="primary"):
                    st.session_state.current_section_index += 1
                    st.rerun()
            else:
                if st.button("✅ Finalize Document", use_container_width=True, type="primary"):
                    st.session_state.final_doc_ready = True
                    st.session_state.review_mode = False
                    st.rerun()


# ─────────────────────────────────────────────
# Step 4 — Final Document
# ─────────────────────────────────────────────
if st.session_state.final_doc_ready:
    st.divider()

    with st.container(border=True):
        st.subheader("🎉 Step 4 — Your Document is Ready!")

        # Document info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Document", st.session_state.selected_doc_title[:30])
        with col2:
            st.metric("🗂️ Category", st.session_state.selected_category[:20])
        with col3:
            st.metric("📋 Type", st.session_state.selected_doc_type)

        st.divider()

        final_doc = "\n\n---\n\n".join(st.session_state.sections)

        # Document preview
        with st.expander("👁️ Preview Full Document", expanded=False):
            st.markdown(final_doc)

        st.divider()

        # Save section
        if not st.session_state.document_saved:
            with st.container(border=True):
                st.subheader("💾 Save Document")
                author_input = st.text_input(
                    "👤 Enter your name",
                    placeholder="Your name...",
                    key="author_input"
                )
                if st.button("💾 Save to Database", use_container_width=True, type="primary"):
                    if not author_input.strip():
                        st.warning("Please enter your name before saving.")
                    else:
                        with st.status("Saving document...", expanded=True) as status:
                            st.write("📤 Sending to database...")
                            payload = {
                                "document_id": st.session_state.last_doc_id,
                                "document_name": st.session_state.selected_doc_title,
                                "category": st.session_state.selected_category,
                                "document_type": st.session_state.selected_doc_type.upper(),
                                "document_content": final_doc,
                                "author": author_input.strip()
                            }
                            res = requests.post(f"{BACKEND_URL}/save-document", json=payload)
                            data = res.json()
                            if res.status_code == 200:
                                st.session_state.document_saved = True
                                st.session_state.author_name = author_input.strip()
                                st.session_state.doc_version = data["version"]
                                status.update(label="✅ Document saved successfully!", state="complete")
                                st.toast(f"Document saved! Version: {data['version']}", icon="✅")
                            else:
                                st.error("Something went wrong. Please try again.")
        else:
            with st.container(border=True):
                st.success("✅ Document Saved Successfully!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📌 Version", st.session_state.doc_version)
                with col2:
                    st.metric("👤 Author", st.session_state.author_name)
                with col3:
                    st.metric("📅 Date", date.today().isoformat())

        st.divider()

        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.download_button(
                label="⬇️ Download as .txt",
                data=final_doc,
                file_name="final_document.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            if not st.session_state.notion_pushed:
                if st.button("📤 Push to Notion", use_container_width=True):
                    if not st.session_state.document_saved:
                        st.warning("Please save the document first before pushing to Notion.")
                    else:
                        with st.status("Pushing to Notion...", expanded=True) as status:
                            st.write("📤 Connecting to Notion...")
                            payload = {
                                "document_id": st.session_state.last_doc_id,
                                "document_name": st.session_state.selected_doc_title,
                                "category": st.session_state.selected_category,
                                "document_type": st.session_state.selected_doc_type.upper(),
                                "version": st.session_state.doc_version,
                                "author": st.session_state.author_name or "Unknown",
                                "industry": "UCaaS",
                                "content": final_doc,
                                "created_date": date.today().isoformat()
                            }
                            res = requests.post(f"{BACKEND_URL}/push-to-notion", json=payload)
                            try:
                                data = res.json()
                                if res.status_code == 200:
                                    st.session_state.notion_pushed = True
                                    status.update(label="✅ Pushed to Notion!", state="complete")
                                    st.toast("Document pushed to Notion!", icon="✅")
                                    st.link_button("🔗 Open in Notion", data["url"])
                                else:
                                    st.error(f"Error: {data}")
                            except Exception as e:
                                st.error(f"Error: {res.text}")
            else:
                st.success("✅ Pushed to Notion!")

        with col3:
            if st.button("🔄 Start Over", use_container_width=True):
                reset_review()
                st.session_state.questions = []
                st.rerun()