import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from datasets import Dataset
from embedder import embed_text
from vector_store import search_chunk
from tools import search_tool
from logger import logger

load_dotenv()

DATASET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_dataset.json")

def get_ragas_llm():
    from langchain_openai import AzureChatOpenAI
    return AzureChatOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("OPEN_API_KEY"),
        api_version=os.getenv("API_VERSION"),
        temperature=0.0
    )

def get_ragas_embeddings():
    from langchain_openai import AzureOpenAIEmbeddings
    return AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("EMBEDDING_DEPLOYMENT_NAME"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("OPEN_API_KEY"),
        api_version=os.getenv("API_VERSION")
    )

def load_test_dataset() -> list:
    with open(DATASET_FILE, "r") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} questions from dataset")
    return data

def get_rag_response(question: str) -> dict:
    query_vector = embed_text(question)
    chunks = search_chunk(
        query_vector=query_vector,
        top_k=5
    )
    contexts = [chunk["text"] for chunk in chunks]
    result = search_tool(query=question)
    return {
        "answer": result["answer"],
        "contexts": contexts
    }

def run_evaluation() -> dict:
    logger.info("Starting RAGAS evaluation...")

    test_data = load_test_dataset()

    if not test_data:
        logger.error("No test data found")
        return {}

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in test_data:
        logger.info(f"Getting RAG response for: {item['question'][:50]}")
        rag_response = get_rag_response(item["question"])
        questions.append(item["question"])
        answers.append(rag_response["answer"])
        contexts.append(rag_response["contexts"])
        ground_truths.append(item["ground_truth"])

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })

    logger.info("Running RAGAS metrics...")
    llm = get_ragas_llm()
    embeddings = get_ragas_embeddings()

    faithfulness_metric = Faithfulness(llm=llm)
    answer_relevancy_metric = AnswerRelevancy(llm=llm, embeddings=embeddings)
    context_precision_metric = ContextPrecision(llm=llm)
    context_recall_metric = ContextRecall(llm=llm)

    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness_metric,
            answer_relevancy_metric,
            context_precision_metric,
            context_recall_metric
        ]
    )

    scores = {
        "faithfulness": round(float(np.mean(results["faithfulness"])), 4),
        "answer_relevancy": round(float(np.mean(results["answer_relevancy"])), 4),
        "context_precision": round(float(np.mean(results["context_precision"])), 4),
        "context_recall": round(float(np.mean(results["context_recall"])), 4),
        "num_questions": len(questions),
        "test_questions": [
            {
                "question": questions[i],
                "answer": answers[i],
                "ground_truth": ground_truths[i]
            }
            for i in range(len(questions))
        ]
    }

    logger.info(f"RAGAS complete — scores: {scores}")
    return scores

if __name__ == "__main__":
    results = run_evaluation()
    if results:
        print(f"Faithfulness: {results['faithfulness']}")
        print(f"Answer Relevancy: {results['answer_relevancy']}")
        print(f"Context Precision: {results['context_precision']}")
        print(f"Context Recall: {results['context_recall']}")
        print(f"Evaluated on {results['num_questions']} questions")