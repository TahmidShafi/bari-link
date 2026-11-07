"""Graph clustering and constraint enforcement for household inference.

Strict segregation: This module processes only model-visible inputs.
Zero references to ground-truth files or directories are permitted.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

import networkx as nx
import pandas as pd

from barilink.household.evidence import UnitProfile


def infer_households(
    profiles: dict[str, UnitProfile],
    edges_df: pd.DataFrame,
    t_hh: float,
    max_size: int = 12,
    output_clusters_path: Optional[Path] = None,
    output_log_path: Optional[Path] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Infer household clusters by connected components with cannot-household and max-size min-cuts.

    Args:
        profiles: Dictionary mapping cluster_id to UnitProfile.
        edges_df: DataFrame of pairwise evidence scores.
        t_hh: Minimum edge score threshold for linking.
        max_size: Maximum allowable household size (default 12).
        output_clusters_path: Optional path to save household_clusters.parquet.
        output_log_path: Optional path to save household_log.parquet.

    Returns:
        tuple of (household_clusters_df, household_log_df)
    """
    # 1. Build initial graph
    G = nx.Graph()
    # Add all unit nodes (including isolates)
    for cid in profiles.keys():
        G.add_node(cid)

    # Filter edges by threshold
    valid_edges = edges_df[edges_df["score"] >= t_hh] if not edges_df.empty else pd.DataFrame()
    for _, row in valid_edges.iterrows():
        u = str(row["unit_id_l"])
        v = str(row["unit_id_r"])
        score = float(row["score"])
        e2_active = bool(row.get("e2", False))
        if G.has_edge(u, v):
            if score > G[u][v]["capacity"]:
                G[u][v]["capacity"] = score
                G[u][v]["e2"] = e2_active
        else:
            G.add_edge(u, v, capacity=score, e2=e2_active)

    log_rows: list[dict[str, Any]] = []

    # 2. Max Household Size Splitting (capacity = score)
    # Split oversize components down to max_size on weakest edges
    while True:
        oversize_comps = [c for c in nx.connected_components(G) if len(c) > max_size]
        if not oversize_comps:
            break

        for comp in oversize_comps:
            H = G.subgraph(comp).copy()
            if len(H) <= 25:
                cut_val, (set1, set2) = nx.stoer_wagner(H, weight="capacity")
                cut_edges = [(u, v) for u in set1 for v in H.neighbors(u) if v in set2]
            else:
                s = list(H.nodes())[0]
                lengths = nx.single_source_shortest_path_length(H, s)
                sorted_nodes = sorted(H.nodes(), key=lambda n: (lengths.get(n, 0), n))
                half = len(sorted_nodes) // 2
                set1 = set(sorted_nodes[:half])
                set2 = set(sorted_nodes[half:])
                cut_edges = [(u, v) for u in set1 for v in H.neighbors(u) if v in set2]

            for u_cut, v_cut in cut_edges:
                w_cut = G[u_cut][v_cut]["capacity"]
                G.remove_edge(u_cut, v_cut)
                log_rows.append(
                    {
                        "action": "max_size_cut",
                        "unit_id_l": u_cut,
                        "unit_id_r": v_cut,
                        "weight": w_cut,
                        "reason": f"oversize_comp_size_{len(comp)}_split",
                    }
                )

    # 3. Cannot-Household Constraint Splitting (per component)
    # Two units with different husband skeletons each linked by E2 to different units in component
    for comp in list(nx.connected_components(G)):
        if len(comp) < 2:
            continue

        curr_comp = list(comp)
        while True:
            wives: list[tuple[str, str, str]] = []
            for u in curr_comp:
                prof = profiles.get(u)
                if prof and prof.has_husband and prof.husband_skeleton:
                    for nbr in G.neighbors(u):
                        if nbr in curr_comp and G[u][nbr].get("e2", False):
                            nbr_prof = profiles.get(nbr)
                            if nbr_prof and (prof.husband_skeleton in nbr_prof.name_skels):
                                wives.append((u, prof.husband_skeleton, nbr))
                                break

            conflict: Optional[tuple[str, str]] = None
            for i in range(len(wives)):
                for j in range(i + 1, len(wives)):
                    w1, h1, m1 = wives[i]
                    w2, h2, m2 = wives[j]
                    if h1 != h2 and m1 != m2:
                        conflict = (w1, w2)
                        break
                if conflict:
                    break

            if conflict:
                w1, w2 = conflict
                H = G.subgraph(curr_comp).copy()
                cut_val, (sa, sb) = nx.minimum_cut(H, w1, w2, capacity="capacity")
                c_edges = [(u, v) for u in sa for v in H.neighbors(u) if v in sb]
                for u_cut, v_cut in c_edges:
                    w_cut = G[u_cut][v_cut]["capacity"]
                    G.remove_edge(u_cut, v_cut)
                    log_rows.append(
                        {
                            "action": "cannot_household_cut",
                            "unit_id_l": u_cut,
                            "unit_id_r": v_cut,
                            "weight": w_cut,
                            "reason": f"different_husbands_{w1}_{w2}",
                        }
                    )
                H.remove_edges_from(c_edges)
                curr_comp = list(nx.node_connected_component(H, w1))
            else:
                break

    # 4. Generate deterministic household IDs
    cluster_rows: list[dict[str, str]] = []
    final_components = [sorted(list(c)) for c in nx.connected_components(G)]
    final_components.sort(key=lambda c: c[0])

    for comp in final_components:
        comp_hash = hashlib.sha256("_".join(comp).encode("utf-8")).hexdigest()[:12]
        hh_id = f"hh_{comp_hash}"
        for member_cid in comp:
            cluster_rows.append(
                {
                    "cluster_id": member_cid,
                    "household_id": hh_id,
                }
            )

    clusters_df = pd.DataFrame(cluster_rows)
    clusters_df = clusters_df.sort_values("cluster_id").reset_index(drop=True)

    log_df = pd.DataFrame(log_rows)
    if log_df.empty:
        log_df = pd.DataFrame(columns=["action", "unit_id_l", "unit_id_r", "weight", "reason"])

    if output_clusters_path is not None:
        output_clusters_path.parent.mkdir(parents=True, exist_ok=True)
        clusters_df.to_parquet(output_clusters_path, index=False)

    if output_log_path is not None:
        output_log_path.parent.mkdir(parents=True, exist_ok=True)
        log_df.to_parquet(output_log_path, index=False)

    return clusters_df, log_df
