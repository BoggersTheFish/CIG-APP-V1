use crate::graph_engine::Graph;
use rayon::prelude::*;

const PARALLEL_THRESHOLD: usize = 100;

/// Spread activation from active nodes to neighbors (one tick).
pub fn propagate_tick(graph: &mut Graph, decay: f64) {
    let current: Vec<f64> = graph.nodes.iter().map(|n| n.activation).collect();
    let edges = &graph.edges;
    let n = graph.nodes.len();

    let next_activation: Vec<f64> = if n >= PARALLEL_THRESHOLD {
        (0..n)
            .into_par_iter()
            .map(|i| {
                let mut new_act = current[i];
                for edge in edges.iter().filter(|e| e.to_id == i as u32) {
                    let from_idx = edge.from_id as usize;
                    if from_idx < n && current[from_idx] > 0.0 {
                        new_act += current[from_idx] * edge.weight * decay;
                    }
                }
                new_act
            })
            .collect()
    } else {
        let mut next = current.clone();
        for (id, &act) in current.iter().enumerate() {
            if act <= 0.0 {
                continue;
            }
            for edge in edges.iter().filter(|e| e.from_id == id as u32) {
                if let Some(a) = next.get_mut(edge.to_id as usize) {
                    *a += act * edge.weight * decay;
                }
            }
        }
        next
    };

    for (i, node) in graph.nodes.iter_mut().enumerate() {
        if i < next_activation.len() {
            node.activation = next_activation[i];
        }
    }
}

/// Run propagation for multiple ticks.
pub fn propagate(graph: &mut Graph, seed_id: u32, ticks: u32, decay: f64) {
    if let Some(node) = graph.nodes.get_mut(seed_id as usize) {
        node.activation = 1.0;
    }
    for _ in 0..ticks {
        propagate_tick(graph, decay);
    }
}

/// Apply decay to all activations.
pub fn apply_decay(graph: &mut Graph, decay: f64) {
    for node in &mut graph.nodes {
        node.activation *= decay;
    }
}

/// Update node states from activation levels.
pub fn update_states(graph: &mut Graph, threshold_low: f64, threshold_high: f64) {
    for node in &mut graph.nodes {
        node.state = if node.activation < threshold_low {
            "DORMANT".to_string()
        } else if node.activation >= threshold_high {
            "ACTIVE".to_string()
        } else {
            "DEEP".to_string()
        };
    }
}

/// Full TS cycle: propagate, resolve constraints, decay, update states.
pub fn full_ts_cycle(
    graph: &mut Graph,
    seed_id: u32,
    ticks: u32,
    decay: f64,
    activation_threshold: f64,
) {
    use crate::constraint_engine::resolve_constraints;
    if let Some(node) = graph.nodes.get_mut(seed_id as usize) {
        node.activation = 1.0;
    }
    let threshold_low = 0.1;
    let threshold_high = activation_threshold;
    for _ in 0..ticks {
        propagate_tick(graph, decay);
        resolve_constraints(graph);
        apply_decay(graph, decay);
        update_states(graph, threshold_low, threshold_high);
    }
}

/// Sum of all activations (influence score).
pub fn compute_influence(graph: &Graph) -> f64 {
    graph.nodes.iter().map(|n| n.activation).sum()
}

/// Run propagation with convergence: stop when delta < epsilon.
pub fn propagate_until_convergence(
    graph: &mut Graph,
    seed_id: u32,
    max_ticks: u32,
    decay: f64,
    epsilon: f64,
) -> u32 {
    if let Some(node) = graph.nodes.get_mut(seed_id as usize) {
        node.activation = 1.0;
    }
    let mut tick = 0u32;
    for _ in 0..max_ticks {
        let prev: Vec<f64> = graph.nodes.iter().map(|n| n.activation).collect();
        propagate_tick(graph, decay);
        tick += 1;
        let delta: f64 = graph
            .nodes
            .iter()
            .zip(prev.iter())
            .map(|(n, p)| (n.activation - p).abs())
            .sum();
        if delta < epsilon {
            break;
        }
    }
    tick
}
