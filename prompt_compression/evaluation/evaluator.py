import numpy as np
from dataclasses import dataclass
from rouge_score import rouge_scorer
from prompt_compression.utils.models import get_embedder

@dataclass
class EvalResult:
    method:str
    score:float

class CompressionEvaluator:
    def __init__(self):
        self.rouge=rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False)

    def evaluate(self, comp):
        r=self.rouge.score(comp.original, comp.compressed)['rougeL'].fmeasure
        emb=get_embedder()
        o=emb.encode(comp.original)
        c=emb.encode(comp.compressed)
        sim=float(np.dot(o,c)/(np.linalg.norm(o)*np.linalg.norm(c)+1e-10))
        score=0.6*sim+0.4*r
        return EvalResult(comp.method, score), comp
