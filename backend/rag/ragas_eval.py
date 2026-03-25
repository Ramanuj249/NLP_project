import json
import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory
from ragas.metrics.collections import AnswerRelevancy, ContextRecall
from ragas.metrics.collections import ContextPrecisionWithReference, Faithfulness

from rag.embedder import embed_text
from rag.vector_store import search_chunk
from rag.tools import search_tool
from rag.logger import logger

load_dotenv()

DATASET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_dataset.json")


# ─────────────────────────────────────────────
# CLIENT + METRIC SETUP
# ─────────────────────────────────────────────

def get_async_client() -> AsyncAzureOpenAI:
    """Single shared AsyncAzureOpenAI client for both LLM and embeddings."""
    return AsyncAzureOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("OPEN_API_KEY"),
        api_version=os.getenv("API_VERSION"),
    )


def get_metrics(client: AsyncAzureOpenAI) -> dict:
    """
    Initialize all 4 RAGAS metrics using modern InstructorLLM.
    Returns a dict of metric_name -> metric_object.
    """
    llm = llm_factory(
        model=os.getenv("DEPLOYMENT_NAME"),
        client=client
    )
    embeddings = embedding_factory(
        model=os.getenv("EMBEDDING_DEPLOYMENT_NAME"),
        client=client,
        interface="modern"
    )
    return {
        "faithfulness": Faithfulness(llm=llm),
        "answer_relevancy": AnswerRelevancy(llm=llm, embeddings=embeddings),
        "context_precision": ContextPrecisionWithReference(llm=llm),
        "context_recall": ContextRecall(llm=llm),
    }


# ─────────────────────────────────────────────
# RAG RESPONSE
# ─────────────────────────────────────────────

def get_rag_response(question: str) -> dict:
    """
    For a given question:
    - Get RAG answer via search_tool()
    - Get retrieved contexts via search_chunk()
    Returns dict with 'answer' and 'contexts'.
    """
    query_vector = embed_text(question)
    chunks = search_chunk(query_vector=query_vector, top_k=5)
    contexts = [chunk["text"] for chunk in chunks]
    result = search_tool(query=question)
    return {
        "answer": result.get("answer", ""),
        "contexts": contexts
    }


# ─────────────────────────────────────────────
# SCORING LOGIC
# ─────────────────────────────────────────────

async def score_single_sample(sample: dict, metrics: dict) -> dict:
    """
    Score one sample across all 4 metrics.
    If a metric fails for a sample, returns nan for that metric only.
    """
    question = sample["question"]
    answer = sample["answer"]
    contexts = sample["contexts"]
    ground_truth = sample["ground_truth"]

    scores = {}

    # Faithfulness — needs: user_input, response, retrieved_contexts
    try:
        result = await metrics["faithfulness"].ascore(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts
        )
        scores["faithfulness"] = result.value
    except Exception as e:
        logger.warning(f"Faithfulness scoring failed for '{question[:40]}': {e}")
        scores["faithfulness"] = float("nan")

    # Answer Relevancy — needs: user_input, response only
    try:
        result = await metrics["answer_relevancy"].ascore(
            user_input=question,
            response=answer
        )
        scores["answer_relevancy"] = result.value
    except Exception as e:
        logger.warning(f"AnswerRelevancy scoring failed for '{question[:40]}': {e}")
        scores["answer_relevancy"] = float("nan")

    # Context Precision — needs: user_input, reference, retrieved_contexts
    try:
        result = await metrics["context_precision"].ascore(
            user_input=question,
            reference=ground_truth,
            retrieved_contexts=contexts
        )
        scores["context_precision"] = result.value
    except Exception as e:
        logger.warning(f"ContextPrecision scoring failed for '{question[:40]}': {e}")
        scores["context_precision"] = float("nan")

    # Context Recall — needs: user_input, retrieved_contexts, reference
    try:
        result = await metrics["context_recall"].ascore(
            user_input=question,
            retrieved_contexts=contexts,
            reference=ground_truth
        )
        scores["context_recall"] = result.value
    except Exception as e:
        logger.warning(f"ContextRecall scoring failed for '{question[:40]}': {e}")
        scores["context_recall"] = float("nan")

    return scores


async def score_all_samples(samples: list, metrics: dict) -> list:
    """
    Score all samples sequentially.
    Returns list of per-sample score dicts.
    """
    all_scores = []
    for i, sample in enumerate(samples):
        logger.info(f"Scoring sample {i + 1}/{len(samples)}: {sample['question'][:50]}")
        scores = await score_single_sample(sample, metrics)
        all_scores.append(scores)
        logger.info(f"Sample {i + 1} scores: {scores}")
    return all_scores


def compute_final_scores(all_scores: list, num_questions: int) -> dict:
    """
    Average scores across all samples using nanmean.
    nanmean safely ignores any nan values from failed scorings.
    """
    return {
        "faithfulness": round(float(np.nanmean([s["faithfulness"] for s in all_scores])), 4),
        "answer_relevancy": round(float(np.nanmean([s["answer_relevancy"] for s in all_scores])), 4),
        "context_precision": round(float(np.nanmean([s["context_precision"] for s in all_scores])), 4),
        "context_recall": round(float(np.nanmean([s["context_recall"] for s in all_scores])), 4),
        "num_questions": num_questions,
    }


