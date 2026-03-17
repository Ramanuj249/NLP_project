import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")

MAX_TOKENS = 500
MIN_TOKENS = 50

def count_tokens(text: str) -> int:
    return len(encoder.encode(text))

def split_by_tokens(text: str) -> list:
    tokens = encoder.encode(text)
    chunks = []
    for i in range(0, len(tokens), MAX_TOKENS):
        chunk_tokens = tokens[i:i + MAX_TOKENS]
        chunks.append(encoder.decode(chunk_tokens))
    return chunks

def chunk_document(document: dict) -> list:
    content = document["content"]
    metadata = document["metadata"]

    # Step 1 - split by --- divider
    raw_chunks = [c.strip() for c in content.split("---") if c.strip()]

    # Step 2 - handle size
    refined_chunks = []
    for chunk in raw_chunks:
        token_count = count_tokens(chunk)

        if token_count > MAX_TOKENS:
            sub_chunks = split_by_tokens(chunk)
            refined_chunks.extend(sub_chunks)
        elif token_count < MIN_TOKENS:
            if refined_chunks:
                refined_chunks[-1] += " " + chunk
            else:
                refined_chunks.append(chunk)
        else:
            refined_chunks.append(chunk)

    # Step 3 - attach metadata to every chunk
    final_chunks = []
    for i, chunk in enumerate(refined_chunks):
        final_chunks.append({
            "text": chunk,
            "metadata": {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(refined_chunks)
            }
        })

    return final_chunks

def chunk_all_documents(documents: list) -> list:
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
    return all_chunks

if __name__ == "__main__":
    from notions_loader import load_all_documents

    documents = load_all_documents()
    chunks = chunk_all_documents(documents)

    print(f"Total documents: {len(documents)}")
    print(f"Total chunks: {len(chunks)}")
    print("─" * 50)
    print(f"Sample chunk text:\n{chunks[0]['text'][:300]}")
    print("─" * 50)
    print(f"Sample chunk metadata:\n{chunks[0]['metadata']}")