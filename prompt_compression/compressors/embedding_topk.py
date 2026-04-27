import numpy as np
from prompt_compression.utils.models import get_embedder

def embedding_topk_compress(text: str, ratio: float = 0.3) -> str:
    sentences = [s.strip() for s in text.split("。") if s.strip()]
    if len(sentences) <= 1:
        return text

    embedder = get_embedder()
    embeddings = embedder.encode(sentences)

    centroid = embeddings.mean(axis=0)

    scores = np.dot(embeddings, centroid) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(centroid) + 1e-10
    )

    k = max(1, int(len(sentences) * ratio))
    topk_idx = np.argsort(scores)[-k:]

    selected = [sentences[i] for i in sorted(topk_idx)]
    return "。".join(selected) + "。"
