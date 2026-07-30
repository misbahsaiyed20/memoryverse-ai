import { apiFetch } from "@/lib/api";

export interface SearchResultItem {
  document_id: string | null;
  chunk_id: string | null;
  chunk_text: string | null;
  filename: string | null;
  chunk_index: number | null;
  metadata: Record<string, unknown>;
  distance: number | null;
}

export async function searchDocuments(query: string, topK = 5): Promise<SearchResultItem[]> {
  const res = await apiFetch("/api/v1/search", {
    method: "POST",
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Search failed. Please try again.");
  }
  const body: { success: boolean; query: string; results: SearchResultItem[] } = await res.json();
  return body.results;
}
