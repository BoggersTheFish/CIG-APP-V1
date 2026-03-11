"""
Hypothesis Engine: suggest links from similarity and tension (conflict edges).
"""
from goat_ts_cig.llm_stub import generate as llm_generate


def generate_hypotheses(kg, rg=None, id_map=None, similarity_threshold: float = 0.3, use_llm: bool = False, config: dict = None):
    """
    Detect weak connections (similar but no edge) and tension (conflict edges with act mismatch).
    id_map: list of SQLite node ids in Rust index order (from to_rust_graph). Required if rg is used.
    Returns list of {"from": id, "to": id, "reason": str, "score": float}.
    """
    config = config or {}
    hypotheses = []
    data = kg.to_json()
    nodes = {n["id"]: n for n in data["nodes"]}
    edge_set = {(e["from_id"], e["to_id"]) for e in data["edges"]}

    # Similarity-based: use Rust if available
    if rg is not None and id_map and hasattr(rg, "find_similar"):
        for i in range(min(rg.node_count(), len(id_map))):
            sqlite_id = id_map[i]
            similar = rg.find_similar(i, similarity_threshold, use_activation_weight=True)
            for rust_j in similar:
                if rust_j < len(id_map):
                    to_id = id_map[rust_j]
                    if sqlite_id != to_id and (sqlite_id, to_id) not in edge_set and (to_id, sqlite_id) not in edge_set:
                        hypotheses.append({
                            "from": sqlite_id,
                            "to": to_id,
                            "reason": "similarity > threshold",
                            "score": similarity_threshold,
                        })

    # Embeddings-based similarity when enabled (fallback or supplement)
    emb_enabled = (config.get("advanced") or {}).get("embeddings") or {}
    if emb_enabled.get("enabled"):
        try:
            from goat_ts_cig.embeddings import available as emb_available, embed_batch
            if emb_available():
                node_list = data.get("nodes", [])
                if len(node_list) <= 200:
                    labels = [(n.get("label") or "").strip() or f"id{n['id']}" for n in node_list]
                    vecs = embed_batch(labels)
                    for i in range(len(node_list)):
                        for j in range(i + 1, len(node_list)):
                            a_id, b_id = node_list[i]["id"], node_list[j]["id"]
                            if (a_id, b_id) in edge_set or (b_id, a_id) in edge_set:
                                continue
                            # cosine similarity
                            va, vb = vecs[i], vecs[j]
                            dot = sum(x * y for x, y in zip(va, vb))
                            na = sum(x * x for x in va) ** 0.5
                            nb = sum(x * x for x in vb) ** 0.5
                            if na > 0 and nb > 0:
                                sim = dot / (na * nb)
                                if sim >= similarity_threshold:
                                    hypotheses.append({
                                        "from": a_id,
                                        "to": b_id,
                                        "reason": "embedding similarity > threshold",
                                        "score": float(sim),
                                    })
        except Exception:
            pass

    # Tension-based: conflict edges with high activation difference
    tension_thresh = config.get("tension_threshold", 0.3)
    for e in data["edges"]:
        if e.get("type") != "conflict":
            continue
        a, b = e["from_id"], e["to_id"]
        na, nb = nodes.get(a), nodes.get(b)
        if not na or not nb:
            continue
        act_a = na.get("activation", 0) or 0
        act_b = nb.get("activation", 0) or 0
        if abs(act_a - act_b) > tension_thresh:
            hypotheses.append({
                "from": a,
                "to": b,
                "reason": "tension (conflict edge, activation mismatch)",
                "score": abs(act_a - act_b),
            })

    if use_llm and config.get("llm"):
        ollama_cfg = config.get("llm_ollama") or {}
        if ollama_cfg.get("enabled") and ollama_cfg.get("use_for_hypotheses"):
            try:
                from goat_ts_cig.llm_ollama import generate as ollama_generate
                for h in hypotheses:
                    h["natural_language"] = ollama_generate(
                        f"Suggest a one-sentence link between concepts: {h.get('from')} and {h.get('to')}.",
                        ollama_cfg.get("host", "http://127.0.0.1:11434"),
                        ollama_cfg.get("model", "llama2"),
                    )
            except Exception:
                for h in hypotheses:
                    h["natural_language"] = llm_generate(f"Suggest link: {h['from']} -> {h['to']}")
        else:
            for h in hypotheses:
                h["natural_language"] = llm_generate(f"Suggest link: {h['from']} -> {h['to']}")

    return hypotheses
