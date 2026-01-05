// web/src/types.ts

export interface RecItem {
  item_id: string;
  title?: string;
  abstract?: string;
  category?: string;
  score?: number;
  reason?: string;
}

// mirrors your FastAPI pydantic models
export interface RecommendRequest {
  user_id: string;
  k?: number;
  recent_clicks?: string[] | null;
  locale?: string;
  algorithm?: "hybrid" | "collaborative" | "content" | "bert" | string;
}

export interface RecommendResponse {
  items: RecItem[];
}