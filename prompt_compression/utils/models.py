from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

_embedder = None
_tokenizer = None
_llm_tok = None
_llm_mdl = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _embedder

def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')
    return _tokenizer

def token_len(text: str) -> int:
    return len(get_tokenizer().encode(text))

def call_llm(prompt: str) -> str:
    import torch
    global _llm_tok, _llm_mdl
    if _llm_mdl is None:
        _llm_tok = AutoTokenizer.from_pretrained('google/flan-t5-base')
        _llm_mdl = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base')
    inputs = _llm_tok(prompt, return_tensors='pt', truncation=True, max_length=512)
    with torch.no_grad():
        outputs = _llm_mdl.generate(**inputs, max_new_tokens=128)
    return _llm_tok.decode(outputs[0], skip_special_tokens=True)
