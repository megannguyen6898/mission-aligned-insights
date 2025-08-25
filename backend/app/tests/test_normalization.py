from pathlib import Path
import sys

import pandas as pd

# Add repository root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

from backend.app.ingest.normalize import normalize_row
from backend.app.ingest.mapping_loader import load_mapping
import importlib
import backend.app.ingest.normalize as normalize_module


def test_normalize_sample_valid():
    root = Path(__file__).resolve().parents[3]
    mapping = load_mapping()

    xls = pd.ExcelFile(root / "fixtures" / "sample_valid.xlsx")

    activities = pd.read_excel(xls, "Activities")
    row = activities.iloc[0].to_dict()
    row["Activity Type"] = "workshop"  # ensure category normalization
    norm, errors = normalize_row(row, "activities", mapping=mapping)
    assert errors is None
    assert norm["activity_type"] == "Workshop"
    assert norm["beneficiaries_reached"] == 30
    assert norm["date"].isoformat() == "2025-06-01"

    beneficiaries = pd.read_excel(xls, "Beneficiaries")
    row = beneficiaries.iloc[0].to_dict()
    norm, errors = normalize_row(row, "beneficiaries", mapping=mapping)
    assert errors is None
    assert norm["date"].isoformat() == "2025-06-30"


def test_normalize_bad_types():
    root = Path(__file__).resolve().parents[3]
    mapping = load_mapping()

    xls = pd.ExcelFile(root / "fixtures" / "bad_types.xlsx")

    activities = pd.read_excel(xls, "Activities")
    row = activities.iloc[0].to_dict()
    norm, errors = normalize_row(row, "activities", mapping=mapping)
    assert errors == {"invalid": ["beneficiaries_reached"]}
    assert norm["beneficiaries_reached"] is None

    outcomes = pd.read_excel(xls, "Outcomes")
    row = outcomes.iloc[0].to_dict()
    norm, errors = normalize_row(row, "outcomes", mapping=mapping)
    assert errors == {"invalid": ["value"]}
    assert norm["value"] is None


def test_pii_redaction(monkeypatch):
    mapping = {"activities": {"notes": "notes"}}
    row = {"notes": "Email me at test@example.com or call +1 555-123-4567"}

    monkeypatch.setenv("PII_REDACTION_ENABLED", "true")
    importlib.reload(normalize_module)
    norm, _ = normalize_module.normalize_row(row, "activities", mapping=mapping)
    assert norm["notes"] == "Email me at [REDACTED] or call [REDACTED]"

    monkeypatch.setenv("PII_REDACTION_ENABLED", "false")
    importlib.reload(normalize_module)
    norm, _ = normalize_module.normalize_row(row, "activities", mapping=mapping)
    assert norm["notes"] == row["notes"]
