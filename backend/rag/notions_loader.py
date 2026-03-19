import os
from  notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv("NOTION_API_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def extract_metadata(page: dict) -> dict:
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

    return {
        "page_id": page["id"],
        "document_name": get_title(props.get("name", {})),
        "category": get_text(props.get("category", {})),
        "document_type": get_text(props.get("type", {})),
        "industry": get_text(props.get("industry", {})),
        "author": get_text(props.get("created_by", {})),
        "created_date": get_date(props.get("created_date", {})),
    }


def extract_content(page_id: str) -> str:
    response = notion.blocks.children.list(block_id=page_id)
    lines = []

    for block in response["results"]:
        block_type = block["type"]

        def get_text(rich_text_list):
            try:
                return "".join([t["text"]["content"] for t in rich_text_list])
            except:
                return ""

        if block_type == "heading_1":
            lines.append(f"# {get_text(block['heading_1']['rich_text'])}")
        elif block_type == "heading_2":
            lines.append(f"## {get_text(block['heading_2']['rich_text'])}")
        elif block_type == "heading_3":
            lines.append(f"### {get_text(block['heading_3']['rich_text'])}")
        elif block_type == "bulleted_list_item":
            lines.append(f"- {get_text(block['bulleted_list_item']['rich_text'])}")
        elif block_type == "numbered_list_item":
            lines.append(f"1. {get_text(block['numbered_list_item']['rich_text'])}")
        elif block_type == "paragraph":
            text = get_text(block["paragraph"]["rich_text"])
            if text:
                lines.append(text)
        elif block_type == "divider":
            lines.append("---")

    return "\n\n".join(lines)

def load_all_documents() -> list:
    documents = []
    start_cursor = None

    while True:
        if start_cursor:
            response = notion.databases.query(
                database_id=DATABASE_ID,
                start_cursor=start_cursor
            )
        else:
            response = notion.databases.query(database_id=DATABASE_ID)

        for page in response["results"]:
            try:
                metadata = extract_metadata(page)
                content = extract_content(metadata["page_id"])

                if content.strip():
                    documents.append({
                        "metadata": metadata,
                        "content": content
                    })
            except Exception as e:
                print(f"Error loading page {page['id']}: {e}")
                continue

        if response.get("has_more"):
            start_cursor = response["next_cursor"]
        else:
            break

    return documents

if __name__ == "__main__":
    documents = load_all_documents()
    print(f"Total documents loaded: {len(documents)}")
    print("─" * 50)

    for doc in documents:
        print(f"Document Name: {doc['metadata']['document_name']}")
        print(f"Category: {doc['metadata']['category']}")
        print(f"Type: {doc['metadata']['document_type']}")
        print(f"Industry: {doc['metadata']['industry']}")
        print(f"Content Length: {len(doc['content'])} characters")
        print(f"Content Preview:\n{doc['content'][:300]}")
        print("─" * 50)