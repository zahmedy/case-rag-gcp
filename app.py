import faiss
import pickle
import numpy as np
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from vertexai.generative_models import GenerativeModel

vertexai.init(project="just-fire-470409-t5", location="us-central1")
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")
llm = GenerativeModel("gemini-2.0-flash-001")

index = faiss.read_index("faiss.index")
with open("chunks.pkl", "rb") as f:
    all_chunks = pickle.load(f)

def answer_question(query, top_k=5, return_chunks=False):
    # Embed query
    query_vector = embedding_model.get_embeddings([query])[0].values
    query_vector = np.array([query_vector], dtype="float32")
    faiss.normalize_L2(query_vector)
    
    # Retrieve top K
    D, I = index.search(query_vector, top_k)
    retrieved_chunks = [all_chunks[idx]['text'] for idx in I[0]]
    
    # Build prompt
    context = "\n\n".join(retrieved_chunks)
    prompt = f"Use only this context:\n{context}\nQuestion: {query}\nAnswer:"
    
    # Generate answer
    answer = llm.generate_content(prompt).text
    
    if return_chunks:
        return answer, retrieved_chunks
    return answer

#===============
# Web App 
#===============
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")
    answer = answer_question(question)  # assume you defined this function
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)