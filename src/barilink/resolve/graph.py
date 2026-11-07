"""Entity resolution graph algorithms: connected components, cannot-link min-cut,
and weak-bridge splitting.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional, Sequence

import networkx as nx
import numpy as np
import pandas as pd


def build_resolved_graph(
    predictions_df: pd.DataFrame,
    records_df: pd.DataFrame,
    t_link: float,
    t_bridge: float,
    max_birth_year_gap: int = 10,
    must_link_pairs: Optional[Sequence[tuple[str, str]]] = None,
    cannot_link_pairs: Optional[Sequence[tuple[str, str]]] = None,
    features_df: Optional[pd.DataFrame] = None,
    apply_listed_as_other_member: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Execute 4-step graph entity resolution.

    Step 1: Build connected components from edges with match_weight >= t_link.
    Step 2: Enforce cannot-link constraints (sex conflict, birth year gap, oracle splits,
            and listed_as_other_member) by cutting minimum-weight edge set separating
            violating pairs (nx.minimum_cut).
    Step 3: Remove weak bridges with match_weight < t_bridge in components with >= 3 records.
    Step 4: Generate deterministic cluster IDs and resolution audit log.
    """
    all_record_ids = sorted(records_df["record_id"].astype(str).unique())

    # Build node attribute lookups
    rec_dict = records_df.set_index("record_id").to_dict(orient="index")
    feat_dict = (
        features_df.set_index("record_id").to_dict(orient="index")
        if features_df is not None and not features_df.empty
        else {}
    )

    # Step 1: Initial Connected Components
    G = nx.Graph()
    G.add_nodes_from(all_record_ids)

    # Filter edges above t_link
    scored_edges = []
    if not predictions_df.empty:
        above = predictions_df[predictions_df["match_weight"] >= t_link]
        for _, row in above.iterrows():
            u = str(row["record_id_l"])
            v = str(row["record_id_r"])
            w = float(row["match_weight"])
            if u != v:
                scored_edges.append((min(u, v), max(u, v), w))

    # Sort edges deterministically
    scored_edges.sort(key=lambda e: (e[0], e[1]))
    for u, v, w in scored_edges:
        G.add_edge(u, v, weight=w)

    # Add must-link edges with very high weight
    if must_link_pairs:
        for u, v in must_link_pairs:
            u_s, v_s = min(str(u), str(v)), max(str(u), str(v))
            if u_s != v_s:
                G.add_edge(u_s, v_s, weight=1000.0)

    resolution_log: list[dict[str, Any]] = []

    # Prepare oracle cannot-link set
    oracle_cl_set = set()
    if cannot_link_pairs:
        for u, v in cannot_link_pairs:
            oracle_cl_set.add((min(str(u), str(v)), max(str(u), str(v))))

    # Step 2: Cannot-Link Constraints Splitting via Minimum Cut
    # Repeat until no component contains any cannot-link pair
    while True:
        violation_found = False
        components = sorted(
            [sorted(c) for c in nx.connected_components(G)],
            key=lambda c: (len(c), c[0]),
            reverse=True,
        )

        for comp in components:
            if len(comp) < 2:
                continue

            comp_id = "comp_" + hashlib.sha256(",".join(comp).encode("utf-8")).hexdigest()[:8]
            violating_pair = None
            violation_reason = None

            # Scan for cannot-link pairs in this component
            for i in range(len(comp)):
                u = comp[i]
                rec_u = rec_dict.get(u, {})
                sex_u = rec_u.get("sex_raw")
                by_u = rec_u.get("birth_year_est")

                for j in range(i + 1, len(comp)):
                    v = comp[j]
                    rec_v = rec_dict.get(v, {})
                    sex_v = rec_v.get("sex_raw")
                    by_v = rec_v.get("birth_year_est")

                    # Check oracle constraint
                    if (min(u, v), max(u, v)) in oracle_cl_set:
                        violating_pair = (u, v)
                        violation_reason = "oracle_cannot_link"
                        break

                    # Check sex conflict
                    if (
                        sex_u is not None
                        and sex_v is not None
                        and pd.notna(sex_u)
                        and pd.notna(sex_v)
                    ):
                        if str(sex_u).strip().upper() != str(sex_v).strip().upper():
                            violating_pair = (u, v)
                            violation_reason = "sex_conflict"
                            break

                    # Check birth year gap
                    if by_u is not None and by_v is not None and pd.notna(by_u) and pd.notna(by_v):
                        try:
                            if abs(float(by_u) - float(by_v)) > max_birth_year_gap:
                                violating_pair = (u, v)
                                violation_reason = "birth_year_gap"
                                break
                        except (ValueError, TypeError):
                            pass

                    # Check listed_as_other_member constraint (for v3)
                    if apply_listed_as_other_member and feat_dict:
                        feat_u = feat_dict.get(u, {})
                        feat_v = feat_dict.get(v, {})
                        skel_u = feat_u.get("name_skeleton")
                        skel_v = feat_v.get("name_skeleton")
                        roster_u = feat_u.get("roster_skels_v3")
                        if roster_u is None or (isinstance(roster_u, float) and pd.isna(roster_u)):
                            roster_u = feat_u.get("roster_skels")
                        roster_v = feat_v.get("roster_skels_v3")
                        if roster_v is None or (isinstance(roster_v, float) and pd.isna(roster_v)):
                            roster_v = feat_v.get("roster_skels")
                        r_u_set = (
                            set(roster_u)
                            if isinstance(roster_u, (list, tuple, set, np.ndarray))
                            else set()
                        )
                        r_v_set = (
                            set(roster_v)
                            if isinstance(roster_v, (list, tuple, set, np.ndarray))
                            else set()
                        )
                        if (skel_u and skel_u in r_v_set) or (skel_v and skel_v in r_u_set):
                            violating_pair = (u, v)
                            violation_reason = "listed_as_other_member"
                            break

                if violating_pair is not None:
                    break

            if violating_pair is not None:
                u, v = violating_pair
                violation_found = True

                # Extract component subgraph
                H = G.subgraph(comp).copy()

                # Set capacity = match_weight exactly (no shift)
                for x, y, d in H.edges(data=True):
                    cap = float(d["weight"])
                    assert cap > 0, f"Edge ({x}, {y}) capacity must be > 0, got {cap}"
                    d["capacity"] = cap

                # Compute minimum s-t cut
                cut_val, (reachable, non_reachable) = nx.minimum_cut(H, u, v, capacity="capacity")

                # Cut edges are those with one endpoint in reachable and one in non_reachable
                cut_edges = []
                for x in reachable:
                    for y in H.neighbors(x):
                        if y in non_reachable:
                            cut_edges.append((min(x, y), max(x, y)))

                cut_edges = sorted(list(set(cut_edges)))

                for x, y in cut_edges:
                    edge_w = G[x][y]["weight"]
                    G.remove_edge(x, y)
                    resolution_log.append(
                        {
                            "component_id": comp_id,
                            "action": "constraint_cut",
                            "record_id_l": x,
                            "record_id_r": y,
                            "weight": edge_w,
                            "reason": violation_reason,
                        }
                    )

                # Restart check across components
                break

        if not violation_found:
            break

    # Step 3: Weak Bridges Removal
    # In each component with >= 3 records, find bridges with weight < t_bridge
    while True:
        bridge_cut_found = False
        components = sorted(
            [sorted(c) for c in nx.connected_components(G)],
            key=lambda c: (len(c), c[0]),
            reverse=True,
        )

        for comp in components:
            if len(comp) < 3:
                continue

            comp_id = "comp_" + hashlib.sha256(",".join(comp).encode("utf-8")).hexdigest()[:8]
            H = G.subgraph(comp)
            bridges = list(nx.bridges(H))

            # Filter weak bridges
            weak_bridges = []
            for u, v in bridges:
                w = G[u][v]["weight"]
                if w < t_bridge:
                    weak_bridges.append((w, min(u, v), max(u, v)))

            if weak_bridges:
                # Remove weakest bridge first (deterministic tiebreaker)
                weak_bridges.sort(key=lambda b: (b[0], b[1], b[2]))
                w_cut, u_cut, v_cut = weak_bridges[0]
                G.remove_edge(u_cut, v_cut)
                resolution_log.append(
                    {
                        "component_id": comp_id,
                        "action": "bridge_cut",
                        "record_id_l": u_cut,
                        "record_id_r": v_cut,
                        "weight": w_cut,
                        "reason": "weak_bridge",
                    }
                )
                bridge_cut_found = True
                break

        if not bridge_cut_found:
            break

    # Step 4: Deterministic Cluster IDs
    final_components = sorted(
        [sorted(c) for c in nx.connected_components(G)],
        key=lambda c: (c[0], len(c)),
    )

    cluster_rows = []
    for comp in final_components:
        cid = "c_" + hashlib.sha256(",".join(comp).encode("utf-8")).hexdigest()[:12]
        for rid in comp:
            cluster_rows.append({"record_id": rid, "cluster_id": cid})

    clusters_df = pd.DataFrame(cluster_rows)
    # Ensure all universe record IDs are present
    if len(clusters_df) < len(all_record_ids):
        present = set(clusters_df["record_id"])
        missing = [r for r in all_record_ids if r not in present]
        missing_rows = [
            {
                "record_id": r,
                "cluster_id": "c_" + hashlib.sha256(r.encode("utf-8")).hexdigest()[:12],
            }
            for r in missing
        ]
        clusters_df = pd.concat([clusters_df, pd.DataFrame(missing_rows)], ignore_index=True)

    clusters_df = clusters_df.sort_values("record_id").reset_index(drop=True)
    res_log_df = pd.DataFrame(resolution_log)
    if res_log_df.empty:
        res_log_df = pd.DataFrame(
            columns=["component_id", "action", "record_id_l", "record_id_r", "weight", "reason"]
        )

    return clusters_df, res_log_df


