import os
import re
from notion_client import Client
from dotenv import load_dotenv
from schema import PushToNotionRequest

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


# ─────────────────────────────────────────────
# Rich Text Builder (handles bold **)
# ─────────────────────────────────────────────

def parse_rich_text(text: str) -> list:
    """
    Converts a line with **bold** markers into
    a Notion rich_text array with bold annotations.
    """
    parts = []
    pattern = re.split(r'(\*\*.*?\*\*)', text)
    for part in pattern:
        if part.startswith("**") and part.endswith("**"):
            parts.append({
                "type": "text",
                "text": {"content": part[2:-2]},
                "annotations": {"bold": True}
            })
        else:
            if part:
                parts.append({
                    "type": "text",
                    "text": {"content": part},
                    "annotations": {"bold": False}
                })
    return parts if parts else [{"type": "text", "text": {"content": text}}]


# ─────────────────────────────────────────────
# Table Parser
# ─────────────────────────────────────────────

def is_table_row(line: str) -> bool: # helper functions
    return line.strip().startswith("|") and line.strip().endswith("|")

def is_separator_row(line: str) -> bool: # helper functions
    return is_table_row(line) and all(c in "|- :" for c in line.strip())

def parse_table_rows(lines: list, start_idx: int):
    """
    Collects all consecutive table rows starting from start_idx.
    Returns (table_block, next_index)
    """
    rows = []
    i = start_idx

    while i < len(lines) and is_table_row(lines[i]):
        if not is_separator_row(lines[i]):
            cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
            rows.append(cells)
        i += 1

    if not rows:
        return None, i

    col_count = max(len(row) for row in rows)

    # Pad rows to same column count
    for row in rows:
        while len(row) < col_count:
            row.append("")

    table_block = {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": col_count,
            "has_column_header": True,
            "has_row_header": False,
            "children": [
                {
                    "object": "block",
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": cell}}]
                            for cell in row
                        ]
                    }
                }
                for row in rows
            ]
        }
    }

    return table_block, i


# ─────────────────────────────────────────────
# Main Markdown to Notion Blocks Converter
# ─────────────────────────────────────────────

def markdown_to_notion_blocks(content: str) -> list:
    blocks = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # --- Empty line → skip ---
        if stripped == "":
            i += 1
            continue

        # --- Divider ---
        elif stripped == "---":
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
            i += 1

        # --- Heading 1 ---
        elif stripped.startswith("# ") and not stripped.startswith("## "):
            text = stripped[2:].strip()
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": parse_rich_text(text)}
            })
            i += 1

        # --- Heading 2 ---
        elif stripped.startswith("## ") and not stripped.startswith("### "):
            text = stripped[3:].strip()
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": parse_rich_text(text)}
            })
            i += 1

        # --- Heading 3 ---
        elif stripped.startswith("### "):
            text = stripped[4:].strip()
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": parse_rich_text(text)}
            })
            i += 1

        # --- Bullet points ---
        elif stripped.startswith("- ") or stripped.startswith("* "):
            text = stripped[2:].strip()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_rich_text(text)}
            })
            i += 1

        # --- Numbered list ---
        elif re.match(r'^\d+\.\s', stripped):
            text = re.sub(r'^\d+\.\s', '', stripped).strip()
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_rich_text(text)}
            })
            i += 1

        # --- Table ---
        elif is_table_row(stripped):
            table_block, i = parse_table_rows(lines, i)
            if table_block:
                blocks.append(table_block)

        # --- Paragraph ---
        else:
            text = stripped.replace("`", "")
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": parse_rich_text(text)}
            })
            i += 1

    return blocks


# ─────────────────────────────────────────────
# Chunk blocks into groups of 100
# ─────────────────────────────────────────────

def chunk_blocks(blocks: list) -> list:
    return [blocks[i:i + 100] for i in range(0, len(blocks), 100)]


# ─────────────────────────────────────────────
# Push Document to Notion
# ─────────────────────────────────────────────

def push_document(data: PushToNotionRequest):

    all_blocks = markdown_to_notion_blocks(data.content)
    chunks = chunk_blocks(all_blocks)

    response = notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "name": {"title": [{"type": "text", "text": {"content": data.document_name}}]},
            "id": {"rich_text": [{"type": "text", "text": {"content": str(data.document_id)}}]},
            "category": {"rich_text": [{"type": "text", "text": {"content": data.category}}]},
            "type": {"rich_text": [{"type": "text", "text": {"content": data.document_type}}]},
            "created_by": {"rich_text": [{"type": "text", "text": {"content": data.author}}]},
            "industry": {"rich_text": [{"type": "text", "text": {"content": data.industry}}]},
            "version": {"number": float(data.version)},
            "created_date": {"date": {"start": data.created_date}},
        },
        children=chunks[0] if chunks else []
    )

    page_id = response["id"]

    for chunk in chunks[1:]:
        notion.blocks.children.append(block_id=page_id, children=chunk)

    return {"page_id": page_id, "url": response["url"]}


def get_all_documents() -> list:
    response = notion.databases.query(database_id=DATABASE_ID)
    documents = []
    for page in response["results"]:
        props = page["properties"]
        def get_text(prop):
            try:
                return prop["rich_text"][0]["text"]["content"]
            except:
                return ""
        def get_title(prop):
            try:
                return prop["title"][0]["text"]["content"]
            except:
                return ""
        def get_date(prop):
            try:
                return prop["date"]["start"]
            except:
                return ""

        documents.append({
            "page_id": page["id"],
            "name": get_title(props.get("name", {})),
            "category": get_text(props.get("category", {})),
            "type": get_text(props.get("type", {})),
            "version": get_text(props.get("version", {})),
            "created_by": get_text(props.get("created_by", {})),
            "created_date": get_date(props.get("created_date", {})),
        })
    return documents


def get_document_content(page_id: str) -> str:
    response = notion.blocks.children.list(block_id=page_id)
    lines = []
    for block in response["results"]:
        block_type = block["type"]
        def extract_text(rich_text_list):
            return "".join([t["text"]["content"] for t in rich_text_list])
        if block_type == "heading_1":
            text = extract_text(block["heading_1"]["rich_text"])
            lines.append(f"# {text}")
        elif block_type == "heading_2":
            text = extract_text(block["heading_2"]["rich_text"])
            lines.append(f"## {text}")
        elif block_type == "heading_3":
            text = extract_text(block["heading_3"]["rich_text"])
            lines.append(f"### {text}")
        elif block_type == "bulleted_list_item":
            text = extract_text(block["bulleted_list_item"]["rich_text"])
            lines.append(f"- {text}")
        elif block_type == "numbered_list_item":
            text = extract_text(block["numbered_list_item"]["rich_text"])
            lines.append(f"1. {text}")
        elif block_type == "paragraph":
            text = extract_text(block["paragraph"]["rich_text"])
            lines.append(text)
        elif block_type == "divider":
            lines.append("---")
    return "\n\n".join(lines)