from pydantic import BaseModel
from typing import List, Literal, Any, Optional
from datetime import date

DocumentType = Literal[
    "POLICY",
    "PROCEDURE",
    "GUIDE",
    "PLAN",
    "AGREEMENT",
    "RECORD"
]

DocumentCategory = Literal[
    "HR & People Operations",
    "Legal & Compliance",
    "Engineering & Operations",
    "Finance & Operations",
    "Marketing & Content",
    "Sales & Customer-Facing",
    "Product & Design"
]


class Answer(BaseModel):
    question: str
    answer: str | list[Any] | dict[Any, Any]

class DocumentRequest(BaseModel):
    category: DocumentCategory
    document_type: DocumentType
    document_name: str
    components: str
    answers: List[Answer]

class RefineSectionRequest(BaseModel):
    section_text: str
    instruction: str

class SaveDocumentRequest(BaseModel):
    document_id: int
    document_name: str
    category: DocumentCategory
    document_type: DocumentType
    document_content: str
    # version: Optional[str] = "1.0"
    author: Optional[str] = "Unknown"

class PushToNotionRequest(BaseModel):
    document_id: int
    document_name: str
    category: str
    document_type: str
    version: Optional[str] = None
    author: Optional[str] = "Unknown"
    industry: Optional[str] = ""
    content: str
    created_date: Optional[str] = date.today().isoformat()