"""
Knowledge Graph Engine: SQLite-backed graph (nodes/edges).
"""
import os
import sqlite3


class KnowledgeGraph:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self) -> None:
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                mass REAL,
                activation REAL,
                state TEXT,
                metadata TEXT
            )"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS edges (
                from_id INTEGER,
                to_id INTEGER,
                type TEXT,
                weight REAL,
                FOREIGN KEY (from_id) REFERENCES nodes(id),
                FOREIGN KEY (to_id) REFERENCES nodes(id)
            )"""
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_nodes_label ON nodes(label)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_id)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_id)"
        )
        self.conn.commit()

    def add_node(
        self,
        label: str,
        mass: float = 1.0,
        activation: float = 0.0,
        state: str = "DORMANT",
        metadata: str = "",
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO nodes (label, mass, activation, state, metadata) VALUES (?, ?, ?, ?, ?)",
            (label, mass, activation, state, metadata),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_node_by_label(self, label: str) -> dict | None:
        cur = self.conn.execute(
            "SELECT * FROM nodes WHERE label = ? LIMIT 1", (label,)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def get_node(self, node_id: int) -> dict | None:
        cur = self.conn.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def add_edge(
        self, from_id: int, to_id: int, edge_type: str = "relates", weight: float = 1.0
    ) -> None:
        self.conn.execute(
            "INSERT INTO edges (from_id, to_id, type, weight) VALUES (?, ?, ?, ?)",
            (from_id, to_id, edge_type, weight),
        )
        self.conn.commit()

    def get_neighbors(self, node_id: int, direction: str = "out") -> list[dict]:
        if direction == "out":
            cur = self.conn.execute(
                "SELECT to_id AS neighbor_id FROM edges WHERE from_id = ?", (node_id,)
            )
        else:
            cur = self.conn.execute(
                "SELECT from_id AS neighbor_id FROM edges WHERE to_id = ?", (node_id,)
            )
        return [dict(r) for r in cur.fetchall()]

    def get_edges_from(self, node_id: int) -> list[dict]:
        cur = self.conn.execute(
            "SELECT from_id, to_id, type, weight FROM edges WHERE from_id = ?",
            (node_id,),
        )
        return [
            {"from_id": r[0], "to_id": r[1], "type": r[2], "weight": r[3]}
            for r in cur.fetchall()
        ]

    def get_all_edges(self) -> list[dict]:
        cur = self.conn.execute(
            "SELECT from_id, to_id, type, weight FROM edges"
        )
        return [
            {"from_id": r[0], "to_id": r[1], "type": r[2], "weight": r[3]}
            for r in cur.fetchall()
        ]

    def update_node_activation(self, node_id: int, activation: float) -> None:
        self.conn.execute(
            "UPDATE nodes SET activation = ? WHERE id = ?", (activation, node_id)
        )
        self.conn.commit()

    def update_node_state(self, node_id: int, state: str) -> None:
        self.conn.execute(
            "UPDATE nodes SET state = ? WHERE id = ?", (state, node_id)
        )
        self.conn.commit()

    def ingest_text(self, text: str) -> None:
        """Simple text parser: split on whitespace, add nodes, link sequential."""
        words = [w.strip() for w in text.split() if w.strip()]
        prev_id = None
        for word in words:
            existing = self.get_node_by_label(word)
            if existing:
                node_id = existing["id"]
            else:
                node_id = self.add_node(word)
            if prev_id is not None:
                self.add_edge(prev_id, node_id, "relates", 1.0)
            prev_id = node_id

    def to_json(self) -> dict:
        """Export nodes and edges as dicts for JSON serialization."""
        nodes_cur = self.conn.execute(
            "SELECT id, label, mass, activation, state, metadata FROM nodes"
        )
        edges_cur = self.conn.execute(
            "SELECT from_id, to_id, type, weight FROM edges"
        )
        nodes = [
            {
                "id": r[0],
                "label": r[1],
                "mass": r[2],
                "activation": r[3],
                "state": r[4],
                "metadata": r[5] or "",
            }
            for r in nodes_cur.fetchall()
        ]
        edges = [
            {"from_id": r[0], "to_id": r[1], "type": r[2], "weight": r[3]}
            for r in edges_cur.fetchall()
        ]
        return {"nodes": nodes, "edges": edges}

    def to_rust_graph(self, batch_size: int = 5000):
        """Load SQLite graph into Rust PyGraph (batched for low-RAM). Returns (PyGraph, sqlite_ids_by_rust_index)."""
        try:
            from bindings.rust_bindings import goat_ts_core
        except ImportError:
            goat_ts_core = None
        if goat_ts_core is None or not hasattr(goat_ts_core, "PyGraph"):
            return None, []
        PyGraph = goat_ts_core.PyGraph
        rg = PyGraph()
        sqlite_ids_by_rust_index = []
        offset = 0
        while True:
            rows = self.conn.execute(
                "SELECT id, label, mass, activation, state FROM nodes ORDER BY id LIMIT ? OFFSET ?",
                (batch_size, offset),
            ).fetchall()
            if not rows:
                break
            for row in rows:
                rg.add_node_with_activation(
                    row[1], float(row[2]), float(row[3]), row[4] or "DORMANT"
                )
                sqlite_ids_by_rust_index.append(row[0])
            offset += batch_size
        sqlite_to_rust = {sid: i for i, sid in enumerate(sqlite_ids_by_rust_index)}
        offset = 0
        while True:
            rows = self.conn.execute(
                "SELECT from_id, to_id, type, weight FROM edges LIMIT ? OFFSET ?",
                (batch_size, offset),
            ).fetchall()
            if not rows:
                break
            for row in rows:
                r_from = sqlite_to_rust.get(row[0])
                r_to = sqlite_to_rust.get(row[1])
                if r_from is not None and r_to is not None:
                    rg.add_edge(r_from, r_to, row[2] or "relates", float(row[3]))
            offset += batch_size
        return rg, sqlite_ids_by_rust_index

    def from_rust_graph(self, rg, sqlite_ids_by_rust_index: list) -> None:
        """Write back activations and states from Rust graph to SQLite."""
        if rg is None or not sqlite_ids_by_rust_index:
            return
        for rust_id in range(rg.node_count()):
            if rust_id >= len(sqlite_ids_by_rust_index):
                break
            sqlite_id = sqlite_ids_by_rust_index[rust_id]
            act = rg.get_node_activation(rust_id)
            state = rg.get_node_state(rust_id)
            if act is not None:
                self.update_node_activation(sqlite_id, act)
            if state is not None:
                self.update_node_state(sqlite_id, state)

    def close(self) -> None:
        self.conn.close()
