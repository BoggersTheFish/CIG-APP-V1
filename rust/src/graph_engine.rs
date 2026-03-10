#[derive(Clone, Debug)]
pub struct Node {
    pub id: u32,
    pub label: String,
    pub mass: f64,
    pub activation: f64,
    pub state: String,
}

#[derive(Clone, Debug)]
pub struct Edge {
    pub from_id: u32,
    pub to_id: u32,
    pub edge_type: String,
    pub weight: f64,
}

pub struct Graph {
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
}

impl Graph {
    pub fn new() -> Self {
        Graph {
            nodes: vec![],
            edges: vec![],
        }
    }

    pub fn add_node(&mut self, label: String) -> u32 {
        let id = self.nodes.len() as u32;
        self.nodes.push(Node {
            id,
            label,
            mass: 1.0,
            activation: 0.0,
            state: "DORMANT".to_string(),
        });
        id
    }

    pub fn add_node_with_activation(&mut self, label: String, mass: f64, activation: f64, state: String) -> u32 {
        let id = self.nodes.len() as u32;
        self.nodes.push(Node {
            id,
            label,
            mass,
            activation,
            state,
        });
        id
    }

    pub fn add_edge(&mut self, from_id: u32, to_id: u32, edge_type: String, weight: f64) {
        self.edges.push(Edge {
            from_id,
            to_id,
            edge_type,
            weight,
        });
    }

    pub fn node_count(&self) -> usize {
        self.nodes.len()
    }

    pub fn get_node(&self, id: u32) -> Option<&Node> {
        self.nodes.get(id as usize)
    }

    pub fn get_node_mut(&mut self, id: u32) -> Option<&mut Node> {
        self.nodes.get_mut(id as usize)
    }

    pub fn neighbors_out(&self, id: u32) -> Vec<(u32, f64)> {
        self.edges
            .iter()
            .filter(|e| e.from_id == id)
            .map(|e| (e.to_id, e.weight))
            .collect()
    }
}

impl Default for Graph {
    fn default() -> Self {
        Self::new()
    }
}
