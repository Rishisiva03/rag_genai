# GenAI PDF Question Answering API

This repository provides a FastAPI backend and Streamlit frontend for uploading PDF files, storing them locally or on AWS S3, and asking questions about their content using OpenAI's GPT models and semantic search with FAISS.

## Features

- **PDF Upload**: Upload PDF files via API or frontend. Files are stored locally or on S3, as configured.
- **Semantic Search**: Extracts text from PDFs, splits into chunks, embeds with Sentence Transformers, and builds a FAISS index for semantic retrieval.
- **Question Answering**: Uses OpenAI GPT models to answer questions based on retrieved document context.
- **Frontend**: Streamlit app for easy file upload and question interaction.
- **Docker Support**: Ready for containerization and deployment.
- **CI/CD**: GitHub Actions workflows for building and deploying Docker images.

## Directory Structure

- `main.py`: FastAPI app entrypoint.
- `app/`
  - `config.py`: Configuration for upload paths and metadata.
  - `models/model_wrapper.py`: Core logic for PDF processing, embedding, and LLM interaction.
  - `routes/`: FastAPI routes for file upload and question processing.
- `frontend/main.py`: Streamlit frontend for user interaction.
- `deployment/DockerFile`: Dockerfile for backend API.
- `.env`: Environment variables (API keys, S3 config, etc.).
- `.github/workflows/`: CI/CD pipelines.
- `requirements.txt`: Python dependencies.

## Setup for local

1. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```

2. **Configure environment**  
   Copy `.env` and set your OpenAI and AWS credentials.

3. **Run backend**  
   ```sh
   uvicorn main:app --reload
   ```

4. **Run frontend**  
   ```sh
   streamlit run frontend/main.py
   ```

5. **Docker**  
   Build and run using the provided Dockerfile.

## API Endpoints

- `POST /upload/file`: Upload a PDF file.
- `POST /question`: Ask a question about an uploaded PDF.

## Environment Variables

See [.env](.env) for required variables:
- `OPENAI_API_KEY`
- `UPLOAD_FOLDER_PATH`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `FASTAPI_URL`

