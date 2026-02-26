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
    # st.write(st.session_state)
    if st.session_state.questions:
        st.subheader("Questions")
        # for q in st.session_state.questions:
        #     st.write(f"• {q['question']}")
        if st.session_state.questions:
            render_questions(st.session_state.questions)

            # if st.button("Submit Responses"):
            #     st.json(st.session_state.answers)


            if st.button("Preview JSON"):
                st.json(build_request_json())
            st.write(st.session_state)
            if st.button("Generate Document"):
                payload = build_request_json()

                res = requests.post(f"{BACKEND_URL}/generate-document", json=payload)
                # st.header("this is the prompt sent to the Model.")
                # st.text_area("hello", res.json()["response"], height=500)
                data = res.json()
                st.markdown(data["response"])