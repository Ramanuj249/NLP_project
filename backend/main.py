from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any
from database import get_connection

app = FastAPI()

@app.get("/")
def root():
    return {"status": "working"}


@app.get("/categories")
def get_categories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, category_name FROM categories")
    data = cursor.fetchall()
    conn.close()
    return data

@app.get("/document-types")
def get_document_types():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, document_type_name FROM document_type")
    data = cursor.fetchall()
    conn.close()
    return data


@app.get("/documents")
def get_documents(category_id: int, document_type_id: int):
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
    return data

@app.get("/questions")
def get_question(document_id: int):
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
    return data

