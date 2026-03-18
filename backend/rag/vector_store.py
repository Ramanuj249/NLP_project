import os
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

from pymilvus import MilvusClient, DataType

MILVUS_DB = "./rag_documents.db"
COLLECTION_NAME = "document_chunks"
VECTOR_DIM = 3072

def get_client():
    return MilvusClient(MILVUS_DB)

def create_collection():
    client = get_client()
    if client.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        return

    schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=True)
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
    data = []
    for chunk in embedded_chunks:
        data.append({
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

if __name__ == "__main__":
    try:
        create_collection()
        print("Collection ready!")
        client = get_client()
        print("Collections in DB:", client.list_collections())
    except Exception as e:
        print(f"Error: {e}")