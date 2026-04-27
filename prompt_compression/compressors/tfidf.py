import re, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .base import BaseCompressor

class TFIDFCompressor(BaseCompressor):
    @property
    def name(self): return 'TF-IDF'

    def _compress(self, text, ratio):
        s = [x.strip() for x in re.split(r'[。.!?\n]', text) if x.strip()]
        if len(s)<=1:
            w=text.split()
            return ' '.join(w[:max(1,int(len(w)*(1-ratio)))])
        k=max(1,int(len(s)*(1-ratio)))
        vec=TfidfVectorizer()
        m=vec.fit_transform(s)
        sc=m.sum(axis=1).A1
        idx=sorted(np.argsort(sc)[-k:].tolist())
        return '。'.join([s[i] for i in idx])
