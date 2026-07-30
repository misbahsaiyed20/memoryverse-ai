import { apiFetch } from "@/lib/api";

export type EntityType =
  | "SKILL"
  | "PROJECT"
  | "CERTIFICATE"
  | "ACHIEVEMENT"
  | "ORGANIZATION"
  | "EDUCATION"
  | "INTERNSHIP"
  | "TECHNOLOGY";

export interface KnowledgeNodeItem {
  id: string;
  entity_type: EntityType;
  name: string;
  description: string | null;
  confidence: number | null;
  evidence_quote: string;
  document_id: string;
  filename: string;
  chunk_id: string;
}

export interface TimelineEntry {
  document_id: string;
  filename: string;
  created_at: string;
  nodes: KnowledgeNodeItem[];
}

interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
}

async function extractErrorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json();
    return body.detail || body.message || fallback;
  } catch {
    return fallback;
  }
}

export async function getEntityCounts(): Promise<Record<EntityType, number>> {
  const res = await apiFetch("/api/v1/career-brain/summary");
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to load Career Brain summary."));
  const body: ApiEnvelope<Record<EntityType, number>> = await res.json();
  return body.data;
}

export async function getNodes(params: {
  entityType?: EntityType;
  relatedTo?: string;
}): Promise<KnowledgeNodeItem[]> {
  const query = new URLSearchParams();
  if (params.entityType) query.set("entity_type", params.entityType);
  if (params.relatedTo) query.set("related_to", params.relatedTo);
  const qs = query.toString();

  const res = await apiFetch(`/api/v1/career-brain/nodes${qs ? `?${qs}` : ""}`);
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to load knowledge nodes."));
  const body: ApiEnvelope<{ nodes: KnowledgeNodeItem[]; count: number }> = await res.json();
  return body.data.nodes;
}

export async function getTimeline(): Promise<TimelineEntry[]> {
  const res = await apiFetch("/api/v1/career-brain/timeline");
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to load timeline."));
  const body: ApiEnvelope<{ timeline: TimelineEntry[] }> = await res.json();
  return body.data.timeline;
}

export interface KnowledgeEdgeItem {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relationship_type: string;
  description: string | null;
  confidence: number | null;
}

export async function getEdges(): Promise<KnowledgeEdgeItem[]> {
  const res = await apiFetch("/api/v1/career-brain/edges");
  if (!res.ok) throw new Error(await extractErrorMessage(res, "Failed to load relationships."));
  const body: ApiEnvelope<{ edges: KnowledgeEdgeItem[] }> = await res.json();
  return body.data.edges;
}

export async function getGraph(): Promise<{ nodes: KnowledgeNodeItem[]; edges: KnowledgeEdgeItem[] }> {
  const [nodes, edges] = await Promise.all([getNodes({}), getEdges()]);
  return { nodes, edges };
}
