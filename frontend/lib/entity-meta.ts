import type { EntityType } from "@/lib/career-brain-api";

export const ENTITY_META: Record<EntityType, { label: string; color: string; dot: string; hex: string }> = {
  SKILL: { label: "Skill", color: "text-accent bg-accent-soft", dot: "bg-accent", hex: "#5B4FE8" },
  PROJECT: { label: "Project", color: "text-emerald-700 bg-emerald-50", dot: "bg-emerald-500", hex: "#10B981" },
  CERTIFICATE: { label: "Certification", color: "text-amber-700 bg-amber-50", dot: "bg-amber-500", hex: "#F59E0B" },
  ACHIEVEMENT: { label: "Achievement", color: "text-rose-700 bg-rose-50", dot: "bg-rose-500", hex: "#F43F5E" },
  ORGANIZATION: { label: "Organization", color: "text-sky-700 bg-sky-50", dot: "bg-sky-500", hex: "#0EA5E9" },
  EDUCATION: { label: "Education", color: "text-indigo-700 bg-indigo-50", dot: "bg-indigo-500", hex: "#6366F1" },
  INTERNSHIP: { label: "Internship", color: "text-fuchsia-700 bg-fuchsia-50", dot: "bg-fuchsia-500", hex: "#D946EF" },
  TECHNOLOGY: { label: "Technology", color: "text-cyan-700 bg-cyan-50", dot: "bg-cyan-500", hex: "#06B6D4" },
};

export const ENTITY_TYPES = Object.keys(ENTITY_META) as EntityType[];
