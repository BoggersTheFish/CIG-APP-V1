"""
Knowledge Graph Engine: SQLite-backed graph (nodes/edges).
Optional: sqlite-vss for vector search when vector.enabled.
"""
import os
import sqlite3
import struct


def _vector_extension_available() -> bool:
    try:
        import sqlite_vss  # noqa: F401
        return True
    except Exception:
        return False


class KnowledgeGraph:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._vss_loaded = False
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
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS vectors (id INTEGER PRIMARY KEY, embedding BLOB)"
        )
        self.conn.commit()

    def _ensure_vss(self) -> bool:
        if self._vss_loaded:
            return True
        if not _vector_extension_available():
            return False
        try:
            import sqlite_vss
            self.conn.enable_load_extension(True)
            sqlite_vss.load(self.conn)
            self.conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS vss_embed USING vss0(embedding(384))"
            )
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS vector_node_map (node_id INTEGER PRIMARY KEY, vss_rowid INTEGER)"
            )
            self.conn.commit()
            self._vss_loaded = True
            return True
        except Exception:
            return False

    def add_vector(self, node_id: int, embedding: list[float]) -> None:
        """Store or replace vector for node_id. Requires sqlite-vss and 384-dim embedding."""
        if not self._ensure_vss() or len(embedding) != 384:
            return
        blob = struct.pack(f"{len(embedding)}f", *embedding)
        cur = self.conn.execute("SELECT vss_rowid FROM vector_node_map WHERE node_id = ?", (node_id,))
        row = cur.fetchone()
        if row:
            self.conn.execute("DELETE FROM vss_embed WHERE rowid = ?", (row[0],))
        self.conn.execute("INSERT INTO vss_embed(embedding) VALUES (?)", (blob,))
        vss_rowid = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        self.conn.execute(
            "INSERT OR REPLACE INTO vector_node_map (node_id, vss_rowid) VALUES (?, ?)",
            (node_id, vss_rowid),
        )
        self.conn.execute(
            "INSERT OR REPLACE INTO vectors (id, embedding) VALUES (?, ?)",
            (node_id, blob),
        )
        self.conn.commit()

    def query_similar_vectors(self, embedding: list[float], limit: int = 10) -> list[tuple[int, float]]:
        """Return list of (node_id, distance) for nearest vectors. Requires sqlite-vss."""
        if not self._ensure_vss() or len(embedding) != 384:
            return []
        blob = struct.pack(f"{len(embedding)}f", *embedding)
        try:
            cur = self.conn.execute(
                "SELECT rowid, distance FROM vss_embed WHERE vss_search(embedding, ?) LIMIT ?",
                (blob, limit),
            )
            rows = cur.fetchall()
        except Exception:
            return []
        out = []
        for vss_rowid, dist in rows:
            r = self.conn.execute(
                "SELECT node_id FROM vector_node_map WHERE vss_rowid = ?", (vss_rowid,)
            ).fetchone()
            if r:
                out.append((r[0], float(dist)))
        return out

    def get_embedding(self, node_id: int) -> list[float] | None:
        """Return 384-d embedding for node_id if stored, else None."""
        cur = self.conn.execute("SELECT embedding FROM vectors WHERE id = ?", (node_id,))
        row = cur.fetchone()
        if not row or not row[0]:
            return None
        blob = row[0]
        n = len(blob) // 4  # float32
        return list(struct.unpack(f"{n}f", blob))

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

    def ingest_pdf(self, file) -> str:
        """
        Extract text from PDF and ingest via ingest_text.
        file: path (str) or file-like with .read(). Returns extracted text or error message.
        """
        try:
            from PyPDF2 import PdfReader
            if hasattr(file, "read"):
                reader = PdfReader(file)
            else:
                reader = PdfReader(file)
            text = "".join(
                (page.extract_text() or "") for page in reader.pages
            )
            if text.strip():
                self.ingest_text(text.strip())
            return text.strip() or "(no text extracted)"
        except Exception as e:
            return f"Error: {e}"

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
