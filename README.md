# 🤖 AI Documentation Platform — RAG + LangGraph Agent

> A full-stack AI-powered platform for a UCaaS/SaaS company that generates professional documents using LLM, provides intelligent RAG-based Q&A over those documents, and manages support tickets — all powered by Azure OpenAI, LangGraph, Milvus, MySQL, and Notion.

---

## 📋 Project Overview

This platform has two core capabilities:

**1. Document Generation**
- Select a document category and type
- Answer guided questions
- LLM generates a complete structured document
- Review and edit each section with AI assistance
- Save to MySQL and push to Notion

**2. Intelligent RAG Agent**
- Ask questions about 92+ company documents
- Compare two documents side by side
- Conversation memory with summarization
- Auto ticket creation for unanswered queries
- RAGAS evaluation of RAG pipeline quality

---

## 🗂️ Project Structure

```
NLP_project/
│
├── backend/
│   ├── main.py                  # All FastAPI endpoints
│   ├── schema.py                # Pydantic request/response models
│   ├── prompt_builder.py        # Prompt construction with scale and depth maps
│   ├── llm.py                   # AzureChatOpenAI via LangChain
│   ├── database.py              # MySQL connection
│   ├── notion_service.py        # Notion API — documents + tickets
│   ├── cache.py                 # Redis caching
│   ├── logger.py                # Logger — terminal + file output
│   ├── app.log                  # Log file
│   └── rag/
│       ├── __init__.py
│       ├── notion_loader.py     # Fetches documents from Notion
│       ├── chunker.py           # Splits documents into chunks
│       ├── embedder.py          # Converts text to vectors
│       ├── vector_store.py      # Milvus Lite vector database
│       ├── tools.py             # All agent tools and LLM functions
│       ├── agent.py             # LangGraph agent — full flow
│       ├── rag_pipeline.py      # Full ingestion pipeline
│       ├── ragas_eval.py        # RAGAS evaluation pipeline
│       ├── test_dataset.json    # 10 test questions with ground truth
│       └── rag_documents.db     # Milvus Lite database file
│
└── frontend/
    ├── app_new.py               # Document Generator — main page
    ├── callback.py              # Helper functions for questions
    ├── sidebar_style.py         # Sidebar styling
    └── pages/
        ├── rag_search.py        # RAG Chat page with 3 tabs
        ├── rag_evaluate.py      # Custom RAGAS evaluation page
        └── view_documents.py    # View Notion documents page
```

---

## 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| Python | Primary language |
| FastAPI | Backend REST API |
| Streamlit | Frontend UI |
| LangGraph | Agent orchestration and state management |
| LangChain | LLM integration |
| Azure OpenAI | GPT-4o-mini for generation and reasoning |
| Milvus Lite | Vector database for RAG |
| MySQL | Relational storage |
| Redis | API response caching |
| Notion API | Document and ticket storage |
| RAGAS | RAG pipeline evaluation |
| Pydantic | Request/response validation |
| python-dotenv | Environment variable management |

---

## 🔌 API Endpoints

### Document Generation

| Method | Endpoint | Description |
|---|---|---|
| GET | `/categories` | Fetch all document categories |
| GET | `/document-types` | Fetch all document types |
| GET | `/documents` | Fetch documents by category and type |
| GET | `/questions` | Fetch guided questions for a document |
| POST | `/generate-document` | Generate full document via LLM |
| POST | `/refine-section` | Rewrite a single section via LLM |
| POST | `/save-document` | Save document to MySQL with auto versioning |
| POST | `/push-to-notion` | Push document to Notion |
| GET | `/notion-documents` | Fetch all documents from Notion |
| GET | `/notion-document/{page_id}` | Fetch specific document content |

### RAG System

| Method | Endpoint | Description |
|---|---|---|
| POST | `/rag/ingest` | Ingest all Notion documents into Milvus |
| POST | `/rag/chat` | RAG Q&A with LangGraph agent |
| GET | `/rag/documents` | Get all document names from Milvus |
| GET | `/rag/evaluate/default` | Fetch or run default RAGAS evaluation |
| POST | `/rag/evaluate` | Run custom RAGAS evaluation |
| GET | `/rag/tickets` | Fetch all support tickets from Notion |

---

## 🧠 LangGraph Agent Flow

The RAG system is powered by a **ReAct LangGraph Agent** that reasons, decides, and acts on every query.

```
User Query
    ↓
memory_update_node
    → checks message count (threshold: 6)
    → summarizes oldest 4 messages if threshold reached
    → keeps latest 2 messages
    ↓
classify_and_followup_node
    → is it a follow-up query? → answer from memory
    → GENERAL_CHAT?            → friendly response
    → GENERAL_KNOWLEDGE?       → polite decline
    → COMPANY_QUERY?           → search documents
    ↓
refine_node → router_node
    ↓                ↓
search_node      compare_node
    ↓                ↓
      check_answer_node
      /               \
   GOOD               BAD
    ↓                   ↓
return answer      create_ticket_node
                        ↓
                   save to Notion
```

### Agent Nodes

| Node | Purpose |
|---|---|
| `memory_update_node` | Manages conversation memory and summarization |
| `classify_and_followup_node` | Classifies query type and detects follow-ups |
| `answer_from_memory_node` | Answers follow-up queries from conversation history |
| `general_node` | Handles casual conversation with memory context |
| `decline_node` | Politely declines out-of-scope queries |
| `refine_node` | Rewrites query for better search results |
| `router_node` | Routes to search or compare |
| `search_node` | Vector search + LLM answer generation |
| `compare_node` | Fetches and compares two documents |
| `check_answer_node` | LLM evaluates answer quality |
| `create_ticket_node` | Creates Notion support ticket with conversation context |

