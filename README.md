# Documentation Generator

> An AI-powered platform to generate, review, edit, and store professional documents using LLM, FastAPI, Streamlit, MySQL, and Notion.

---

## Project Overview

Documentation Generator is a full-stack AI application that helps users create publication-ready professional documents by:

- Selecting a document category and type
- Answering a guided set of questions
- Letting the LLM generate a complete, structured document
- Reviewing and editing each section with AI assistance
- Saving the final document to MySQL and pushing it to Notion

---

## Project Structure

```
project/
│
├── backend/
│   ├── main.py              # All FastAPI endpoints
│   ├── schema.py            # Pydantic request models
│   ├── prompt_builder.py    # Prompt construction with scale and depth maps
│   ├── llm.py               # AzureChatOpenAI via LangChain
│   ├── database.py          # MySQL connection
│   └── notion_service.py    # Notion API integration (in progress)
│
├── frontend/
│   ├── app.py               # Main Streamlit UI
│   └── callback.py          # Helper functions for questions and request building
│
├── .env                     # Environment variables (never commit this)
└── README.md
```

---

## Tech Stack

| Technology | Usage |
|---|---|
| Python | Primary programming language |
| FastAPI | Backend REST API |
| Streamlit | Frontend UI |
| LangChain | LLM orchestration |
| Azure OpenAI | Document generation and section rewriting |
| MySQL | Document and metadata storage |
| Pydantic | Request validation |
| Notion API | Document push and retrieval (in progress) |
| python-dotenv | Environment variable management |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/categories` | Fetch all document categories |
| GET | `/document-types` | Fetch all document types with components |
| GET | `/documents` | Fetch documents by category and type |
| GET | `/questions` | Fetch guided questions for a document |
| POST | `/generate-document` | Generate full document via LLM |
| POST | `/refine-section` | Rewrite a single section via LLM |
| POST | `/save-document` | Save finalized document to MySQL |
| POST | `/push-to-notion` | Push document to Notion (in progress) |

---

## Database Tables

| Table | Purpose |
|---|---|
| `categories` | Document categories — HR, Legal, Engineering etc. |
| `document_type` | Document types with component lists |
| `documents` | Document templates with titles and IDs |
| `questions` | Guided questions per document with type and options |
| `generated_documents` | Finalized documents with full content and metadata |

---

## Supported Document Types

| Type | Expected Length |
|---|---|
| POLICY | 4 to 8 pages |
| PROCEDURE | 3 to 6 pages |
| GUIDE | 8 to 15 pages |
| PLAN | 4 to 8 pages |
| AGREEMENT | 2 to 4 pages |
| RECORD | 1 to 3 pages |

---

## How It Works

### Step 1 — Select Document
- User selects a Category and Document Type from dropdowns
- Clicks **Get Documents** to fetch matching templates
- Selects a specific document

### Step 2 — Answer Questions
- System loads guided questions for the selected document
- User fills in answers — text, radio, multiselect, calendar, table inputs supported
- Clicks **Generate Document**

### Step 3 — Review & Edit Sections
- Document is split into sections by `---` dividers
- User navigates section by section with a progress bar
- For each section — user types an instruction and clicks **Rewrite with AI**
- LLM rewrites only that section based on the instruction
- User clicks **Finalize & Next** to move forward

### Step 4 — Save & Export
- Complete document shown after all sections are finalized
- User clicks **Save Document** to store in MySQL
- User can **Download as .txt** or **Push to Notion**

---

## Prompt Intelligence

### Document Scale Map
Each document type has a defined expected length, tone, and writing style injected into the prompt so the LLM writes the correct depth automatically.

### Component Depth Map
Every document component has a specific writing instruction — for example:
- `Step-by-Step Procedure` → comprehensive numbered steps, every action written explicitly
- `Exceptions` → concise, 2 to 4 sentences only
- `Commercial Terms` → precise, legally accurate, use a table if multiple items
- `Core Content` → at least 40% of total document, extensive with subsections

---

## Environment Setup

Create a `.env` file in the project root:

```env
OPEN_API_KEY=your_azure_openai_key
DEPLOYMENT_NAME=your_deployment_name
API_VERSION=your_api_version
AZURE_ENDPOINT=your_azure_endpoint
NOTION_API_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_notion_database_id
```

---

## Running the Project

**Start the backend:**
```bash
uvicorn main:app --reload
```

**Start the frontend:**
```bash
streamlit run app.py
```

---

## What Is Done

- [x] Document generation via LLM
- [x] Section-by-section review with navigation
- [x] AI-assisted section rewriting
- [x] Save to MySQL with metadata
- [x] Download as .txt
- [x] Prompt intelligence — scale map and component depth map

## What Is Remaining

- [ ] Notion — push document to Notion database
- [ ] Notion — view and retrieve documents from Notion
- [ ] Export to PDF and DOCX formats

---

> **Note:** Never commit your `.env` file to version control.