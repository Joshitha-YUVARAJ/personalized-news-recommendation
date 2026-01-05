from typing import List, Optional
from pydantic import BaseModel

class RecommendRequest(BaseModel):
    user_id: str
    k: int = 10
    recent_clicks: Optional[List[str]] = None
    locale: str = "en"
    algorithm: str = "hybrid"  # "hybrid", "collaborative", "content", "bert"

class RecItem(BaseModel):
    item_id: str
    title: Optional[str] = None
    abstract: Optional[str] = None
    category: Optional[str] = None
    score: Optional[float] = None

class RecommendResponse(BaseModel):
    items: List[RecItem]

class SearchQuery(BaseModel):
    q: str
    k: int = 20
    category: Optional[str] = None

class SummarizeRequest(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    max_tokens: int = 128

class ExportPdfRequest(BaseModel):
    articles: List[RecItem]   # keys used by pdf generator
    user_id: str = "guest"
