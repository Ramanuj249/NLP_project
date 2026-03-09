from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any
from database import get_connection
from schema import DocumentRequest, RefineSectionRequest, SaveDocumentRequest, PushToNotionRequest
from prompt_builder import build_prompt, build_refine_section_prompt
from llm import generate_llm_response
from notion_service import push_document, get_all_documents, get_document_content
from cache import get_cache, set_cache

app = FastAPI()

@app.get("/")
def root():
    return {"status": "working"}


@app.get("/categories")
def get_categories():
    cached = get_cache("categories")
    if cached:
        print("Categories served from cache")
        return cached
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, category_name FROM categories")
    data = cursor.fetchall()
    conn.close()
    set_cache("categories", data)
    return data

@app.get("/document-types")
def get_document_types():
    cached = get_cache("document_types")
    if cached:
        print("Document types served from cache")
        return cached
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM document_type")
    data = cursor.fetchall()
    conn.close()
    set_cache("document_types", data)
    return data

@app.get("/documents")
def get_documents(category_id: int, document_type_id: int):
    cache_key = f"documents_{category_id}_{document_type_id}"
    cached = get_cache(cache_key)
    if cached:
        print(f"Documents served from cache for key: {cache_key}")
        return cached
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT id, title
    FROM documents
    WHERE category_id = %s
    AND document_type_id = %s
    """
    cursor.execute(query, (category_id, document_type_id))
    data = cursor.fetchall()
    conn.close()
    set_cache(cache_key, data)
    return data

@app.get("/questions")
def get_question(document_id: int):
    cache_key = f"questions_{document_id}"
    cached = get_cache(cache_key)
    if cached:
        print(f"Questions served from cache for key: {cache_key}")
        return cached
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT id, question, type, options
    FROM questions 
    WHERE document_id = %s
    """
    cursor.execute(query, (document_id,))
    data = cursor.fetchall()
    conn.close()
    set_cache(cache_key, data)
    return data


@app.post("/generate-document")
def generate_document(data: DocumentRequest):
    prompt = build_prompt(data)
    # print(prompt)
    response = generate_llm_response(prompt)
    return {
        "response": response
    }

@app.post("/refine-section")
def refine_section(data: RefineSectionRequest):
    prompt = build_refine_section_prompt(data)
    response = generate_llm_response(prompt)
    return {
        "refined_section": response
    }

@app.post("/save-document")
def save_document(data: SaveDocumentRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # Count existing versions for this document
    cursor.execute(
        "SELECT COUNT(*) FROM generated_documents WHERE document_id = %s",
        (data.document_id,)
    )
    count = cursor.fetchone()[0]
    version = float(count + 1)
    version_str = f"{int(version)}.0"

    query = """
    INSERT INTO generated_documents (
        document_id, document_name, category, document_type,
        document_content, version, author
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        data.document_id, data.document_name, data.category, data.document_type,
        data.document_content, version_str, data.author
    ))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return {
        "message": "Document saved successfully",
        "generated_document_id": inserted_id,
        "version": version_str
    }

@app.post("/push-to-notion")
def push_to_notion(data: PushToNotionRequest):
    result = push_document(data)
    return {
        "message": "Document pushed to Notion successfully",
        "page_id": result["page_id"],
        "url": result["url"]
    }

@app.get("/notion-documents")
def notion_documents():
    documents = get_all_documents()
    return documents


@app.get("/notion-document/{page_id}")
def notion_document(page_id: str):
    content = get_document_content(page_id)
    return {"content": content}