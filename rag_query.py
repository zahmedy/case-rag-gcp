import numpy as np
import faiss
import pickle
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.language_models import TextEmbeddingModel

# ---------------------------
# 1) Init Vertex AI
# ---------------------------
vertexai.init(project="just-fire-470409-t5", location="us-central1")

embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")
llm = GenerativeModel("gemini-2.0-flash-001")  # Fast, cheaper than Pro

# ---------------------------
# 2) Load FAISS + chunks
# ---------------------------
index = faiss.read_index("faiss.index")
with open("chunks.pkl", "rb") as f:
    all_chunks = pickle.load(f)

# ---------------------------
# 3) Ask a question
# ---------------------------
query_text = "Who is the applicant in this application?"

# Embed the query
query_vector = embedding_model.get_embeddings([query_text])[0].values
query_vector = np.array([query_vector], dtype="float32")
faiss.normalize_L2(query_vector)

# Retrieve top 3 chunks
D, I = index.search(query_vector, 10)

retrieved_chunks = [all_chunks[idx]['text'] for idx in I[0]]

# ---------------------------
# 4) Build prompt for LLM
# ---------------------------
context = "\n\n".join(retrieved_chunks)
prompt = f"""
You are a helpful assistant. Use ONLY the following context from visa application to answer the question.

Context:
{context}

Question: {query_text}
"""

# ---------------------------
# 5) Generate response
# ---------------------------
response = llm.generate_content(prompt)
print("\n=== Answer ===")
print(response.text)
