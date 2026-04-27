from fastapi import FastAPI
from pydantic import BaseModel
from prompt_compression.pipeline.smart_llm import smart_llm

app = FastAPI(title="Prompt Compression API")

class Request(BaseModel):
    prompt: str
    ratio: float = 0.3

@app.post("/compress")
def compress(req: Request):
    result = smart_llm(req.prompt, compression_ratio=req.ratio)

    return {
        "response": result["response"],
        "best_method": result["best_method"],
        "cache_hit": result["cache_hit"],
    }
