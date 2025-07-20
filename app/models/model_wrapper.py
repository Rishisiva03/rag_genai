from io import BytesIO
import os
import fitz
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from openai import OpenAI

import os
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

import boto3
from botocore.config import Config

def read_s3_file_to_bytes(s3_path: str, bucket_name: str,
                         access_key: str, secret_key: str, region: str) -> bytes:
    boto_config = Config(signature_version='s3v4')

    session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    s3 = session.client("s3", config=boto_config)

    response = s3.get_object(Bucket=bucket_name, Key=s3_path)
    data = response['Body'].read()  # bytes

    return data


class QuestionModelWrapper:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(
            api_key=self.openai_api_key)
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def extract_text_from_pdf(self, file_path):
        if not file_path.startswith("s3://"):
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        else:
            boto_config = Config(signature_version='s3v4')
            session = boto3.session.Session(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name="ap-south-1"
            )
            s3 = session.client("s3", config=boto_config)

            response = s3.get_object(Bucket=file_path.split('/')[2], Key='/'.join(file_path.split('/')[3:]))
            pdf_bytes = response['Body'].read()

            pdf_stream = BytesIO(pdf_bytes)

            doc = fitz.open(stream=pdf_stream, filetype="pdf")

            text = ""
            for page in doc:
                text += page.get_text()

            return text
    
    def split_text(self, text, chunk_size=500, overlap=100):
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
        return chunks
    
    def embed_text(self, chunks):
        return self.model.encode(chunks, convert_to_numpy=True)

    def build_faiss_index(self, embeddings):
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        return index

    def search_index(self, index, question_embedding, k=4): 
        _, indices = index.search(np.array([question_embedding]), k)
        return indices[0]

    def ask_llm(self, context, question):
        prompt = f"""You are an assistant that answers based only on the following document content.

                Context:
                {context}

                Question:
                {question}

                Answer:"""

        response = openai.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
        )
        return response.choices[0].message.content.strip()
    
    def process_pdf(self, file_path, question):
        text = self.extract_text_from_pdf(file_path)
        chunks = self.split_text(text)
        embeddings = self.embed_text(chunks)
        index = self.build_faiss_index(embeddings)

        question_embedding = self.embed_text([question])[0]
        indices = self.search_index(index, question_embedding)

        context = "\n".join([chunks[i] for i in indices])
        answer = self.ask_llm(context, question)
        
        return answer
    
