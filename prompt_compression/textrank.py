import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from prompt_compression.utils.models import get_embedder

def textrank_compress(text: str, ratio: float = 0.3) -> str:
    sentences = [s.strip() for s in text.split("。") if s.strip()]
    if len(sentences) <= 1:
        return text

    embedder = get_embedder()
    embeddings = embedder.encode(sentences)

    sim_matrix = cosine_similarity(embeddings)
    scores = sim_matrix.sum(axis=1)

    k = max(1, int(len(sentences) * ratio))
    topk_idx = np.argsort(scores)[-k:]

    selected = [sentences[i] for i in sorted(topk_idx)]
    return "。".join(selected) + "。"
