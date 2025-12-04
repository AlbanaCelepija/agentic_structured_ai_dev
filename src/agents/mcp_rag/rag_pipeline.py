import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama

class RAGPipeline:
    def __init__(self, index_path="vector_store.faiss"):
        self.index_path = index_path
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Load FAISS index
        self.index = faiss.read_index(index_path)

        # Load documents metadata
        with open("documents/doc_list.txt") as f:
            self.documents = [line.strip() for line in f]

    def embed(self, text: str):
        return np.array([self.model.encode(text)], dtype="float32")

    def retrieve(self, query: str, k=5):
        vec = self.embed(query)
        scores, ids = self.index.search(vec, k)
        docs = [self.documents[i] for i in ids[0]]
        return docs

    def generate(self, query: str, context_docs):
        prompt = f"""
You are a helpful assistant. Use ONLY the context provided.

Question: {query}

Context:
{chr(10).join(context_docs)}

Answer:
"""
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]

    def run_rag(self, query: str):
        docs = self.retrieve(query)
        answer = self.generate(query, docs)
        return {"answer": answer, "docs": docs}

