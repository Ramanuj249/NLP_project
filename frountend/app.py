# import streamlit as st
# import requests
#
# BACKEND_URL = "http://localhost:8000"
#
# st.title("Documentation Generator")
#
# # Get categories
# categories = requests.get(f"{BACKEND_URL}/categories").json()
# doc_types = requests.get(f"{BACKEND_URL}/document-types").json()
#
# # Convert to dropdown-friendly format
# category_map = {c["category_name"]: c["id"] for c in categories}
# doc_type_map = {d["document_type_name"]: d["id"] for d in doc_types}
#
#
# selected_category = st.selectbox("Select Category", category_map.keys())
# selected_doc_type = st.selectbox("Select Document Type", doc_type_map.keys())
#
# if st.button("Get Documents"):
#     params = {
#         "category_id": category_map[selected_category],
#         "document_type_id": doc_type_map[selected_doc_type]
#     }
#
#     res = requests.get(f"{BACKEND_URL}/documents", params=params)
#     documents = res.json()
#
#     if documents:
#         for doc in documents:
#             st.write("📄", doc["title"])
#     else:
#         st.warning("No documents found")





########
# st.title("My First App")
#
# if st.button("Get Data"):
#     res = requests.get("http://localhost:8000/")
#     st.json(res.json())



import streamlit as st
import pandas as pd

st.title("Interactive Streamlit Demo")

st.header("1️⃣ Single Choice Question")
single_choice = st.radio(
    "Choose your favorite fruit:",
    ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
)
st.write("You selected:", single_choice)

st.header("2️⃣ Multiple Choice Question")
multi_choice = st.multiselect(
    "Select your favorite colors:",
    ["Red", "Blue", "Green", "Yellow", "Purple"]
)
st.write("You selected:", multi_choice)

st.header("3️⃣ Short Answer")
short_answer = st.text_input("Write a short answer (one line):")
st.write("You wrote:", short_answer)

st.header("4️⃣ Paragraph Answer")
paragraph_answer = st.text_area("Write a paragraph answer:")
st.write("You wrote:", paragraph_answer)

st.header("5️⃣ Yes / No Question")
yes_no = st.selectbox("Do you like programming?", ["Yes", "No"])
yes_no_bool = True if yes_no == "Yes" else False
st.write("Saved as boolean:", yes_no_bool)

st.header("6️⃣ Table Input")
# Default table
if 'table_data' not in st.session_state:
    st.session_state.table_data = pd.DataFrame(columns=["Name", "Age", "City", "Occupation"])

# Display table
st.write("Current Table:")
st.dataframe(st.session_state.table_data)

# Add a new row
with st.form("add_row_form"):
    st.subheader("Add a New Row")
    name = st.text_input("Name")
    age = st.text_input("Age")
    city = st.text_input("City")
    occupation = st.text_input("Occupation")
    if st.form_submit_button("Add Row"):
        new_row = {"Name": name, "Age": age, "City": city, "Occupation": occupation}
        st.session_state.table_data = pd.concat([st.session_state.table_data, pd.DataFrame([new_row])], ignore_index=True)

# Add new column
with st.form("add_column_form"):
    st.subheader("Add a New Column")
    new_column_name = st.text_input("Column Name")
    default_value = st.text_input("Default Value")
    if st.form_submit_button("Add Column") and new_column_name:
        st.session_state.table_data[new_column_name] = default_value

st.write("Updated Table:")
st.dataframe(st.session_state.table_data)
