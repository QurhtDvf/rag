from prompt_compression.compressors import get_compressor, REGISTRY
from prompt_compression.evaluation.evaluator import CompressionEvaluator
from prompt_compression.cache.semantic_cache import search_cache, save_cache
from prompt_compression.utils.models import get_embedder, call_llm


def smart_llm(prompt, ratio=0.3):
    cached=search_cache(prompt)
    if cached: return cached

    ev=CompressionEvaluator()
    results=[]
    for name in REGISTRY:
        comp=get_compressor(name).compress(prompt, ratio)
        er,_=ev.evaluate(comp)
        results.append((er.score, comp))
    results.sort(reverse=True)
    best=results[0][1]

    out=call_llm(best.compressed)
    emb=get_embedder().encode(prompt)
    save_cache(prompt,out,emb,best.method)
    return out