def build_samples_from_data(test_data: list) -> list:
    """
    Get RAG responses for all questions in test_data.
    Returns list of sample dicts ready for scoring.
    """
    samples = []
    for item in test_data:
        logger.info(f"Getting RAG response for: {item['question'][:50]}")
        rag_response = get_rag_response(item["question"])
        samples.append({
            "question": item["question"],
            "answer": rag_response["answer"],
            "contexts": rag_response["contexts"],
            "ground_truth": item["ground_truth"],
            "document_name": item.get("document_name", None)
        })
    return samples


# ─────────────────────────────────────────────
# DEFAULT EVALUATION
# Uses test_dataset.json — 10 hardcoded questions
# Called only ONCE — when no data exists in MySQL
# ─────────────────────────────────────────────

def run_default_evaluation() -> dict:
    """
    Run RAGAS evaluation on the default test_dataset.json.
    Saves results to MySQL with evaluation_type = 'default'.
    Returns final averaged scores.
    """
    logger.info("Starting DEFAULT RAGAS evaluation...")

    with open(DATASET_FILE, "r") as f:
        test_data = json.load(f)

    if not test_data:
        logger.error("test_dataset.json is empty")
        return {}

    logger.info(f"Loaded {len(test_data)} questions from test_dataset.json")

    samples = build_samples_from_data(test_data)

    client = get_async_client()
    metrics = get_metrics(client)

    all_scores = asyncio.run(score_all_samples(samples, metrics))

    final_scores = compute_final_scores(all_scores, len(samples))

    try:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        for item in samples:
            cursor.execute("""
                INSERT INTO ragas_evaluations (
                    question, ground_truth, document_name,
                    faithfulness, answer_relevancy,
                    context_precision, context_recall,
                    evaluation_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item["question"],
                item["ground_truth"],
                item.get("document_name"),
                final_scores["faithfulness"],
                final_scores["answer_relevancy"],
                final_scores["context_precision"],
                final_scores["context_recall"],
                "default"
            ))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Default evaluation scores saved to MySQL")
    except Exception as e:
        logger.error(f"Failed to save default evaluation to MySQL: {e}")

    logger.info(f"DEFAULT evaluation complete — scores: {final_scores}")
    return final_scores


# ─────────────────────────────────────────────
# CUSTOM EVALUATION
# Uses user-provided questions from UI (5-10 questions)
# Called when user clicks Run Evaluation in UI
# ─────────────────────────────────────────────

def run_custom_evaluation(questions: list) -> dict:
    """
    Run RAGAS evaluation on user-provided questions.
    Saves results to MySQL with evaluation_type = 'custom'.
    Returns final averaged scores.

    Args:
        questions: list of dicts with keys:
                   - question (str)
                   - ground_truth (str)
                   - document_name (str, optional)
    """
    logger.info(f"Starting CUSTOM RAGAS evaluation with {len(questions)} questions...")

    if len(questions) < 5:
        raise ValueError("Minimum 5 questions required for custom evaluation")
    if len(questions) > 10:
        raise ValueError("Maximum 10 questions allowed for custom evaluation")

    samples = build_samples_from_data(questions)

    client = get_async_client()
    metrics = get_metrics(client)

    all_scores = asyncio.run(score_all_samples(samples, metrics))

    final_scores = compute_final_scores(all_scores, len(samples))

    try:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        for item in samples:
            cursor.execute("""
                INSERT INTO ragas_evaluations (
                    question, ground_truth, document_name,
                    faithfulness, answer_relevancy,
                    context_precision, context_recall,
                    evaluation_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item["question"],
                item["ground_truth"],
                item.get("document_name"),
                final_scores["faithfulness"],
                final_scores["answer_relevancy"],
                final_scores["context_precision"],
                final_scores["context_recall"],
                "custom"
            ))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Custom evaluation scores saved to MySQL")
    except Exception as e:
        logger.error(f"Failed to save custom evaluation to MySQL: {e}")

    logger.info(f"CUSTOM evaluation complete — scores: {final_scores}")
    return final_scores


# ─────────────────────────────────────────────
# FETCH LATEST SCORES FROM MySQL
# Used by page load to show existing scores instantly
# ─────────────────────────────────────────────

def get_latest_scores(evaluation_type: str) -> dict:
    """
    Fetch the latest evaluation scores from MySQL.
    Returns None if no scores exist yet.

    Args:
        evaluation_type: "default" or "custom"
    """
    try:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT faithfulness, answer_relevancy,
                   context_precision, context_recall,
                   COUNT(*) as num_questions, evaluated_at
            FROM ragas_evaluations
            WHERE evaluation_type = %s
            ORDER BY evaluated_at DESC
            LIMIT 1
        """, (evaluation_type,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row or row["faithfulness"] is None:
            return None

        return {
            "faithfulness": row["faithfulness"],
            "answer_relevancy": row["answer_relevancy"],
            "context_precision": row["context_precision"],
            "context_recall": row["context_recall"],
            "evaluated_at": str(row["evaluated_at"])
        }
    except Exception as e:
        logger.error(f"Failed to fetch latest scores from MySQL: {e}")
        return None


# ─────────────────────────────────────────────
# SCRIPT ENTRY POINT — runs default evaluation
# ─────────────────────────────────────────────

if __name__ == "__main__":
    results = run_default_evaluation()
    if results:
        print(f"\n========== RAGAS Default Evaluation Results ==========")
        print(f"  Faithfulness       : {results['faithfulness']}")
        print(f"  Answer Relevancy   : {results['answer_relevancy']}")
        print(f"  Context Precision  : {results['context_precision']}")
        print(f"  Context Recall     : {results['context_recall']}")
        print(f"  Evaluated on       : {results['num_questions']} questions")
        print(f"======================================================\n")