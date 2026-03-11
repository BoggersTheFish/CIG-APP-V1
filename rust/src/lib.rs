mod constraint_engine;
mod graph_engine;
mod similarity_engine;
mod wave_engine;

use graph_engine::Graph;
use pyo3::prelude::*;
use similarity_engine::find_similar as rust_find_similar;

#[pyclass]
struct PyGraph {
    inner: Graph,
}

#[pymethods]
impl PyGraph {
    #[new]
    fn new() -> Self {
        PyGraph {
            inner: Graph::new(),
        }
    }

    fn add_node(&mut self, label: String) -> u32 {
        self.inner.add_node(label)
    }

    fn add_node_with_activation(
        &mut self,
        label: String,
        mass: f64,
        activation: f64,
        state: String,
    ) -> u32 {
        self.inner.add_node_with_activation(label, mass, activation, state)
    }

    fn add_edge(&mut self, from_id: u32, to_id: u32, edge_type: String, weight: f64) {
        self.inner.add_edge(from_id, to_id, edge_type, weight);
    }

    fn node_count(&self) -> usize {
        self.inner.node_count()
    }

    fn get_node_activation(&self, id: u32) -> Option<f64> {
        self.inner.get_node(id).map(|n| n.activation)
    }

    fn get_node_state(&self, id: u32) -> Option<String> {
        self.inner.get_node(id).map(|n| n.state.clone())
    }

    fn get_node_label(&self, id: u32) -> Option<String> {
        self.inner.get_node(id).map(|n| n.label.clone())
    }

    #[pyo3(signature = (seed_id, ticks, decay, activation_threshold, activation_fn="linear", use_frontier=false, use_convergence=false, max_ticks=100, epsilon=1e-5))]
    fn full_ts_cycle(
        &mut self,
        seed_id: u32,
        ticks: u32,
        decay: f64,
        activation_threshold: f64,
        activation_fn: &str,
        use_frontier: bool,
        use_convergence: bool,
        max_ticks: u32,
        epsilon: f64,
    ) {
        wave_engine::full_ts_cycle(
            &mut self.inner,
            seed_id,
            ticks,
            decay,
            activation_threshold,
            activation_fn,
            use_frontier,
            use_convergence,
            max_ticks,
            epsilon,
        );
    }

    fn compute_influence(&self) -> f64 {
        wave_engine::compute_influence(&self.inner)
    }

    fn find_similar(&self, id: u32, threshold: f64, use_activation_weight: bool) -> Vec<u32> {
        rust_find_similar(&self.inner, id, threshold, use_activation_weight)
    }
}

#[pymodule]
fn goat_ts_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyGraph>()?;
    Ok(())
}
