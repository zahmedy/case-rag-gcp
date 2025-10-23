from pathlib import Path
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
import faiss

# New Vertex AI SDK
import vertexai
from vertexai.language_models import TextEmbeddingModel
from vertexai.language_models import TextEmbeddingInput

# ----------------------------
# 1) Initialize GCP Vertex AI
# ----------------------------
vertexai.init(project="just-fire-470409-t5", location="us-central1")

# ----------------------------
# 2) Load embedding model
# ----------------------------
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")

# ----------------------------
# 3) Load & chunk PDFs
# ----------------------------
DATA_DIR = Path("data")
all_chunks = []

def load_pdf_text(file_path):
    """Read text from PDF pages"""
    reader = PdfReader(str(file_path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

for pdf_file in DATA_DIR.glob("*.pdf"):
    text = load_pdf_text(pdf_file)
    chunks = splitter.split_text(text)
    for i, chunk in enumerate(chunks):
        all_chunks.append({
            "source": str(pdf_file),
            "chunk_id": i,
            "text": chunk
        })

print(f"Total chunks created: {len(all_chunks)}")

# ----------------------------
# 4) Generate embeddings
# ----------------------------
texts = [chunk["text"] for chunk in all_chunks]
inputs = [TextEmbeddingInput(text) for text in texts]

embeddings = embedding_model.get_embeddings(inputs)
embedding_vectors = [emb.values for emb in embeddings]

print("Embeddings generated:", len(embedding_vectors), "vectors")

# ----------------------------
# 5) Build FAISS index
# ----------------------------
emb_array = np.array(embedding_vectors, dtype="float32")
dim = emb_array.shape[1]
index = faiss.IndexFlatIP(dim)  # IP = inner product for cosine similarity
faiss.normalize_L2(emb_array)
index.add(emb_array)

print("FAISS index created with", index.ntotal, "vectors")

import pickle

# Save FAISS index
faiss.write_index(index, "faiss.index")

# Save chunks metadata
with open("chunks.pkl", "wb") as f:
    pickle.dump(all_chunks, f)

print("Saved FAISS index and chunks metadata.")
