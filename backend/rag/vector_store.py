import os
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

from pymilvus import MilvusClient, DataType

MILVUS_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag_documents.db")
COLLECTION_NAME = "document_chunks"
VECTOR_DIM = 3072

def get_client():
    return MilvusClient(MILVUS_DB)

def create_collection():
    client = get_client()
    print(f"CREATE COLLECTION — DB Path: {MILVUS_DB}")
    if client.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        return

    schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=True)
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
    schema.add_field(field_name="page_id", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="document_name", datatype=DataType.VARCHAR, max_length=512)
    schema.add_field(field_name="document_type", datatype=DataType.VARCHAR, max_length=100)
    schema.add_field(field_name="category", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="industry", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="author", datatype=DataType.VARCHAR, max_length=256)
    schema.add_field(field_name="created_date", datatype=DataType.VARCHAR, max_length=100)
    schema.add_field(field_name="chunk_index", datatype=DataType.INT64)
    schema.add_field(field_name="total_chunks", datatype=DataType.INT64)

    index_params = MilvusClient.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="AUTOINDEX",
        metric_type="COSINE"
    )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        schema=schema,
        index_params=index_params
    )
    print(f"Collection '{COLLECTION_NAME}' created successfully.")


def insert_chunks(embedded_chunks: list):
    client = get_client()
    print(f"INSERT CHUNKS — DB Path: {MILVUS_DB}")
    data = []
    for i, chunk in enumerate(embedded_chunks):
        data.append({
            "id": i + 1,
            "vector": chunk["vector"],
            "text": chunk["text"],
            "page_id": chunk["metadata"].get("page_id", ""),
            "document_name": chunk["metadata"].get("document_name", ""),
            "document_type": chunk["metadata"].get("document_type", ""),
            "category": chunk["metadata"].get("category", ""),
            "industry": chunk["metadata"].get("industry", ""),
            "author": chunk["metadata"].get("author", ""),
            "created_date": chunk["metadata"].get("created_date", ""),
            "chunk_index": int(chunk["metadata"].get("chunk_index", 0)),
            "total_chunks": int(chunk["metadata"].get("total_chunks", 0))
        })
    print(f"Sample chunk keys: {list(data[0].keys())}")
    client.insert(collection_name=COLLECTION_NAME, data=data)
    print(f"Inserted {len(data)} chunks into Milvus.")

def search_chunk(query_vector: list, top_k: int = 5, filters: dict = None) -> list:
    client = get_client()
    filter_expr = None
    if filters:
        conditions = []
        if filters.get("document_type"):
            conditions.append(f'document_type == "{filters["document_type"]}"')
        if filters.get("category"):
            conditions.append(f'category == "{filters["category"]}"')
        if filters.get("industry"):
            conditions.append(f'industry == "{filters["industry"]}"')
        if filters.get("document_name_exact"):
            conditions.append(f'document_name == "{filters["document_name_exact"]}"')
        if conditions:
            filter_expr = " && ".join(conditions)
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        limit=top_k,
        filter=filter_expr,
        output_fields=[
            "text", "page_id", "document_name",
            "document_type", "category", "industry",
            "author", "created_date", "chunk_index"
        ]
    )
    chunks = []
    for hit in results[0]:
        chunks.append({
            "text": hit["entity"]["text"],
            "score": hit["distance"],
            "metadata": {
                "page_id": hit["entity"]["page_id"],
                "document_name": hit["entity"]["document_name"],
                "document_type": hit["entity"]["document_type"],
                "category": hit["entity"]["category"],
                "industry": hit["entity"]["industry"],
                "author": hit["entity"]["author"],
                "created_date": hit["entity"]["created_date"],
                "chunk_index": hit["entity"]["chunk_index"]
            }
        })
    return chunks

def drop_collection():
    client = get_client()
    if client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' dropped.")
    else:
        print(f"Collection '{COLLECTION_NAME}' does not exist.")


def inspect_collection():
    client = get_client()
    print(f"DB Path: {MILVUS_DB}")
    print(f"Collections available: {client.list_collections()}")

    if not client.has_collection(COLLECTION_NAME):
        print("Collection does not exist.")
        return

    # Get total count
    stats = client.get_collection_stats(COLLECTION_NAME)
    print(f"Total chunks stored: {stats['row_count']}")
    print("─" * 50)

    # Get sample records
    results = client.query(
        collection_name=COLLECTION_NAME,
        filter="chunk_index >= 0",
        output_fields=[
            "id", "text", "document_name",
            "document_type", "category",
            "chunk_index", "total_chunks",
            "vector"
        ],
        limit=5
    )

    print(f"Sample chunks (showing first 5):")
    print("─" * 50)
    for r in results:
        print(f"ID: {r['id']}")
        print(f"Document: {r['document_name']}")
        print(f"Type: {r['document_type']}")
        print(f"Category: {r['category']}")
        print(f"Chunk: {r['chunk_index']} of {r['total_chunks']}")
        print(f"Text preview: {r['text'][:150]}")
        print(f"Vector exists: {r['vector'] is not None}")
        print(f"Vector dimensions: {len(r['vector'])}")
        print("─" * 50)


if __name__ == "__main__":
    inspect_collection()