def evaluate_resolved_clusters(
    clusters_df: pd.DataFrame,
    record_truth_df: pd.DataFrame,
    true_pairs_df: pd.DataFrame,
    doppelganger_person_pairs_df: Optional[pd.DataFrame] = None,
    cost_false_merge: float = 5.0,
    cost_missed_duplicate: float = 1.0,
) -> dict[str, float]:
    """Compute cluster-level pairwise metrics and asymmetric cost for resolved clusters."""
    rec_person_map = dict(
        zip(record_truth_df["record_id"].astype(str), record_truth_df["person_id"].astype(str))
    )

    true_pairs_set = set()
    for _, r in true_pairs_df.iterrows():
        r1, r2 = str(r["record_id_1"]), str(r["record_id_2"])
        true_pairs_set.add((min(r1, r2), max(r1, r2)))
    total_true = len(true_pairs_set)

    # Cluster sizes and person breakdowns
    cluster_records = clusters_df.groupby("cluster_id")["record_id"].apply(list).to_dict()

    cluster_tp = 0
    total_pred_pairs = 0
    false_merge_clusters = 0
    person_clusters = {}

    for cid, rids in cluster_records.items():
        c_size = len(rids)
        if c_size > 1:
            total_pred_pairs += (c_size * (c_size - 1)) // 2

        p_counts = {}
        for rid in rids:
            p = rec_person_map.get(rid)
            if p:
                p_counts[p] = p_counts.get(p, 0) + 1
                if p not in person_clusters:
                    person_clusters[p] = set()
                person_clusters[p].add(cid)

        for p, cnt in p_counts.items():
            if cnt > 1:
                cluster_tp += (cnt * (cnt - 1)) // 2

        if len(p_counts) > 1:
            false_merge_clusters += 1

    cluster_fp = total_pred_pairs - cluster_tp
    cluster_fn = total_true - cluster_tp

    p = cluster_tp / (cluster_tp + cluster_fp) if (cluster_tp + cluster_fp) > 0 else 1.0
    r = cluster_tp / total_true if total_true > 0 else 0.0
    f1 = (2.0 * p * r) / (p + r) if (p + r) > 0 else 0.0
    expected_cost = cost_false_merge * cluster_fp + cost_missed_duplicate * cluster_fn

    # Doppelganger false merge rate
    doppel_rate = 0.0
    if doppelganger_person_pairs_df is not None and not doppelganger_person_pairs_df.empty:
        merged_doppels = 0
        tot_doppels = len(doppelganger_person_pairs_df)
        for _, row in doppelganger_person_pairs_df.iterrows():
            p1 = str(row["person_id_1"])
            p2 = str(row["person_id_2"])
            c1 = person_clusters.get(p1, set())
            c2 = person_clusters.get(p2, set())
            if c1 and c2 and bool(c1.intersection(c2)):
                merged_doppels += 1
        doppel_rate = merged_doppels / tot_doppels if tot_doppels > 0 else 0.0

    return {
        "cluster_tp": cluster_tp,
        "cluster_fp": cluster_fp,
        "cluster_fn": cluster_fn,
        "cluster_precision": p,
        "cluster_recall": r,
        "cluster_f1": f1,
        "false_merge_clusters": false_merge_clusters,
        "expected_cost": expected_cost,
        "doppelganger_false_merge_rate": doppel_rate,
        "dedup_reach": len(cluster_records),
    }


