use std::collections::HashSet;
use crate::graph_engine::Graph;

fn char_bigrams(s: &str) -> HashSet<String> {
    let s = s.to_lowercase();
    let mut set = HashSet::new();
    for i in 0..s.len().saturating_sub(1) {
        let chunk: String = s.chars().skip(i).take(2).collect();
        if chunk.len() == 2 {
            set.insert(chunk);
        }
    }
    if s.len() == 1 {
        set.insert(s.to_string());
    }
    set
}

/// Jaccard similarity on character bigrams (0.0 to 1.0).
pub fn jaccard(a: &str, b: &str) -> f64 {
    let sa = char_bigrams(a);
    let sb = char_bigrams(b);
    if sa.is_empty() && sb.is_empty() {
        return 1.0;
    }
    if sa.is_empty() || sb.is_empty() {
        return 0.0;
    }
    let inter = sa.intersection(&sb).count();
    let union = sa.union(&sb).count();
    if union == 0 {
        0.0
    } else {
        inter as f64 / union as f64
    }
}

/// Find node IDs with label similarity above threshold. Optionally weight by activation.
pub fn find_similar(graph: &Graph, id: u32, threshold: f64, use_activation_weight: bool) -> Vec<u32> {
    let label = graph.nodes.get(id as usize).map(|n| n.label.as_str()).unwrap_or("");
    graph
        .nodes
        .iter()
        .enumerate()
        .filter_map(|(i, n)| {
            if i as u32 == id {
                return None;
            }
            let sim = jaccard(label, &n.label);
            let thresh = if use_activation_weight {
                threshold * (n.activation.max(0.1))
            } else {
                threshold
            };
            if sim > thresh {
                Some(i as u32)
            } else {
                None
            }
        })
        .collect()
}
