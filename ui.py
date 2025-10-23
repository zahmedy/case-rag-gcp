import requests
import streamlit as st

BACKEND_URL = "http://localhost:5001/ask"

st.title("RAG Document Q&A")
question = st.text_input("Ask your docs something:")

if st.button("Get Answer") and question:
    try:
        response = requests.post(BACKEND_URL, json={"question": question})
        if response.ok:
            st.write(response.json().get("answer"))
        else:
            st.error("Backend returned an error")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
