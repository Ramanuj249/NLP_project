import os
from http.client import responses

from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

model = AzureChatOpenAI(
    api_key = os.getenv("OPEN_API_KEY"),
    deployment_name = os.getenv("DEPLOYMENT_NAME"),
    api_version = os.getenv("API_VERSION"),
    azure_endpoint = os.getenv("AZURE_ENDPOINT"),
    temperature = 0.1
)

# prompt = "how many Moons do earth have?"
# print(model.invoke(prompt))

def generate_llm_response(prompt: str) -> str:
    response = model.invoke(prompt)
    return response.content
