use crate::graph_engine::Graph;

/// Resolve constraints: e.g. conflict edges dampen activation.
pub fn resolve_constraints(graph: &mut Graph) {
    let mut act: Vec<f64> = graph.nodes.iter().map(|n| n.activation).collect();
    for edge in &graph.edges {
        if edge.edge_type == "conflict" {
            let from_idx = edge.from_id as usize;
            let to_idx = edge.to_id as usize;
            if from_idx < act.len() && to_idx < act.len() {
                let avg = (act[from_idx] + act[to_idx]) / 2.0;
                act[from_idx] = avg * 0.8;
                act[to_idx] = avg * 0.8;
            }
        }
    }
    for (i, node) in graph.nodes.iter_mut().enumerate() {
        if i < act.len() {
            node.activation = act[i];
        }
    }
}
