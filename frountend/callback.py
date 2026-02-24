import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"

def fetch_questions_for_document():
    selected_title = st.session_state.selected_doc_title

    # Placeholder selected → do nothing
    if selected_title == "-- Select a document --":
        st.session_state.questions = []
        st.session_state.last_doc_id = None
        return

    doc_map = st.session_state.get("doc_map", {})
    doc = doc_map.get(selected_title)

    if not doc:
        return

    doc_id = doc["id"]

    # Prevent duplicate API calls
    if st.session_state.last_doc_id == doc_id:
        return

    res = requests.get(
        f"{BACKEND_URL}/questions",
        params={"document_id": doc_id}
    )

    st.session_state.questions = res.json()
    st.session_state.last_doc_id = doc_id

# data = fetch_questions_for_document()
# print(data)

def normalize_options(raw_options):
    """
    Converts backend options to a proper list.
    Handles:
    - list
    - "{a, b, c}"
    - "a, b, c"
    """
    if not raw_options:
        return []

    # Already a list
    if isinstance(raw_options, list):
        return raw_options

    # String case
    if isinstance(raw_options, str):
        options = raw_options.strip()

        # Remove { }
        if options.startswith("[") and options.endswith("]"):
            options = options[1:-1]

        return [opt.strip() for opt in options.split(",") if opt.strip()]

    return []


def render_questions(questions):
    answers = []

    for q in questions:
        qid = q["id"]
        q_text = q["question"]
        q_type = q["type"]
        key = f"q_{qid}"

        # Question text (tight layout)
        st.write(f"**{q_text}**")

        # ---------- RADIO ----------
        if q_type == "radio":
            options = normalize_options(q.get("options"))
            value = st.radio(
                "",
                options,
                key=key,
                label_visibility="collapsed"
            )

        # ---------- TEXT ----------
        elif q_type == "text":
            value = st.text_input(
                "",
                key=key,
                label_visibility="collapsed"
            )

        # ---------- TEXT AREA ----------
        elif q_type == "text area":
            value = st.text_area(
                "",
                key=key,
                label_visibility="collapsed"
            )

        # ---------- MULTI SELECT ----------
        elif q_type == "multi select":
            options = normalize_options(q.get("options"))
            value = st.multiselect(
                "",
                options,
                key=key,
                label_visibility="collapsed"
            )

        # ---------- BOOLEAN RADIO ----------
        elif q_type == "bol_radio":
            choice = st.radio(
                "",
                ["Yes", "No"],
                key=key,
                horizontal=True,
                label_visibility="collapsed"
            )
            value = choice == "Yes"

        # ---------- CALENDAR ----------
        elif q_type == "calendar":
            value = st.date_input(
                "",
                key=key,
                label_visibility="collapsed"
            )
            value = value.isoformat() if value else None

        # ---------- TABLE ----------
        elif q_type == "table":
            columns = normalize_options(q.get("columns"))

            if key not in st.session_state:
                st.session_state[key] = [{col: "" for col in columns}]

            value = st.data_editor(
                st.session_state[key],
                key=f"{key}_editor",
                num_rows="dynamic",
                use_container_width=True
            )

            st.session_state[key] = value

        else:
            continue

        answers.append({
            "question_id": qid,
            "question": q_text,
            "answer": value
        })

        # Minimal spacing between questions
        st.markdown("<br>", unsafe_allow_html=True)

    # Persist answers for submit button
    st.session_state.answers = answers