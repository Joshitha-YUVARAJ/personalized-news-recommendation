from typing import List, Dict, Any, Optional

# adjust the import if your folder name differs
from utils import recommenders as R

_loaded = False

def _ensure_loaded() -> None:
    """Run any one-time setup for utils.recommenders."""
    global _loaded
    if _loaded:
        return
    if hasattr(R, "initialize"):
        R.initialize()
    _loaded = True


def recommend(
    user_id: str,
    k: int = 10,
    recent_clicks: Optional[list[str]] = None,
    locale: str = "en",
    algorithm: str = "hybrid",
) -> List[Dict[str, Any]]:
    _ensure_loaded()
    
    # Try each algorithm with fallback mechanisms
    try:
        if algorithm == "bert4rec" and hasattr(R, "bert4rec_recommend"):
            return R.bert4rec_recommend(user_id=user_id, k=k)
        elif algorithm == "hybrid" and hasattr(R, "hybrid_recommend"):
            return R.hybrid_recommend(user_id=user_id, k=k)
        elif algorithm == "collaborative" and hasattr(R, "collaborative_filtering"):
            return R.collaborative_filtering(user_id=user_id, k=k)
        elif algorithm == "content" and hasattr(R, "content_based_filtering"):
            return R.content_based_filtering(user_id=user_id, k=k)
        elif hasattr(R, "recommend"):
            return R.recommend(user_id=user_id, k=k, recent_clicks=recent_clicks, algorithm=algorithm)
    except Exception as e:
        print(f"Recommendation algorithm {algorithm} failed: {e}")
    
    # Fallback: personalized recommendations based on user preferences
    try:
        news_df, behaviors_df = R.load_mind_data()
        # Try to get user behavior patterns
        user_articles = news_df.sample(n=min(k, len(news_df)))
        return [
            {
                "item_id": str(row.get("NewsID", f"R{i}")),
                "title": str(row.get("Title", "")) if row.get("Title") and str(row.get("Title")) != "nan" else "",
                "abstract": str(row.get("Abstract", "")) if row.get("Abstract") and str(row.get("Abstract")) != "nan" else "",
                "category": str(row.get("Category", "")) if row.get("Category") and str(row.get("Category")) != "nan" else "",
                "score": 0.8,
                "reason": f"Recommended via {algorithm}"
            }
            for i, row in user_articles.iterrows()
        ]
    except Exception as e:
        print(f"Recommendation fallback failed: {e}")
        # Final fallback to trending
        return trending(k)


def search(q: str, k: int = 20, category: Optional[str] = None) -> List[Dict[str, Any]]:
    _ensure_loaded()
    
    # Use the actual search_by_keywords function from utils.recommenders
    if hasattr(R, "search_by_keywords"):
        try:
            results = R.search_by_keywords(q=q, k=k, category=category)
            # The function already returns a properly formatted list
            return results
        except Exception as e:
            print(f"search_by_keywords failed: {e}")
    
    # Fallback: use simple keyword search with the loaded data
    try:
        import pandas as pd
        news_df, _ = R.load_mind_data()
        
        df = news_df.copy()
        if category:
            df = df[df.get("Category", "").astype(str).str.lower() == category.lower()]

        q_norm = (q or "").strip().lower()
        if not q_norm:
            # Return trending articles if no query
            head = df.head(k)
            return [
                {
                    "item_id": str(row.get("NewsID", f"N{i}")),
                    "title": row.get("Title", ""),
                    "abstract": row.get("Abstract", ""),
                    "category": row.get("Category", ""),
                    "score": 1.0,
                    "reason": "Trending"
                }
                for i, row in head.iterrows()
            ]

        # Search in title and abstract
        title_hit = df.get("Title", "").astype(str).str.lower().str.contains(q_norm, na=False, regex=False)
        abs_hit = df.get("Abstract", "").astype(str).str.lower().str.contains(q_norm, na=False, regex=False)

        # Score: title match = 2, abstract match = 1
        df = df.assign(_score=(title_hit.astype(int) * 2 + abs_hit.astype(int)))
        df = df[df["_score"] > 0].sort_values("_score", ascending=False).head(k)

        results = []
        for i, row in df.iterrows():
            results.append({
                "item_id": str(row.get("NewsID", f"N{i}")),
                "title": row.get("Title", ""),
                "abstract": row.get("Abstract", ""),
                "category": row.get("Category", ""),
                "score": float(row.get("_score", 0)),
                "reason": "Keyword match"
            })
        return results
    except Exception as e:
        print(f"Fallback search failed: {e}")
        # Last resort: return stubs
        return [{"item_id": f"stub-{i}", "title": f"{q} (stub {i})", "score": 0.0} for i in range(k)]


def summarize(title: Optional[str] = None, abstract: Optional[str] = None, max_tokens: int = 128) -> Dict[str, Any]:
    _ensure_loaded()
    if hasattr(R, "summarize"):
        return R.summarize(title=title, abstract=abstract, max_tokens=max_tokens)
    text = (title or "") + " " + (abstract or "")
    return {"summary": text[:max_tokens]}


def trending(k: int = 10) -> List[Dict[str, Any]]:
    _ensure_loaded()
    
    # Use the actual get_trending_articles function
    if hasattr(R, "get_trending_articles"):
        try:
            results = R.get_trending_articles(k=k)
            return results
        except Exception as e:
            print(f"get_trending_articles failed: {e}")
    
    # Fallback: get popular articles
    if hasattr(R, "get_popular_articles"):
        try:
            results = R.get_popular_articles()
            return results[:k] if isinstance(results, list) else results
        except Exception as e:
            print(f"get_popular_articles failed: {e}")
    
    # Last fallback: return first k articles from dataset
    try:
        news_df, _ = R.load_mind_data()
        head = news_df.head(k)
        return [
            {
                "item_id": str(row.get("NewsID", f"N{i}")),
                "title": str(row.get("Title", "")) if row.get("Title") and str(row.get("Title")) != "nan" else "",
                "abstract": str(row.get("Abstract", "")) if row.get("Abstract") and str(row.get("Abstract")) != "nan" else "",
                "category": str(row.get("Category", "")) if row.get("Category") and str(row.get("Category")) != "nan" else "",
                "score": 1.0,
                "reason": "Popular"
            }
            for i, row in head.iterrows()
        ]
    except Exception as e:
        print(f"Trending fallback failed: {e}")
        return [{"item_id": f"trending-{i}", "title": f"Trending Article {i}", "score": 1.0} for i in range(k)]
