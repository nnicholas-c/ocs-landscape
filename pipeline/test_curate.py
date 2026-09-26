"""Regression check for the fuzzy_title subset-match bug (see pitfalls.md,
stage 2 retry): rapidfuzz token_set_ratio scores 100 whenever one normalized
title's tokens are a subset of the other's, which wrongly merged different
papers. cluster_records must also require token_sort_ratio >= 90 before
merging on fuzzy title.

Plain assert, no framework. Run with:
    .venv/bin/python -m pipeline.test_curate
"""
from pipeline.curate import cluster_records


def make(key, title, year, doi=None, arxiv_id=None):
    return key, {"title": title, "year": year, "doi": doi, "arxiv_id": arxiv_id}


def demo():
    # Real pair from the stage 2 checker report: token_set_ratio 100 (subset
    # match) but the titles are different papers, so token_sort_ratio (57.7)
    # must block the merge.
    subset_records = dict([
        make("openalex:W4327858904", "Integrated silicon photonic MEMS", 2023),
        make(
            "openalex:W4393174577",
            "Large-scale silicon photonic MEMS switch with flip-chip integrated CMOS drivers",
            2023,
        ),
    ])
    order = list(subset_records.keys())
    clusters, _ = cluster_records(subset_records, order)
    assert len(clusters) == 2, (
        f"subset-match titles should NOT merge, got clusters={clusters}"
    )

    # A genuine near-duplicate (whitespace/case only) must still merge.
    dup_records = dict([
        make("openalex:A", "Integrating microsecond circuit switching into the data center", 2013),
        make("openalex:B", "integrating   microsecond circuit switching into the data center", 2013),
    ])
    order2 = list(dup_records.keys())
    clusters2, _ = cluster_records(dup_records, order2)
    assert len(clusters2) == 1, (
        f"near-duplicate titles should merge, got clusters={clusters2}"
    )

    print("ok: subset-match titles stay split, near-duplicates still merge")


if __name__ == "__main__":
    demo()
