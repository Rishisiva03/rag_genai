import requests
import streamlit as st
import os

FASTAPI_URL = os.getenv("FASTAPI_URL")

st.title("PDF Upload and Processing")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
import streamlit as st
import requests


if uploaded_file:
    if st.button("Upload"):
        with st.spinner("Uploading..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{FASTAPI_URL}/upload/file", files=files)
                response.raise_for_status()
                result = response.json()
                st.session_state["file_path"] = result["file_path"]
                st.session_state["file_uploaded"] = True
                st.success("File uploaded successfully!")
            except requests.exceptions.RequestException as e:
                st.error(f"Upload failed: {e}")

if st.session_state.get("file_uploaded", False):
    st.markdown("---")
    st.subheader("Ask a question about the uploaded PDF")

    question = st.text_input("Enter your question")
    
    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a valid question.")
        else:
            with st.spinner("Getting answer..."):
                try:
                    response = requests.post(
                        f"{FASTAPI_URL}/question",
                        json={
                            "question": question,
                            "file_path": st.session_state["file_path"]
                        }
                    )
                    response.raise_for_status()
                    result_data = response.json()
                    st.success(f"Answer: {result_data['answer']}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Question processing failed: {e}")
