from .base import BaseCompressor

class SelectiveContextCompressor(BaseCompressor):
    def __init__(self, model_type='gpt2'):
        self.model_type=model_type
        self._sc=None

    def _get(self):
        if self._sc is None:
            from selective_context import SelectiveContext
            self._sc=SelectiveContext(model_type=self.model_type)
        return self._sc

    @property
    def name(self): return 'SelectiveContext'

    def _compress(self, text, ratio):
        c,_=self._get()(text, reduce_ratio=ratio)
        return c
