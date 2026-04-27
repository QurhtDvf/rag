import redis
import json
import time
import numpy as np
from prompt_compression.utils.models import get_embedder

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def save_cache(prompt, response, emb, method):
    key = f'cache:{int(time.time()*1000)}'
    r.set(
        key,
        json.dumps({
            'prompt': prompt,
            'response': response,
            'embedding': emb.tolist(),
            'method': method
        }),
        ex=3600
    )

def search_cache(prompt, threshold=0.5):
    query_emb = get_embedder().encode(prompt)

    best_score = 0.0
    best_res = None

    for key in r.keys('cache:*'):
        raw = r.get(key)
        if not raw:
            continue

        data = json.loads(raw)
        emb = np.array(data['embedding'])

        sim = float(
            np.dot(query_emb, emb) /
            (np.linalg.norm(query_emb) * np.linalg.norm(emb) + 1e-10)
        )

        if sim > best_score:
            best_score = sim
            best_res = data['response']

    if best_score >= threshold:
        return best_res

    return None
