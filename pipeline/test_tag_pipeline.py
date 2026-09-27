"""Self-check for tag_export/tag_import. Not a deliverable (CLAUDE.md data contract).

Run: .venv/bin/python -m pipeline.test_tag_pipeline
"""
import json
import sqlite3
import tempfile
from pathlib import Path

from pipeline import tag_export, tag_import


def test_first_words():
    assert tag_export.first_words("a b c d", n=2) == "a b"
    assert tag_export.first_words(None) == ""
    assert tag_export.first_words("only two", n=5) == "only two"


def test_next_batch_num_resumes_and_skips_out_json():
    with tempfile.TemporaryDirectory() as tmp:
        tag_export.WORK_DIR = Path(tmp)
        (tag_export.WORK_DIR / "relevance_batch_001.json").write_text("[]")
        (tag_export.WORK_DIR / "relevance_batch_002.json").write_text("[]")
        (tag_export.WORK_DIR / "relevance_batch_002.out.json").write_text("[]")  # must not count as 3
        assert tag_export.next_batch_num("relevance", low=1) == 3

        (tag_export.WORK_DIR / "tag_batch_005.json").write_text("[]")
        (tag_export.WORK_DIR / "tag_batch_901.json").write_text("[]")
        assert tag_export.next_batch_num("tag", low=1, high=899) == 6  # ignores the 9xx range
        assert tag_export.next_batch_num("tag", low=901, high=999) == 902
        assert tag_export.next_batch_num("tag", low=901, high=999) != 901  # doesn't restart at 901


def test_relevance_export_dedups_across_files_and_skips_scored():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tag_export.RAW_DIR = tmp
        tag_export.WORK_DIR = tmp / "work"
        tag_export.RELEVANCE_CSV = tmp / "relevance.csv"

        rec_a = {"record_key": "openalex:A", "source": "openalex", "title": "T", "year": 2020, "venue": "V", "abstract": " ".join(f"w{i}" for i in range(200))}
        rec_b = {"record_key": "arxiv:B", "source": "arxiv", "title": "T2", "year": 2021, "venue": "arXiv", "abstract": "short"}
        (tmp / "one.jsonl").write_text(json.dumps(rec_a) + "\n")
        # rec_a repeated in a second file (as with smoke + full overlap) and rec_b once
        (tmp / "two.jsonl").write_text(json.dumps(rec_a) + "\n" + json.dumps(rec_b) + "\n")
        (tmp / "relevance.csv").write_text("record_key,source,score,adjacent_field,reason\nopenalex:A,openalex,3,,already scored\n")

        written, n = tag_export.export_relevance()
        assert n == 1  # A already scored, B is new, A's duplicate line doesn't double-count
        assert len(written) == 1
        batch = json.loads(written[0].read_text())
        assert batch[0]["record_key"] == "arxiv:B"
        assert len(batch[0]["abstract"].split()) <= 120
        assert tag_export.export_relevance() == ([], 0)  # pending batch keys are not re-exported


def test_full_export_skips_tagged_and_pending_unless_only():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tag_export.WORK_DIR = tmp / "work"
        tag_export.DB_PATH = tmp / "papers.sqlite"

        con = sqlite3.connect(tag_export.DB_PATH)
        con.execute("CREATE TABLE papers (paper_id TEXT PRIMARY KEY, title TEXT, year INTEGER, venue TEXT, "
                     "abstract TEXT, extended_set INTEGER)")
        con.execute("CREATE TABLE tags (paper_id TEXT PRIMARY KEY)")
        for pid, ext in [("TAGGED", 1), ("PENDING", 1), ("NEW", 1), ("NOT_EXT", 0)]:
            con.execute("INSERT INTO papers VALUES (?, 'T', 2020, 'V', 'A', ?)", (pid, ext))
        con.execute("INSERT INTO tags VALUES ('TAGGED')")
        con.commit()
        con.close()
        tag_export.WORK_DIR.mkdir()
        (tag_export.WORK_DIR / "tag_batch_001.json").write_text(json.dumps([{"paper_id": "PENDING"}]))

        written, n = tag_export.export_full()
        assert n == 1 and [p.name for p in written] == ["tag_batch_002.json"]
        assert [r["paper_id"] for r in json.loads(written[0].read_text())] == ["NEW"]
        assert tag_export.export_full() == ([], 0)  # second run exports nothing

        only = tmp / "only.txt"
        only.write_text("TAGGED\nPENDING\n")
        written, n = tag_export.export_full(only)  # --only still retags whatever it names
        assert n == 2 and [p.name for p in written] == ["tag_batch_901.json"]