def select_resolve_parameters(
    predictions_df: pd.DataFrame,
    records_df: pd.DataFrame,
    record_truth_df: pd.DataFrame,
    true_pairs_df: pd.DataFrame,
    doppelganger_person_pairs_df: Optional[pd.DataFrame] = None,
    max_birth_year_gap: int = 10,
    cost_false_merge: float = 5.0,
    cost_missed_duplicate: float = 1.0,
    output_dir: Optional[Path] = None,
    features_df: Optional[pd.DataFrame] = None,
    apply_listed_as_other_member: bool = False,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """DEV-only parameter grid search for (t_link, t_bridge).

    Grid:
      t_link in {2.0, 2.5, 3.0, ..., 9.0}
      t_bridge in {t_link, int(t_link)+1, ..., 16} with t_link included exactly.
      Note: t_bridge = t_link is the baseline where no weak bridges are cut.

    Returns:
      (best_selection_dict, resolve_grid_df)
    """
    t_link_values = [round(x, 1) for x in np.arange(2.0, 14.1, 0.5)]
    grid_rows = []

    best_cost = float("inf")
    best_params = {}

    for t_l in t_link_values:
        # Build t_bridge values: t_l included exactly, then integer steps up to 16
        bridge_vals = [t_l]
        start_int = int(t_l) + 1
        for b in range(start_int, 17):
            if b > t_l and b not in bridge_vals:
                bridge_vals.append(float(b))

        for t_b in bridge_vals:
            clusters_df, res_log_df = build_resolved_graph(
                predictions_df=predictions_df,
                records_df=records_df,
                t_link=t_l,
                t_bridge=t_b,
                max_birth_year_gap=max_birth_year_gap,
                features_df=features_df,
                apply_listed_as_other_member=apply_listed_as_other_member,
            )

            metrics = evaluate_resolved_clusters(
                clusters_df=clusters_df,
                record_truth_df=record_truth_df,
                true_pairs_df=true_pairs_df,
                doppelganger_person_pairs_df=doppelganger_person_pairs_df,
                cost_false_merge=cost_false_merge,
                cost_missed_duplicate=cost_missed_duplicate,
            )

            cost = metrics["expected_cost"]
            is_baseline = t_b == t_l

            row = {
                "t_link": t_l,
                "t_bridge": t_b,
                "is_no_bridge_split_baseline": is_baseline,
                "cluster_precision": metrics["cluster_precision"],
                "cluster_recall": metrics["cluster_recall"],
                "cluster_f1": metrics["cluster_f1"],
                "expected_cost": cost,
                "doppelganger_false_merge_rate": metrics["doppelganger_false_merge_rate"],
                "false_merge_clusters": metrics["false_merge_clusters"],
                "dedup_reach": metrics["dedup_reach"],
                "cuts_constraint": int((res_log_df["action"] == "constraint_cut").sum())
                if not res_log_df.empty
                else 0,
                "cuts_bridge": int((res_log_df["action"] == "bridge_cut").sum())
                if not res_log_df.empty
                else 0,
            }
            grid_rows.append(row)

            if cost < best_cost:
                best_cost = cost
                best_params = {
                    "method": "splink_v1_resolved",
                    "dev_run": "demo",
                    "t_link": t_l,
                    "t_bridge": t_b,
                    "min_cost": cost,
                    "cluster_precision": metrics["cluster_precision"],
                    "cluster_recall": metrics["cluster_recall"],
                    "cluster_f1": metrics["cluster_f1"],
                    "doppelganger_false_merge_rate": metrics["doppelganger_false_merge_rate"],
                }

    grid_df = pd.DataFrame(grid_rows)

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        grid_df.to_parquet(output_dir / "resolve_grid.parquet", index=False)

        # Export interactive HTML heatmap
        charts_dir = output_dir / "charts"
        charts_dir.mkdir(parents=True, exist_ok=True)
        _export_resolve_grid_html(grid_df, best_params, charts_dir / "resolve_grid.html")

    return best_params, grid_df


def _export_resolve_grid_html(grid_df: pd.DataFrame, best_params: dict, out_html: Path) -> None:
    """Generate standalone interactive HTML chart showing the resolve grid with the baseline."""
    records_json = grid_df.to_json(orient="records")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Entity Resolution Grid: t_link vs t_bridge</title>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 24px;
      background: #fafafa;
    }}
    h1 {{ font-size: 20px; color: #111; margin-bottom: 8px; }}
    .subtitle {{ color: #555; margin-bottom: 20px; font-size: 14px; }}
    .legend-box {{
      background: white;
      padding: 12px;
      border-radius: 6px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      margin-bottom: 16px;
      font-size: 13px;
    }}
    #vis {{
      background: white;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }}
  </style>
</head>
<body>
  <h1>Phase 5 Entity Resolution Grid Search (Expected Cost)</h1>
  <div class="subtitle">
    Exploring linking threshold (<code>t_link</code>) and weak-bridge cutting threshold
    (<code>t_bridge</code>).
  </div>
  <div class="legend-box">
    <strong>Selected Optimum:</strong>
    <code>t_link = {best_params.get("t_link")}</code>,
    <code>t_bridge = {best_params.get("t_bridge")}</code>
    (Expected Cost: <strong>{best_params.get("min_cost"):.1f}</strong>,
    F1: <strong>{best_params.get("cluster_f1"):.4f}</strong>)<br>
    <em>Note:</em> Points where <code>t_bridge = t_link</code> represent the
    <strong>no bridge-splitting baseline</strong>.
  </div>
  <div id="vis"></div>

  <script>
    const data = {records_json};
    const spec = {{
      "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
      "data": {{ "values": data }},
      "width": 640,
      "height": 400,
      "mark": {{ "type": "rect", "tooltip": true }},
      "encoding": {{
        "x": {{ "field": "t_link", "type": "ordinal", "title": "Linking Threshold (t_link)" }},
        "y": {{
          "field": "t_bridge",
          "type": "ordinal",
          "title": "Bridge Threshold (t_bridge)",
          "sort": "descending"
        }},
        "color": {{
          "field": "expected_cost",
          "type": "quantitative",
          "scale": {{ "scheme": "redyellowblue", "reverse": true }},
          "title": "Expected Cost"
        }},
        "stroke": {{
          "condition": {{
            "test": "datum.is_no_bridge_split_baseline",
            "value": "#222"
          }},
          "value": "#ddd"
        }},
        "strokeWidth": {{
          "condition": {{
            "test": "datum.is_no_bridge_split_baseline",
            "value": 2
          }},
          "value": 0.5
        }}
      }}
    }};
    vegaEmbed('#vis', spec);
  </script>
</body>
</html>
"""
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_content)


def precompute_ui_clusters(
    predictions_df: pd.DataFrame,
    records_df: pd.DataFrame,
    t_bridge: float,
    output_path: Path,
    max_birth_year_gap: int = 10,
    features_df: Optional[pd.DataFrame] = None,
    apply_listed_as_other_member: bool = False,
) -> pd.DataFrame:
    """Precompute resolved clusters on holdout_0 for every t_link at the selected t_bridge.

    Output format: resolved_by_threshold.parquet with columns (t_link, record_id, cluster_id).
    """
    t_link_values = [round(x, 1) for x in np.arange(2.0, 14.1, 0.5)]
    all_dfs = []

    for t_l in t_link_values:
        clusters_df, _ = build_resolved_graph(
            predictions_df=predictions_df,
            records_df=records_df,
            t_link=t_l,
            t_bridge=t_bridge,
            max_birth_year_gap=max_birth_year_gap,
            features_df=features_df,
            apply_listed_as_other_member=apply_listed_as_other_member,
        )
        clusters_df["t_link"] = t_l
        all_dfs.append(clusters_df[["t_link", "record_id", "cluster_id"]])

    combined_df = pd.concat(all_dfs, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_parquet(output_path, index=False)
    return combined_df
