import requests
from callback import fetch_questions_for_document, render_questions, build_request_json
# from callback import update_components

import streamlit as st

BACKEND_URL = "http://localhost:8000"

st.title("Documentation Generator")

# --- Initialize session state ---
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

# --- Section review state ---
if "sections" not in st.session_state:
    st.session_state.sections = []        # List of split chunks

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

# if "components" not in st.session_state:
#     st.session_state.components = []

# --- Maps for dropdowns ---
category_map = {c["category_name"]: c["id"] for c in st.session_state.categories}
doc_type_map = {d["document_type_name"]: {"id": d["id"], "components": d.get("components", [])} for d in st.session_state.doc_types}

def update_components():
    selected_type = st.session_state.selected_doc_type
    st.session_state.components = doc_type_map.get(selected_type, {}).get("components", []) #[selected_type]["components"]

# --- Initialize selected values if not present ---
if "selected_category" not in st.session_state:
    st.session_state.selected_category = list(category_map.keys())[0]

if "selected_doc_type" not in st.session_state:
    st.session_state.selected_doc_type = list(doc_type_map.keys())[0]

if "components" not in st.session_state or not st.session_state.components:
    update_components()

def split_by_divider(text: str) -> list[str]:
    """
    Split the document by '---' horizontal rules.
    Each chunk is stripped of extra whitespace and empty chunks are removed.
    """
    raw_chunks = text.split("\n---\n")
    cleaned = [chunk.strip() for chunk in raw_chunks]
    return [c for c in cleaned if c]  # remove empty


def reset_review():
    st.session_state.sections = []
    st.session_state.instructions = []
    st.session_state.current_section_index = 0
    st.session_state.review_mode = False
    st.session_state.final_doc_ready = False
    st.session_state.document_saved = False

# --- Dropdowns for categories ---
selected_category = st.selectbox(
    "Select Category",
    list(category_map.keys()),
    index=list(category_map.keys()).index(st.session_state.selected_category),
    key="selected_category"
)

# --- Dropdowns for document type ---
selected_doc_type = st.selectbox(
    "Select Document Type",
    list(doc_type_map.keys()),
    index=list(doc_type_map.keys()).index(st.session_state.selected_doc_type),
    key="selected_doc_type",
    on_change= update_components
)

# --- Fetch documents only when button clicked ---
if st.button("Get Documents"):
    params = {
        "category_id": category_map[selected_category],
        "document_type_id": doc_type_map[selected_doc_type]["id"]
    }
    res = requests.get(f"{BACKEND_URL}/documents", params=params)
    st.session_state.documents = res.json()
    reset_review()

# --- Show documents if available ---
documents = st.session_state.documents

if documents:
    doc_map = {doc["title"]: doc for doc in documents}
    st.session_state.doc_map = doc_map

    placeholder = "-- Select a document --"
    doc_titles = [placeholder] + list(doc_map.keys())
    # doc_titles = list(doc_map.keys())

    # Initialize selected document
    if "selected_doc_title" not in st.session_state:
        st.session_state.selected_doc_title = placeholder

    selected_doc_title = st.selectbox(
        "Select a Document",
        doc_titles,
        index=doc_titles.index(st.session_state.selected_doc_title),
        key="selected_doc_title",
        on_change=fetch_questions_for_document
    )

    # ## Questions and answers showing code
    # # st.write(st.session_state)
    # if st.session_state.questions:
    #     st.subheader("Questions")
    #     # for q in st.session_state.questions:
    #     #     st.write(f"• {q['question']}")
    #     if st.session_state.questions:
    #         render_questions(st.session_state.questions)
    #
    #         # if st.button("Submit Responses"):
    #         #     st.json(st.session_state.answers)
    #
    #
    #         if st.button("Preview JSON"):
    #             st.json(build_request_json())
    #         # st.write(st.session_state)
    #         if st.button("Generate Document"):
    #             payload = build_request_json()
    #
    #             res = requests.post(f"{BACKEND_URL}/generate-document", json=payload)
    #             st.header("this is the prompt sent to the Model.")
    #             st.text_area("hello", res.json()["response"], height=500)
    #             # data = res.json()
    #             # st.markdown(data["response"])

    if st.session_state.questions:
        st.subheader("Questions")
        render_questions(st.session_state.questions)

        if st.button("Generate Document"):
            payload = build_request_json()
            res = requests.post(f"{BACKEND_URL}/generate-document", json=payload)
            data = res.json()
            raw_text = data["response"]

            # Split and enter review mode
            reset_review()
            st.session_state.sections = split_by_divider(raw_text)
            st.session_state.instructions = [""] * len(st.session_state.sections)
            st.session_state.review_mode = True
            st.rerun()

