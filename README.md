# case-rag-gcp

Lightweight Retrieval-Augmented Generation (RAG) pipeline for case documents, built for deployment on Google Cloud Platform (GCP).

## Overview
Provides tools to:
- Ingest and index case documents (PDF / text).
- Create embeddings and store them in a vector store.
- Serve a retrieval + generation endpoint for question answering over case content.
- Deploy to GCP (Cloud Storage + Cloud Run / Vertex AI).

## Key features
- Pluggable embedding provider (local / OpenAI / Vertex AI).
- Pluggable vector store (FAISS / Pinecone / Vertex Matching Engine).
- Document preprocessing, chunking, and metadata preservation.
- Simple REST API for querying (examples use FastAPI).

## Repo layout (suggested)
- README.md
- requirements.txt
- Dockerfile
- src/
    - app/            # API and orchestration
    - ingest.py       # ingestion and indexing scripts
    - embeddings.py   # embedding provider interfaces
    - vectorstore.py  # vector store interfaces
    - utils.py
- scripts/
    - ingest.sh
    - deploy.sh
- tests/

## Quickstart (local)
1. Clone:
     git clone <repo-url>
     cd case-rag-gcp

2. Install:
     python -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt

3. Configure environment (example):
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/creds.json"
     export EMBEDDING_API_KEY="sk-..."
     export VECTOR_STORE="faiss"   # or pinecone | vertex
     export BUCKET_NAME="case-rag-bucket"
     export PROJECT_ID="my-gcp-project"
     export REGION="us-central1"

4. Ingest documents:
     python src/ingest.py --source ./data/cases --chunk-size 1000

5. Run API:
     uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

6. Query:
     curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"question":"What were the damages in case X?"}'

## GCP deployment (high-level)
- Storage: upload raw documents to Cloud Storage.
- Credentials: set GOOGLE_APPLICATION_CREDENTIALS using a service account with Cloud Storage & Secret Manager access.
- Vector store options:
    - FAISS: run inside Cloud Run (local disk persistence ephemeral — consider Cloud Filestore for persistence).
    - Vertex Matching Engine: managed vector search on GCP.
    - Pinecone: external managed vector DB.
- Build and deploy to Cloud Run:
    gcloud builds submit --tag gcr.io/$PROJECT_ID/case-rag-gcp
    gcloud run deploy case-rag-gcp --image gcr.io/$PROJECT_ID/case-rag-gcp --region $REGION --platform managed --allow-unauthenticated

- Secrets: store API keys in Secret Manager and mount or fetch at container startup.

## Configuration
Keep sensitive values out of source. Recommended env vars:
- GOOGLE_APPLICATION_CREDENTIALS
- EMBEDDING_API_KEY
- VECTOR_STORE
- BUCKET_NAME
- PROJECT_ID
- REGION
- PORT
