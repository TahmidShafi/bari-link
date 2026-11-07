import React, { useEffect, useRef, useState } from 'react';
import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  type SimulationNodeDatum,
  type SimulationLinkDatum,
} from 'd3-force';
import type { HouseholdGraphData } from '../data/types';

interface HouseholdGraphProps {
  householdClusterId: string;
  graphData: HouseholdGraphData;
}

interface D3Node extends SimulationNodeDatum {
  id: string;
  display_name: string;
  modules?: string[];
  isMember: boolean;
  household_id?: string;
}

interface D3Link extends SimulationLinkDatum<D3Node> {
  score: number;
  evidence_types: string[];
}

export const HouseholdGraph: React.FC<HouseholdGraphProps> = ({
  householdClusterId,
  graphData,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredNode, setHoveredNode] = useState<D3Node | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<D3Link | null>(null);

  // Filter 1-hop neighborhood subgraph for this household
  const { nodes, links } = React.useMemo(() => {
    const rawNodes = (graphData.nodes || []) as any[];
    const rawEdges = (graphData.edges || []) as any[];

    // 1. Identify direct household member nodes
    const memberNodeIds = new Set<string>();
    for (const n of rawNodes) {
      if (n.household_id === householdClusterId) {
        memberNodeIds.add(n.id);
      }
    }

    // 2. Identify 1-hop connected neighbour nodes and relevant edges
    const relevantEdgeSet = new Set<any>();
    const subNodeIds = new Set<string>(memberNodeIds);

    for (const e of rawEdges) {
      const u = typeof e.source === 'object' ? e.source.id : e.source;
      const v = typeof e.target === 'object' ? e.target.id : e.target;
      if (memberNodeIds.has(u) || memberNodeIds.has(v)) {
        relevantEdgeSet.add(e);
        subNodeIds.add(u);
        subNodeIds.add(v);
      }
    }

    const subNodes: D3Node[] = rawNodes
      .filter((n) => subNodeIds.has(n.id))
      .map((n) => ({
        id: n.id,
        display_name: n.display_name || n.name || n.id,
        modules: n.modules,
        household_id: n.household_id,
        isMember: memberNodeIds.has(n.id),
      }));

    const nodeMap = new Map<string, D3Node>();
    for (const n of subNodes) {
      nodeMap.set(n.id, n);
    }

    const subLinks: D3Link[] = [];
    for (const e of relevantEdgeSet) {
      const u = typeof e.source === 'object' ? e.source.id : e.source;
      const v = typeof e.target === 'object' ? e.target.id : e.target;
      if (nodeMap.has(u) && nodeMap.has(v)) {
        subLinks.push({
          source: nodeMap.get(u)!,
          target: nodeMap.get(v)!,
          score: e.score,
          evidence_types: e.evidence_types || [],
        });
      }
    }

    return { nodes: subNodes, links: subLinks };
  }, [householdClusterId, graphData]);

  // Force simulation
  const [positions, setPositions] = useState<{
    nodes: D3Node[];
    links: D3Link[];
  }>({ nodes: [], links: [] });

  useEffect(() => {
    if (nodes.length === 0) return;

    const width = 650;
    const height = 360;

    const simulation = forceSimulation<D3Node>(nodes)
      .force(
        'link',
        forceLink<D3Node, D3Link>(links)
          .id((d) => d.id)
          .distance(75)
      )
      .force('charge', forceManyBody().strength(-200))
      .force('center', forceCenter(width / 2, height / 2))
      .stop();

    // Run simulation synchronously to prevent layout shifts
    for (let i = 0; i < 120; ++i) {
      simulation.tick();
    }

    setPositions({
      nodes: [...nodes],
      links: [...links],
    });
  }, [nodes, links]);

  const evidenceDescription: Record<string, string> = {
    E1: 'E1: Listed Member Skeleton',
    E2: 'E2: Husband-Name Link',
    E3: 'E3: Father-Name Link (Patrilocal)',
    E4: 'E4: Roster Overlap (≥2 members)',
    E5: 'E5: Shared Phone Number',
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">Household Evidence Network (1-Hop Subgraph)</h3>
          <p className="tile-sub">
            Force layout of household members (solid green) and 1-hop evidence connections (dashed).
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span className="chip" style={{ backgroundColor: '#ccfbf1', color: '#115e59', fontWeight: 600 }}>
            ● Enrolled Member ({nodes.filter((n) => n.isMember).length})
          </span>
          <span className="chip" style={{ backgroundColor: '#f1f5f9', color: '#475569' }}>
            ○ 1-Hop Neighbor ({nodes.filter((n) => !n.isMember).length})
          </span>
        </div>
      </div>

      <div style={{ position: 'relative', width: '100%', overflow: 'hidden' }}>
        <svg
          ref={svgRef}
          className="household-subgraph"
          viewBox="0 0 650 360"
          style={{ width: '100%', height: 'auto', background: 'var(--bg-surface-subtle)', borderRadius: '4px' }}
        >
          {/* Edges */}
          {positions.links.map((link, idx) => {
            const s = link.source as D3Node;
            const t = link.target as D3Node;
            if (s.x === undefined || s.y === undefined || t.x === undefined || t.y === undefined) {
              return null;
            }
            const midX = (s.x + t.x) / 2;
            const midY = (s.y + t.y) / 2;
            const isHovered = hoveredEdge === link;

            return (
              <g
                key={idx}
                onMouseEnter={() => setHoveredEdge(link)}
                onMouseLeave={() => setHoveredEdge(null)}
                style={{ cursor: 'pointer' }}
              >
                <line
                  x1={s.x}
                  y1={s.y}
                  x2={t.x}
                  y2={t.y}
                  stroke={isHovered ? 'var(--accent)' : '#94a3b8'}
                  strokeWidth={isHovered ? 3 : Math.min(Math.max(link.score * 0.75, 1.5), 4)}
                  strokeDasharray={s.isMember && t.isMember ? undefined : '4 3'}
                />
                {/* Edge Label badge */}
                <rect
                  x={midX - 18}
                  y={midY - 8}
                  width={36}
                  height={16}
                  rx={3}
                  fill={isHovered ? '#0f766e' : '#ffffff'}
                  stroke={isHovered ? '#0f766e' : '#cbd5e1'}
                />
                <text
                  x={midX}
                  y={midY + 3}
                  textAnchor="middle"
                  fontSize={9}
                  fontWeight={600}
                  fill={isHovered ? '#ffffff' : '#334155'}
                >
                  {link.evidence_types.join(',')}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {positions.nodes.map((node) => {
            if (node.x === undefined || node.y === undefined) return null;
            const isHovered = hoveredNode === node;
            const r = node.isMember ? 12 : 9;

            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                onMouseEnter={() => setHoveredNode(node)}
                onMouseLeave={() => setHoveredNode(null)}
                style={{ cursor: 'pointer' }}
              >
                <circle
                  r={isHovered ? r + 2 : r}
                  fill={node.isMember ? '#0f766e' : '#ffffff'}
                  stroke={isHovered ? 'var(--accent)' : node.isMember ? '#115e59' : '#64748b'}
                  strokeWidth={isHovered ? 3 : node.isMember ? 2.5 : 1.5}
                />
                <text
                  y={r + 12}
                  textAnchor="middle"
                  fontSize={10}
                  fontWeight={node.isMember ? 700 : 500}
                  fill={node.isMember ? '#0f172a' : '#64748b'}
                >
                  {node.display_name.split(' ')[0]}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hover detail tooltip */}
        {hoveredEdge && (
          <div
            style={{
              position: 'absolute',
              bottom: 8,
              left: 8,
              background: 'rgba(15, 23, 42, 0.9)',
              color: '#ffffff',
              padding: '0.5rem 0.75rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              pointerEvents: 'none',
            }}
          >
            <strong>Evidence Link:</strong> Score {hoveredEdge.score.toFixed(1)}
            <br />
            Rules: {hoveredEdge.evidence_types.map((e) => evidenceDescription[e] || e).join(', ')}
          </div>
        )}

        {hoveredNode && (
          <div
            style={{
              position: 'absolute',
              top: 8,
              right: 8,
              background: 'rgba(15, 23, 42, 0.9)',
              color: '#ffffff',
              padding: '0.5rem 0.75rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              pointerEvents: 'none',
            }}
          >
            <strong>{hoveredNode.display_name}</strong>
            <br />
            Cluster: {hoveredNode.id}
            <br />
            Household: {hoveredNode.isMember ? 'Current Household' : hoveredNode.household_id}
            {hoveredNode.modules && (
              <>
                <br />
                Modules: {hoveredNode.modules.join(', ')}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
