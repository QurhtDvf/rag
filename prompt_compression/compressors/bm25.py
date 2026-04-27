import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def bm25_like_compress(text: str, ratio: float = 0.3) -> str:
    sentences = [s.strip() for s in text.split("。") if s.strip()]
    if len(sentences) <= 1:
        return text

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(sentences)

    scores = tfidf.sum(axis=1).A1  # BM25簡略版

    k = max(1, int(len(sentences) * ratio))
    topk_idx = np.argsort(scores)[-k:]

    selected = [sentences[i] for i in sorted(topk_idx)]
    return "。".join(selected) + "。"
