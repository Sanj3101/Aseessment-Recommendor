from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
import uvicorn

# Load model and index
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("assessment_index.faiss")
with open("assessment_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

app = FastAPI(title="SHL Assessment Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_recommendations(query, top_k=10):
    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding).astype("float32"), top_k)
    results = []
    for idx in I[0]:
        item = metadata[idx]
        results.append({
            "name": item["name"],
            "url": item["url"],
            "remote_testing": item["remote_testing"],
            "adaptive_irt": item["adaptive_irt"],
            "duration": item["duration"],
            "test_types": item["test_types"]
        })
    return results

@app.get("/recommend")
def recommend(query: str = Query(..., description="Query text for recommendation"), top_k: int = 10):
    results = get_recommendations(query, top_k)
    return {"results": results}
