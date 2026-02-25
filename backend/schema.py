from pydantic import BaseModel
from typing import List, Literal


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
    answer: str

class DocumentRequest(BaseModel):
    category: DocumentCategory
    document_type: DocumentType
    document_name: str
    components: str
    answers: List[Answer]