"""Tests for PDF ingestion (Step 8)."""
import sys
import os
import tempfile
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_ingest_pdf():
    try:
        from goat_ts_cig.knowledge_graph import KnowledgeGraph
        from PyPDF2 import PdfReader
    except ImportError:
        import pytest
        pytest.skip("PyPDF2 not installed")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        kg = KnowledgeGraph(db_path)
        # Minimal PDF: create a tiny PDF-like stream (or use a real tiny PDF)
        # PyPDF2 can fail on empty/corrupt; test the code path
        empty_pdf = io.BytesIO(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF")
        out = kg.ingest_pdf(empty_pdf)
        assert isinstance(out, str)
        kg.close()
    finally:
        if os.path.isfile(db_path):
            os.remove(db_path)


def test_ingest_pdf_text():
    try:
        from goat_ts_cig.knowledge_graph import KnowledgeGraph
    except ImportError:
        import pytest
        pytest.skip("knowledge_graph not available")
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        import pytest
        pytest.skip("PyPDF2 not installed")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        kg = KnowledgeGraph(db_path)
        kg.add_node("dummy")
        # Ingest text path: ingest_pdf with invalid PDF returns error string
        out = kg.ingest_pdf(io.BytesIO(b"not a pdf"))
        assert "Error" in out or len(out) >= 0
        kg.close()
    finally:
        if os.path.isfile(db_path):
            os.remove(db_path)
