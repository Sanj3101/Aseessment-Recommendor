import pandas as pd
import faiss
import json
import numpy as np
import ast
from sentence_transformers import SentenceTransformer

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can try other models too

# Define column headers
column_names = ["name", "url", "remote_testing", "adaptive_irt", "test_types", "duration"]
df = pd.read_csv("duration.csv", names=column_names, header=None)

# Safely parse test_types
def safe_parse_list(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else []
    except:
        return []

df["test_types"] = df["test_types"].apply(safe_parse_list)

# Convert each row to a string
def row_to_text(row):
    return (
        f"{row['name']} - Test Types: {', '.join(row['test_types'])}, "
        f"Remote Testing: {row['remote_testing']}, Adaptive/IRT: {row['adaptive_irt']}, "
        f"Duration: {row['duration']}"
    )

texts = df.apply(row_to_text, axis=1).tolist()

# Get embeddings
print("Generating embeddings using SentenceTransformer...")
embeddings = model.encode(texts, show_progress_bar=True)

# Create FAISS index
embedding_dim = embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_dim)
index.add(np.array(embeddings).astype("float32"))

# Save FAISS index
faiss.write_index(index, "assessment_index.faiss")

# Save metadata
with open("assessment_metadata.json", "w", encoding="utf-8") as f:
    json.dump(df.to_dict(orient="records"), f, indent=2)

print("Local embeddings + index + metadata saved!")
