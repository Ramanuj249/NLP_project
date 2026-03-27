import requests
import streamlit as st
from sidebar_style import apply_sidebar_style

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Evaluate RAG Quality", page_icon="📊", layout="wide")
apply_sidebar_style()

# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────
if "eval_questions" not in st.session_state:
    st.session_state.eval_questions = []

if "eval_scores" not in st.session_state:
    st.session_state.eval_scores = None

if "eval_running" not in st.session_state:
    st.session_state.eval_running = False

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("📊 Evaluate RAG Quality")
st.caption("Add 5 to 10 questions with ground truth answers to evaluate your RAG pipeline using RAGAS.")
st.divider()

# ─────────────────────────────────────────────
# Main Layout — Form (60%) | Scores (40%)
# ─────────────────────────────────────────────
form_col, score_col = st.columns([3, 2])

# ─────────────────────────────────────────────
# LEFT — ADD QUESTIONS FORM
# ─────────────────────────────────────────────
with form_col:
    st.markdown("### ➕ Add Questions")
    st.caption(f"Questions added: **{len(st.session_state.eval_questions)}** / 10")

    if len(st.session_state.eval_questions) < 10:
        with st.form(key="add_question_form", clear_on_submit=True):
            new_question = st.text_area(
                "Question",
                placeholder="e.g. What is the approval process for remote work?",
                height=100
            )
            new_ground_truth = st.text_area(
                "Ground Truth Answer",
                placeholder="e.g. Employees must submit a formal request to their manager...",
                height=100
            )

            add_clicked = st.form_submit_button(
                "➕ Add Question",
                use_container_width=True
            )

            if add_clicked:
                if new_question.strip() and new_ground_truth.strip():
                    st.session_state.eval_questions.append({
                        "question": new_question.strip(),
                        "ground_truth": new_ground_truth.strip(),
                        "document_name": None
                    })
                    st.rerun()
                else:
                    st.warning("⚠️ Please fill in both Question and Ground Truth before adding.")
    else:
        st.info("✅ Maximum of 10 questions reached.")

    st.divider()

    if st.session_state.eval_questions:
        st.markdown("### 📋 Added Questions")

        for i, q in enumerate(st.session_state.eval_questions):
            with st.container(border=True):
                q_col, del_col = st.columns([5, 1])
                with q_col:
                    st.markdown(f"**Q{i + 1}.** {q['question']}")
                    st.caption(f"✅ GT: {q['ground_truth'][:100]}{'...' if len(q['ground_truth']) > 100 else ''}")
                with del_col:
                    if st.button("❌", key=f"del_{i}", help="Remove this question"):
                        st.session_state.eval_questions.pop(i)
                        st.rerun()
    else:
        st.info("No questions added yet. Add at least 5 questions to run evaluation.")

    st.divider()

    questions_count = len(st.session_state.eval_questions)

    if questions_count >= 5:
        st.success(f"✅ {questions_count} questions ready. You can now run the evaluation.")

        if st.button(
            "🚀 Run Evaluation",
            use_container_width=True,
            type="primary",
            disabled=st.session_state.eval_running
        ):
            st.session_state.eval_running = True
            st.session_state.eval_scores = None

            with st.spinner("Running RAGAS evaluation... this may take a few minutes ⏳"):
                try:
                    payload = {
                        "questions": st.session_state.eval_questions,
                        "evaluation_type": "custom"
                    }
                    res = requests.post(
                        f"{BACKEND_URL}/rag/evaluate",
                        json=payload,
                        timeout=900
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.eval_scores = data["scores"]
                        st.session_state.eval_running = False
                        # Don't clear questions here — keep them visible with results
                        st.rerun()
                    else:
                        detail = res.json().get("detail", "Unknown error")
                        st.error(f"❌ Evaluation failed: {detail}")
                        st.session_state.eval_running = False

                except Exception as e:
                    st.error(f"❌ Something went wrong: {str(e)}")
                    st.session_state.eval_running = False
    else:
        remaining = 5 - questions_count
        st.warning(f"⚠️ Add {remaining} more question(s) to enable evaluation.")


# ─────────────────────────────────────────────
# RIGHT — EVALUATION SCORES
# ─────────────────────────────────────────────
with score_col:
    st.markdown("### 📊 Evaluation Results")
    st.divider()

    if st.session_state.eval_scores:
        scores = st.session_state.eval_scores

        st.success("✅ Evaluation Complete!")
        st.metric(label="Faithfulness", value=f"{scores['faithfulness']:.2f}", help="How factually consistent the answer is with the retrieved context")
        st.metric(label="Answer Relevancy", value=f"{scores['answer_relevancy']:.2f}", help="How relevant the answer is to the question asked")
        st.metric(label="Context Precision", value=f"{scores['context_precision']:.2f}", help="Whether the retrieved chunks are useful for answering")
        st.metric(label="Context Recall", value=f"{scores['context_recall']:.2f}", help="Whether all needed information was retrieved")
        st.divider()
        st.caption(f"Evaluated on {scores['num_questions']} questions")
        st.caption("Results saved to database ✅")

        if st.button("🔄 Run Another Evaluation", use_container_width=True):
            st.session_state.eval_scores = None
            st.session_state.eval_questions = []
            st.rerun()

    else:
        st.info("Scores will appear here after evaluation runs.")
        st.markdown("""
        **How scoring works:**

        - **Faithfulness** — Is the answer based on retrieved context or hallucinated?
        - **Answer Relevancy** — Does the answer address the question?
        - **Context Precision** — Are the retrieved chunks useful?
        - **Context Recall** — Was all needed info retrieved?

        All scores are between **0.0 and 1.0**.
        Higher is better ✅
        """)