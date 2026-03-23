from fastapi import FastAPI, HTTPException
from database import get_connection
from schema import DocumentRequest, RefineSectionRequest, SaveDocumentRequest, PushToNotionRequest, RAGQueryRequest
from prompt_builder import build_prompt, build_refine_section_prompt
from llm import generate_llm_response
from notion_service import push_document, get_all_documents, get_document_content
from cache import get_cache, set_cache
from rag.logger import logger
from rag.rag_pipeline import ingest_documents
from rag.agent import run_agent


app = FastAPI()

@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"status": "working"}


@app.get("/categories")
def get_categories():
    try:
        cached = get_cache("categories")
        if cached:
            logger.info("Categories served from cache")
            return cached
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, category_name FROM categories")
        data = cursor.fetchall()
        conn.close()
        set_cache("categories", data)
        logger.info(f"Categories fetched — {len(data)} categories returned")
        return data
    except Exception as e:
        logger.error(f"Error fetching categories — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")


@app.get("/document-types")
def get_document_types():
    try:
        cached = get_cache("document_types")
        if cached:
            logger.info("Document types served from cache")
            return cached
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM document_type")
        data = cursor.fetchall()
        conn.close()
        set_cache("document_types", data)
        logger.info(f"Document types fetched — {len(data)} types returned")
        return data
    except Exception as e:
        logger.error(f"Error fetching Document Types — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error Document Types: {str(e)}")


@app.get("/documents")
def get_documents(category_id: int, document_type_id: int):
    try:
        cache_key = f"documents_{category_id}_{document_type_id}"
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Documents served from cache for key: {cache_key}")
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
        logger.info(
            f"Documents fetched — category_id: {category_id}, document_type_id: {document_type_id}, {len(data)} documents returned")
        return data
    except Exception as e:
        logger.error(f"Error fetching Documents — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Documents: {str(e)}")

@app.get("/questions")
def get_question(document_id: int):
    try:
        cache_key = f"questions_{document_id}"
        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Questions served from cache for key: {cache_key}")
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
        logger.info(f"Questions fetched — document_id: {document_id}, {len(data)} questions returned")
        return data
    except Exception as e:
        logger.error(f"Error fetching Questions — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching questions: {str(e)}")


@app.post("/generate-document")
def generate_document(data: DocumentRequest):
    try:
        prompt = build_prompt(data)
        logger.info(f"Generating document — name: {data.document_name}, type: {data.document_type}, category: {data.category}")
        response = generate_llm_response(prompt)
        logger.info(f"Document generated successfully — name: {data.document_name}")
        return {
            "response": response
        }
    except Exception as e:
        logger.error(f"Error in generating Document — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in generating Document: {str(e)}")

@app.post("/refine-section")
def refine_section(data: RefineSectionRequest):
    try:
        prompt = build_refine_section_prompt(data)
        response = generate_llm_response(prompt)
        logger.info(f"Refining section — instruction: {data.instruction[:50]}")
        logger.info("Section refined successfully")
        return {
            "refined_section": response
        }
    except Exception as e:
        logger.error(f"Error in Refining Sections — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Refining Sections: {str(e)}")

@app.post("/save-document")
def save_document(data: SaveDocumentRequest):
    try:
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
        logger.info(f"Saving document — name: {data.document_name}, author: {data.author}")
        cursor.execute(query, (
            data.document_id, data.document_name, data.category, data.document_type,
            data.document_content, version_str, data.author
        ))
        conn.commit()
        inserted_id = cursor.lastrowid
        logger.info(f"Document saved successfully — id: {inserted_id}, version: {version_str}")
        conn.close()
        return {
            "message": "Document saved successfully",
            "generated_document_id": inserted_id,
            "version": version_str
        }
    except Exception as e:
        logger.error(f"Error in Saving Document in Database — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Saving Document in Database: {str(e)}")

@app.post("/push-to-notion")
def push_to_notion(data: PushToNotionRequest):
    try:
        logger.info(f"Pushing document to Notion — name: {data.document_name}")
        result = push_document(data)
        logger.info(f"Document pushed to Notion successfully — page_id: {result['page_id']}")
        return {
            "message": "Document pushed to Notion successfully",
            "page_id": result["page_id"],
            "url": result["url"]
        }
    except Exception as e:
        logger.error(f"Error in Pushing Document in Notion — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Pushing Document in Notion: {str(e)}")

@app.get("/notion-documents")
def notion_documents():
    try:
        documents = get_all_documents()
        logger.info(f"Fetching all Notion documents — {len(documents)} documents returned")
        return documents
    except Exception as e:
        logger.error(f"Error in Fetching Document from Notion — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Fetching Document from Notion: {str(e)}")


@app.get("/notion-document/{page_id}")
def notion_document(page_id: str):
    try:
        content = get_document_content(page_id)
        logger.info(f"Fetching Notion document content — page_id: {page_id}")
        return {"content": content}
    except Exception as e:
        logger.error(f"Error in Fetching Document Content — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Fetching Document Content: {str(e)}")


@app.post("/rag/ingest")
def rag_ingest(limit: int = None):
    try:
        logger.info("RAG ingestion started via API")
        result = ingest_documents(limit=limit)
        logger.info(f"RAG ingestion complete — {result['documents']} documents, {result['chunks']} chunks")
        return {
            "message": "Ingestion complete",
            "documents": result["documents"],
            "chunks": result["chunks"]
        }
    except Exception as e:
        logger.error(f"RAG ingestion failed — {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/rag/chat")
def rag_chat(data: RAGQueryRequest):
    try:
        logger.info(f"RAG chat query received: {data.query}")
        result = run_agent(
            user_query=data.query,
            filters=data.filters
        )
        logger.info(f"RAG chat complete — tool used: {result['tool_used']}")
        return result
    except Exception as e:
        logger.error(f"RAG chat failed — {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG chat failed: {str(e)}")

@app.get("/rag/documents")
def rag_documents():
    try:
        from rag.vector_store import get_client, COLLECTION_NAME
        client = get_client()
        results = client.query(
            collection_name=COLLECTION_NAME,
            filter="chunk_index == 0",
            output_fields=["document_name", "document_type", "category"],
            limit=200
        )
        documents = []
        seen = set()
        for r in results:
            if r["document_name"] not in seen:
                seen.add(r["document_name"])
                documents.append({
                    "document_name": r["document_name"],
                    "document_type": r["document_type"],
                    "category": r["category"]
                })
        logger.info(f"RAG documents list returned — {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Error fetching RAG documents — {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))