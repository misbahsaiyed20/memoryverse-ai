"use client";

import { useMemo, useRef, useState } from "react";
import { ZoomIn, ZoomOut, Maximize2 } from "lucide-react";

import type { KnowledgeEdgeItem, KnowledgeNodeItem } from "@/lib/career-brain-api";
import { ENTITY_META, ENTITY_TYPES } from "@/lib/entity-meta";
import { EvidenceChip } from "@/components/evidence-chip";
import { cn } from "@/lib/utils";

const WIDTH = 1000;
const HEIGHT = 760;
const CENTER = { x: WIDTH / 2, y: HEIGHT / 2 };
const RING_STEP = 62;
const BASE_RADIUS = 70;

interface PositionedNode extends KnowledgeNodeItem {
  x: number;
  y: number;
}

function layout(nodes: KnowledgeNodeItem[]): PositionedNode[] {
  const byType = new Map<string, KnowledgeNodeItem[]>();
  for (const node of nodes) {
    const list = byType.get(node.entity_type) ?? [];
    list.push(node);
    byType.set(node.entity_type, list);
  }

  const positioned: PositionedNode[] = [];
  ENTITY_TYPES.forEach((type, ringIndex) => {
    const ringNodes = byType.get(type) ?? [];
    const radius = BASE_RADIUS + ringIndex * RING_STEP;
    ringNodes.forEach((node, i) => {
      const angle = (i / Math.max(ringNodes.length, 1)) * Math.PI * 2 + ringIndex * 0.4;
      positioned.push({
        ...node,
        x: CENTER.x + radius * Math.cos(angle),
        y: CENTER.y + radius * Math.sin(angle),
      });
    });
  });
  return positioned;
}

export function KnowledgeGraph({
  nodes,
  edges,
}: {
  nodes: KnowledgeNodeItem[];
  edges: KnowledgeEdgeItem[];
}) {
  const [activeTypes, setActiveTypes] = useState<Set<string>>(new Set(ENTITY_TYPES));
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const dragState = useRef<{ startX: number; startY: number; originX: number; originY: number } | null>(
    null,
  );

  const positioned = useMemo(() => layout(nodes), [nodes]);
  const visible = useMemo(
    () => positioned.filter((n) => activeTypes.has(n.entity_type)),
    [positioned, activeTypes],
  );
  const visibleIds = useMemo(() => new Set(visible.map((n) => n.id)), [visible]);
  const positionById = useMemo(() => new Map(visible.map((n) => [n.id, n])), [visible]);

  const visibleEdges = edges.filter(
    (e) => visibleIds.has(e.source_node_id) && visibleIds.has(e.target_node_id),
  );

  const connectedIds = useMemo(() => {
    if (!selectedId) return null;
    const set = new Set<string>([selectedId]);
    for (const edge of visibleEdges) {
      if (edge.source_node_id === selectedId) set.add(edge.target_node_id);
      if (edge.target_node_id === selectedId) set.add(edge.source_node_id);
    }
    return set;
  }, [selectedId, visibleEdges]);

  const selectedNode = selectedId ? positionById.get(selectedId) : null;

  function toggleType(type: string) {
    setActiveTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  }

  function zoom(factor: number) {
    setTransform((t) => ({ ...t, scale: Math.min(3, Math.max(0.4, t.scale * factor)) }));
  }

  function resetView() {
    setTransform({ x: 0, y: 0, scale: 1 });
  }

  function onMouseDown(e: React.MouseEvent) {
    dragState.current = {
      startX: e.clientX,
      startY: e.clientY,
      originX: transform.x,
      originY: transform.y,
    };
  }

  function onMouseMove(e: React.MouseEvent) {
    if (!dragState.current) return;
    const dx = e.clientX - dragState.current.startX;
    const dy = e.clientY - dragState.current.startY;
    setTransform((t) => ({ ...t, x: dragState.current!.originX + dx, y: dragState.current!.originY + dy }));
  }

  function onMouseUp() {
    dragState.current = null;
  }

  return (
    <div className="flex gap-4">
      <div className="flex-1">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {ENTITY_TYPES.map((type) => (
              <button
                key={type}
                onClick={() => toggleType(type)}
                className={cn(
                  "flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                  activeTypes.has(type)
                    ? "border-accent bg-accent-soft text-accent"
                    : "border-border bg-surface text-muted opacity-60",
                )}
              >
                <span className={cn("h-1.5 w-1.5 rounded-full", ENTITY_META[type].dot)} />
                {ENTITY_META[type].label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1.5">
            <button onClick={() => zoom(1.2)} className="rounded-lg border border-border bg-surface p-1.5 text-muted hover:text-accent">
              <ZoomIn size={15} />
            </button>
            <button onClick={() => zoom(1 / 1.2)} className="rounded-lg border border-border bg-surface p-1.5 text-muted hover:text-accent">
              <ZoomOut size={15} />
            </button>
            <button onClick={resetView} className="rounded-lg border border-border bg-surface p-1.5 text-muted hover:text-accent">
              <Maximize2 size={15} />
            </button>
          </div>
        </div>

        <div
          className="mt-4 h-[600px] cursor-grab overflow-hidden rounded-2xl border border-border bg-surface active:cursor-grabbing"
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseUp}
        >
          <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="h-full w-full select-none">
            <g transform={`translate(${transform.x} ${transform.y}) scale(${transform.scale})`}>
              {visibleEdges.map((edge) => {
                const source = positionById.get(edge.source_node_id);
                const target = positionById.get(edge.target_node_id);
                if (!source || !target) return null;
                const dimmed = connectedIds ? !connectedIds.has(source.id) || !connectedIds.has(target.id) : false;
                return (
                  <line
                    key={edge.id}
                    x1={source.x}
                    y1={source.y}
                    x2={target.x}
                    y2={target.y}
                    stroke="#C9C9D4"
                    strokeWidth={dimmed ? 0.75 : 1.5}
                    opacity={dimmed ? 0.25 : 0.8}
                  />
                );
              })}

              {visible.map((node) => {
                const dimmed = connectedIds ? !connectedIds.has(node.id) : false;
                const selected = node.id === selectedId;
                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x} ${node.y})`}
                    className="cursor-pointer"
                    onClick={() => setSelectedId(node.id === selectedId ? null : node.id)}
                    opacity={dimmed ? 0.3 : 1}
                  >
                    <circle
                      r={selected ? 9 : 6}
                      fill={ENTITY_META[node.entity_type].hex}
                      stroke={selected ? "#14141A" : "none"}
                      strokeWidth={selected ? 1.5 : 0}
                    />
                    <text
                      x={10}
                      y={4}
                      fontSize={11}
                      fill="#14141A"
                      className={selected ? "font-semibold" : ""}
                    >
                      {node.name.length > 22 ? `${node.name.slice(0, 22)}…` : node.name}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>
      </div>

      {selectedNode && (
        <div className="w-64 shrink-0 rounded-2xl border border-border bg-surface p-5">
          <p className="font-display text-sm font-semibold text-foreground">{selectedNode.name}</p>
          <p className="mt-1 text-xs text-muted">{ENTITY_META[selectedNode.entity_type].label}</p>
          {selectedNode.description && (
            <p className="mt-3 text-sm text-muted">{selectedNode.description}</p>
          )}
          <div className="mt-4">
            <EvidenceChip filename={selectedNode.filename} quote={selectedNode.evidence_quote} />
          </div>
        </div>
      )}
    </div>
  );
}