def test_evidence_ok():
    assert tag_import.evidence_ok("We build a switch.", "Intro. We build a switch. End.", "Title")
    assert not tag_import.evidence_ok("not in there", "Intro. We build a switch.", "Title")
    assert tag_import.evidence_ok("Exact Title", None, "Exact Title")
    assert not tag_import.evidence_ok("", "abstract text", "Title")


def test_relevance_import_idempotent_and_upserts():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tag_import.RAW_DIR = tmp
        tag_import.WORK_DIR = tmp
        tag_import.RELEVANCE_CSV = tmp / "relevance.csv"

        batch_out = [
            {"record_key": "openalex:A", "score": 3, "adjacent_field": None, "reason": "builds a switch"},
            {"record_key": "arxiv:B", "score": 1, "adjacent_field": "silicon_photonics", "reason": "adjacent"},
        ]
        (tmp / "relevance_batch_001.out.json").write_text(json.dumps(batch_out))

        n1 = tag_import.import_relevance()
        rows1 = (tmp / "relevance.csv").read_text()
        n2 = tag_import.import_relevance()  # rerun, nothing changed
        rows2 = (tmp / "relevance.csv").read_text()
        assert n1 == n2 == 2
        assert rows1 == rows2
        assert "openalex:A,openalex,3" in rows1
        assert "arxiv:B,arxiv,1,silicon_photonics" in rows1


def test_full_import_loads_all_and_flags_failures():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tag_import.WORK_DIR = tmp
        tag_import.DB_PATH = tmp / "papers.sqlite"
        tag_import.FAILURES_PATH = tmp / "tag_failures.json"

        con = sqlite3.connect(tag_import.DB_PATH)
        con.execute("CREATE TABLE papers (paper_id TEXT PRIMARY KEY, title TEXT, abstract TEXT)")
        con.execute("CREATE TABLE tags (paper_id TEXT PRIMARY KEY, tech_route TEXT, tech_route_secondary TEXT, "
                     "integration TEXT, trl_band TEXT, ai_dc_fit TEXT, adjacent_field TEXT, evidence_span TEXT, "
                     "confidence TEXT, tagged_at TEXT)")
        con.execute("INSERT INTO papers VALUES ('P1', 'Title One', 'We build an optical switch here.')")
        con.execute("INSERT INTO papers VALUES ('P2', 'Null Abstract Title', NULL)")
        con.commit()
        con.close()

        batch1 = [{"paper_id": "P1", "tech_route": "mems_3d", "tech_route_secondary": None, "integration": "free_space_bulk",
                   "trl_band": "lab", "ai_dc_fit": "direct", "adjacent_field": None,
                   "evidence_span": "We build an optical switch here.", "confidence": "high"}]
        batch2 = [{"paper_id": "P2", "tech_route": "unclear", "tech_route_secondary": None, "integration": "unclear",
                   "trl_band": "unclear", "ai_dc_fit": "unclear", "adjacent_field": None,
                   "evidence_span": "wrong text", "confidence": "low"}]
        (tmp / "tag_batch_001.out.json").write_text(json.dumps(batch1))
        (tmp / "tag_batch_002.out.json").write_text(json.dumps(batch2))

        n, n_fail = tag_import.import_full()
        assert n == 2
        assert n_fail == 1  # P2's evidence_span doesn't match its null-abstract title

        con = sqlite3.connect(tag_import.DB_PATH)
        rows = con.execute("SELECT paper_id, tech_route FROM tags ORDER BY paper_id").fetchall()
        con.close()
        assert rows == [("P1", "mems_3d"), ("P2", "unclear")]  # both loaded despite P2's failure


def run_all():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)} checks passed")


if __name__ == "__main__":
    run_all()
