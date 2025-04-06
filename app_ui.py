import streamlit as st
import faiss
import json
from sentence_transformers import SentenceTransformer
from recommend import get_recommendations

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load index and metadata
index = faiss.read_index("assessment_index.faiss")
with open("assessment_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Streamlit UI
st.set_page_config(page_title="Assessment Recommender", layout="centered")
st.title("SHL Assessment Recommender")
st.markdown("Type a job description or skillset query below:")

query = st.text_area("Query", height=150)
top_k = st.slider("Number of Recommendations", 1, 10, 5)

if st.button("Recommend"):
    if query.strip():
        with st.spinner("Finding best matches..."):
            results = get_recommendations(query, model, index, metadata, top_k)
        if results:
            st.success(f"Top {len(results)} Results:")
            for res in results:
                st.markdown(f"""
                <div style='padding:10px;margin-bottom:10px;border:1px solid #eee;border-radius:10px;background-color:#f9f9f9; color:black'>
                <strong>Name:</strong> <a href="{res['url']}" target="_blank">{res['name']}</a><br>
                <strong>Remote Testing:</strong> {res['remote_testing']}<br>
                <strong>Adaptive/IRT:</strong> {res['adaptive_irt']}<br>
                <strong>Duration:</strong> {res['duration']} minutes<br>
                <strong>Test Types:</strong> {", ".join(res['test_types'])}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No results found.")
    else:
        st.error("Please enter a query.")
