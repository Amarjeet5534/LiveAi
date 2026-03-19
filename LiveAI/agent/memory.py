import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

MEMORY_DIR = "data/memory"
INDEX_FILE = os.path.join(MEMORY_DIR, "memory.index")
TEXT_FILE = os.path.join(MEMORY_DIR, "memory.pkl")

os.makedirs(MEMORY_DIR, exist_ok=True)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384

# Load or create index
if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
    with open(TEXT_FILE, "rb") as f:
        memory_texts = pickle.load(f)
else:
    index = faiss.IndexFlatL2(dimension)
    memory_texts = []


def save_memory(text):
    global memory_texts

    embedding = embedding_model.encode([text])
    index.add(np.array(embedding).astype("float32"))

    memory_texts.append(text)

    faiss.write_index(index, INDEX_FILE)
    with open(TEXT_FILE, "wb") as f:
        pickle.dump(memory_texts, f)


def retrieve_memory(query, k=3):
    if len(memory_texts) == 0:
        return ""

    embedding = embedding_model.encode([query])
    D, I = index.search(np.array(embedding).astype("float32"), k)

    results = []
    for idx in I[0]:
        if idx < len(memory_texts):
            results.append(memory_texts[idx])

    return "\n".join(results)