# ─────────────────────────────────────────────
# Section Navigation (Review Mode)
# ─────────────────────────────────────────────
if st.session_state.review_mode and st.session_state.sections and not st.session_state.final_doc_ready:
    sections = st.session_state.sections
    idx = st.session_state.current_section_index
    total = len(sections)

    st.divider()
    st.subheader(f"Section {idx + 1} of {total}")
    st.progress((idx + 1) / total)

    # Render current section as markdown
    st.markdown(sections[idx])

    st.divider()

    # --- Instruction box ---
    instruction = st.text_area(
        label="📝 Instructions for this section",
        value=st.session_state.instructions[idx],
        placeholder="Describe the changes you want in this section... e.g. 'Make this more formal' or 'Add a point about data privacy'",
        height=120,
        key=f"instruction_{idx}"
    )
    # Save instruction into session state as user types
    st.session_state.instructions[idx] = instruction

    if st.button("Rewrite with AI"):
        if instruction.strip() == "":
            st.warning("Please write an instruction before requesting a rewrite.")
        else:
            with st.spinner("Rewriting section..."):
                payload = {
                    "section_text": sections[idx],
                    "instruction": instruction
                }
                res = requests.post(f"{BACKEND_URL}/refine-section", json=payload)
                refined = res.json().get("refined_section", "")
                if refined:
                    st.session_state.sections[idx] = refined
                    st.session_state.instructions[idx] = ""  # clear instruction after rewrite
                    st.rerun()

    st.divider()

    # --- Navigation buttons ---
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if idx > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_section_index -= 1
                st.rerun()

    with col3:
        if idx < total - 1:
            if st.button("Finalize & Next ➡️"):
                st.session_state.current_section_index += 1
                st.rerun()
        else:
            if st.button("✅ Finalize Document"):
                st.session_state.final_doc_ready = True
                st.session_state.review_mode = False
                st.rerun()

# ─────────────────────────────────────────────
# Final Document
# ─────────────────────────────────────────────
if st.session_state.final_doc_ready:
    st.divider()
    st.subheader("📄 Final Document")
    st.success("Your document is ready!")

    final_doc = "\n\n---\n\n".join(st.session_state.sections)
    st.markdown(final_doc)

    st.divider()

    # --- Save & Download row ---
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💾 Save Document", use_container_width=True):
            if not st.session_state.document_saved:
                with st.spinner("Saving document..."):
                    payload = {
                        "document_id": st.session_state.last_doc_id,
                        "document_name": st.session_state.selected_doc_title,
                        "category": st.session_state.selected_category,
                        "document_type": st.session_state.selected_doc_type.upper(),
                        "document_content": final_doc,
                        "version": "1.0",
                        "author": "Unknown"
                    }
                    res = requests.post(f"{BACKEND_URL}/save-document", json=payload)
                    data = res.json()
                    if res.status_code == 200:
                        st.session_state.document_saved = True
                        st.success(f"Document saved! ID: {data['generated_document_id']}")
                    else:
                        st.error("Something went wrong while saving. Please try again.")
            else:
                st.info("Document already saved.")

    with col2:
        st.download_button(
            label="⬇️ Download as .txt",
            data=final_doc,
            file_name="final_document.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col3:
        if st.button("🔄 Start Over", use_container_width=True):
            reset_review()
            st.session_state.questions = []
            st.rerun()

    # st.download_button(
    #     label="⬇️ Download as .txt",
    #     data=final_doc,
    #     file_name="final_document.txt",
    #     mime="text/plain"
    # )
    #
    # if st.button("🔄 Start Over"):
    #     reset_review()
    #     st.session_state.questions = []
    #     st.rerun()