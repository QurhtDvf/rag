import numpy as np
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from .base import BaseCompressor

class AttentionPruningCompressor(BaseCompressor):
    def __init__(self, model_name='google/flan-t5-base'):
        self.model_name=model_name
        self._tok=None
        self._mdl=None

    def _get(self):
        if self._mdl is None:
            self._tok=AutoTokenizer.from_pretrained(self.model_name)
            self._mdl=AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        return self._tok,self._mdl

    @property
    def name(self): return 'AttentionPruning'

    def _compress(self, text, ratio):
        import torch
        tok,mdl=self._get()
        inp=tok(text, return_tensors='pt', truncation=True, max_length=512)
        with torch.no_grad():
            out=mdl.encoder(**inp, output_attentions=True)
        att=torch.stack(out.attentions).mean(dim=[0,1,2])
        sc=att.sum(dim=0).numpy()
        ids=inp['input_ids'][0].tolist()
        k=max(1,int(len(ids)*(1-ratio)))
        idx=sorted(np.argsort(sc)[-k:].tolist())
        return tok.decode([ids[i] for i in idx], skip_special_tokens=True)
