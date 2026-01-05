import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Route adapters (we already patched these)
from server.app.adapters import recommend as rec_fn, search as search_fn, summarize as sum_fn, trending as trending_fn
from server.app.schemas import (
    RecommendRequest, RecommendResponse, RecItem,
    SearchQuery, SummarizeRequest
)

def _origins_from_env():
    raw = os.getenv("CORS_ORIGINS", "")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins or ["*"]

app = FastAPI(title="Smart News Recommender API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/trending", response_model=list[RecItem])
def trending(k: int = 10):
    try:
        items = trending_fn(k=k)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    try:
        items = rec_fn(
            user_id=req.user_id,
            k=req.k,
            recent_clicks=req.recent_clicks,
            locale=req.locale,
            algorithm=req.algorithm,
        )
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=list[RecItem])
def search(q: SearchQuery):
    try:
        return search_fn(q=q.q, k=q.k, category=q.category)
    except Exception as e:
        import traceback
        print("SEARCH ERROR:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
def summarize(req: SummarizeRequest):
    try:
        return sum_fn(title=req.title, abstract=req.abstract, max_tokens=req.max_tokens)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
