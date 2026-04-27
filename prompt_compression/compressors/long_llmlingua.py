from .base import BaseCompressor

class LongLLMLinguaCompressor(BaseCompressor):
    def __init__(self, model_name='microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank'):
        self.model_name=model_name
        self._c=None

    def _get(self):
        if self._c is None:
            from llmlingua import PromptCompressor
            self._c=PromptCompressor(model_name=self.model_name)
        return self._c

    @property
    def name(self): return 'LongLLMLingua'

    def _compress(self, text, ratio):
        r=self._get().compress_prompt(text, rate=1-ratio, rank_method='longllmlingua')
        return r['compressed_prompt']
