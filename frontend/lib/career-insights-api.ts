import { apiFetch } from "@/lib/api";

export interface Recommendation {
  item: string;
  reason: string;
}

export interface Highlight {
  name: string;
  reason: string;
}

export interface CareerInsights {
  resume_summary: string;
  experience_summary: string;
  top_strengths: string[];
  core_skills: string[];
  weak_skills: Recommendation[];
  missing_skills: Recommendation[];
  learning_suggestions: Recommendation[];
  career_recommendations: Recommendation[];
  project_highlights: Highlight[];
  certification_highlights: Highlight[];
}

export async function getInsights(): Promise<CareerInsights> {
  const res = await apiFetch("/api/v1/career-brain/insights");
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Failed to generate career insights.");
  }
  const body: { success: boolean; message: string; data: CareerInsights } = await res.json();
  return body.data;
}
