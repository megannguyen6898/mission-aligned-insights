import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from backend.app.ingest.hash import canonical_row_hash


def test_hash_stability():
    row_one = {"b": "2", "a": "1"}
    row_two = {"a": "1", "b": "2"}

    assert canonical_row_hash(row_one) == canonical_row_hash(row_two)


def test_whitespace_and_case_tolerance():
    row_one = {"name": " Alice "}
    row_two = {"name": "alice"}

    assert canonical_row_hash(row_one) == canonical_row_hash(row_two)


def test_only_changed_rows_update():
    original = [
        {"id": 1, "name": "alice"},
        {"id": 2, "name": "bob"},
    ]
    original_hashes = {r["id"]: canonical_row_hash(r) for r in original}

    updated = [
        {"id": 1, "name": " Alice "},  # unchanged after canonicalization
        {"id": 2, "name": "Bobby"},  # changed
    ]
    changed = [
        row["id"]
        for row in updated
        if canonical_row_hash(row) != original_hashes.get(row["id"])
    ]

    assert changed == [2]

