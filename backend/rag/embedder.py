import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPEN_API_KEY"),
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING_DEPLOYMENT_NAME")


def embed_text(text: str) -> list:
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding


def embed_chunks(chunks: list) -> list:
    embedded = []
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        print(f"Embedding chunk {i+1} of {total}...")
        vector = embed_text(chunk["text"])
        embedded.append({
            "text": chunk["text"],
            "vector": vector,
            "metadata": chunk["metadata"]
        })
    return embedded



if __name__ == "__main__":
    test_text = "This is a test chunk for embedding."
    vector = embed_text(test_text)
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")