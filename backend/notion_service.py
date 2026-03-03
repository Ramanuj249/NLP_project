import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

