import redis, json, time, numpy as np
from prompt_compression.utils.models import get_embedder

r=redis.Redis(host='localhost',port=6379,decode_responses=True)

def save_cache(prompt, response, emb, method):
    key=f'cache:{int(time.time()*1000)}'
    r.set(key, json.dumps({
        'prompt':prompt,'response':response,
        'embedding':emb.tolist(),'method':method
    }), ex=3600)

def search_cache(prompt, threshold=0.5):
    emb=get_embedder().encode(prompt)
    best=0;res=None
    for k in r.keys('cache:*'):
        d=json.loads(r.get(k))
        e=np.array(d['embedding'])
        s=float(np.dot(emb,e)/(np.linalg.norm(emb)*np.linalg.norm(e)+1e-10))
        if s>best: best=s;res=d['response']
    return res if best>=threshold else None
