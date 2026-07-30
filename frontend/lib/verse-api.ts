import { apiFetch } from "@/lib/api";

export interface VerseSource {
  document_id: string | null;
  filename: string | null;
  chunk_id: string | null;
  chunk_index: number | null;
  distance: number | null;
}

export interface VerseAnswer {
  success: boolean;
  answer: string;
  sources: VerseSource[];
}

export async function askVerse(question: string, topK = 5): Promise<VerseAnswer> {
  const res = await apiFetch("/api/v1/verse/ask", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Verse AI didn't respond. Please try again.");
  }
  return res.json();
}
