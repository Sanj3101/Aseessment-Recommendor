import numpy as np

def get_recommendations(query, model, index, metadata, top_k=10):
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
