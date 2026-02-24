import pandas as pd
from backend.database import  get_connection
import sys

# Read CSV file
df = pd.read_csv("/home/shivam/PycharmProjects/NLP_project/data/document_question.csv")

unique_documents = df["document_id"].unique()

conn = get_connection()
cursor = conn.cursor()

doc_id_map = {}

# ---- For each unique document name, get its ID ----
for doc_name in unique_documents:
    cursor.execute(
        "SELECT id FROM documents WHERE title = %s",
        (doc_name,)
    )
    result = cursor.fetchone()
    if result is None:
        print(f"❌ ERROR: Document not found in DB: {doc_name}")
        cursor.close()
        conn.close()
        sys.exit(1)
    doc_id_map[doc_name] = result[0]

cursor.close()
conn.close()

# ---- Quick check ----
print("✅ Document mapping created successfully:")
for k, v in list(doc_id_map.items())[:5]:  # show first 5 for brevity
    print(f"{k} → {v}")


# ---- Reconnect to DB for insertion ----
conn = get_connection()
cursor = conn.cursor()

insert_query = """
INSERT INTO questions (document_id, question, type, options)
VALUES (%s, %s, %s, %s)
"""

# ---- Loop over all rows in the DataFrame ----
for _, row in df.iterrows():
    cursor.execute(
        insert_query,
        (
            doc_id_map[row["document_id"]],        # get ID from mapping
            row["question"],                       # question text
            row["type"],                           # question type
            row["options"] if pd.notna(row["options"]) else None  # options
        )
    )

# ---- Commit all inserts ----
conn.commit()
cursor.close()
conn.close()

print("✅ All questions inserted successfully.")