---

## 💬 Agent Intelligence

### Query Classification
Every query is classified into one of 3 types:
- **GENERAL_CHAT** → greetings, casual conversation
- **GENERAL_KNOWLEDGE** → world knowledge, sensitive system info, out of scope
- **COMPANY_QUERY** → company documents, policies, procedures

### Conversation Memory
- Stores last 6 messages in state
- When threshold reached → oldest 4 messages summarized by LLM
- Summary + recent messages passed to every node for context
- Memory persists across page navigation in session

### Follow-up Detection
- Detects if user is asking about previous response
- Answers directly from memory — no Milvus search needed
- Example: "summarize that" / "explain in simple terms"

### Answer Quality Check
- LLM evaluates if answer properly addresses the question
- Good answer → returned to user
- Bad answer → support ticket created automatically

---

## 🎫 Ticket System

When RAG cannot find a relevant answer:
- Auto creates a support ticket in Notion
- Ticket ID format: `TK-0001`, `TK-0002` etc.
- Saves full conversation context in ticket page body:
  - Conversation summary
  - Recent messages between user and AI
  - The unanswered query
- Dynamic LLM-generated response to user
- Ticket viewer available in RAG Chat UI

### Notion Ticket Properties

| Property | Type | Description |
|---|---|---|
| Ticket_id | Title | TK-0001 format |
| Query | Text | Original user question |
| Status | Select | open / progress / closed |
| Priority | Select | high / medium / low |
| Created_at | Date | Auto set to today |

---

## 📊 RAGAS Evaluation

The RAG pipeline is evaluated using 4 metrics:

| Metric | What it measures |
|---|---|
| Faithfulness | Is answer based on retrieved context? (no hallucination) |
| Answer Relevancy | Does answer address the question? |
| Context Precision | Are retrieved chunks useful? |
| Context Recall | Was all needed information retrieved? |

### Two evaluation modes:
- **Default** → runs on 10 hardcoded test questions, saved to MySQL, shown on first load
- **Custom** → user provides 5-10 questions with ground truth, saves to MySQL

---

## 🗄️ Database Tables

### MySQL

| Table | Purpose |
|---|---|
| `categories` | Document categories |
| `document_type` | Document types with components |
| `documents` | Document templates |
| `questions` | Guided questions per document |
| `generated_documents` | Saved documents with auto versioning |
| `ragas_evaluations` | RAGAS scores for default and custom evaluations |

### Notion Databases

| Database | Purpose |
|---|---|
| Documents | All generated company documents |
| Support Tickets | All unanswered query tickets |

---

## 📄 Supported Document Types

| Type | Expected Length |
|---|---|
| POLICY | 4 to 8 pages |
| PROCEDURE | 3 to 6 pages |
| GUIDE | 8 to 15 pages |
| PLAN | 4 to 8 pages |
| AGREEMENT | 2 to 4 pages |
| RECORD | 1 to 3 pages |

---

## 🖥️ Frontend Pages

| Page | Description |
|---|---|
| `app_new.py` | Document Generator — 4 step flow |
| `pages/rag_search.py` | RAG Chat with 3 tabs (Chat, RAG Scores, Tickets) |
| `pages/rag_evaluate.py` | Custom RAGAS evaluation — add 5-10 questions |
| `pages/view_documents.py` | Browse and view Notion documents |

---

## ⚙️ Environment Setup

Create a `.env` file in the `backend/` directory:

```env
# Azure OpenAI
OPEN_API_KEY=your_azure_openai_key
DEPLOYMENT_NAME=gpt-4o-mini
API_VERSION=2024-08-01-preview
AZURE_ENDPOINT=your_azure_endpoint

# Embeddings
EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large
EMBEDDING_MODEL_NAME=text-embedding-3-large

# Notion
NOTION_API_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_documents_database_id
NOTION_TICKET_DATABASE_ID=your_tickets_database_id

# MySQL
# configured in database.py

# Redis
# configured in cache.py
```

---

## 🚀 Running the Project

**Start the backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Start the frontend:**
```bash
cd frontend
streamlit run app_new.py
```

**Run default RAGAS evaluation (first time):**
```bash
cd backend
python rag/ragas_eval.py
```

---

## ⚠️ Important Notes

- `pymilvus` must be version `2.4.9` — newer versions hang
- Milvus Lite only allows one connection at a time — stop FastAPI before running `vector_store.py` directly
- `rag_documents.db` must not be read-only — delete and recreate if permission issues
- Never commit your `.env` file to version control
- RAGAS evaluation uses `ragas==0.4.3` (Vibrant Labs fork) — not the original ragas package

---

## ✅ What Is Complete

- [x] Document generation with UCaaS/SaaS context
- [x] Section review and AI rewrite
- [x] Auto versioning in MySQL
- [x] Push to Notion with formatted blocks
- [x] View documents page
- [x] Redis caching
- [x] LangGraph ReAct Agent — full flow
- [x] Conversation memory with summarization
- [x] Follow-up query detection
- [x] Query classification (Chat/Knowledge/Company)
- [x] RAG ingestion — 92 documents, 1037 chunks
- [x] RAG search with citations and relevance scores
- [x] RAG compare — 2 document comparison
- [x] Answer quality check with LLM
- [x] Auto ticket creation in Notion
- [x] Ticket viewer in UI
- [x] RAGAS evaluation — default and custom
- [x] Evaluation UI with scores
- [x] RAG scores tab in chat UI
- [x] Logger with graph path logging

---

> **Note:** Never commit your `.env` file to version control.