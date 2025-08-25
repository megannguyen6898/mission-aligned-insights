from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from backend.app.ingest.mapping_loader import load_mapping

EXPECTED_MAPPING = {
    "project_info": {
        "project id": "project_id",
        "project name": "name",
        "org name": "org_name",
        "start date": "start_date",
        "end date": "end_date",
        "country": "country",
        "region": "region",
        "sdg goal": "sdg_goal",
        "notes": "notes",
    },
    "activities": {
        "project id": "project_id",
        "date": "date",
        "activity type": "activity_type",
        "activity name": "activity_name",
        "beneficiaries reached": "beneficiaries_reached",
        "location": "location",
        "notes": "notes",
    },
    "outcomes": {
        "project id": "project_id",
        "date": "date",
        "outcome metric": "outcome_metric",
        "value": "value",
        "unit": "unit",
        "method of measurement": "method",
        "notes": "notes",
    },
    "funding_resources": {
        "project id": "project_id",
        "date": "date",
        "funding source": "funding_source",
        "funding received": "received",
        "funding spent": "spent",
        "volunteer hours": "volunteer_hours",
        "staff hours": "staff_hours",
        "notes": "notes",
    },
    "beneficiaries": {
        "project id": "project_id",
        "date": "date",
        "beneficiary group": "group",
        "count": "count",
        "demographic info": "demographic_info",
        "location": "location",
        "notes": "notes",
    },
}


def test_load_mapping_excel_v1():
    mapping = load_mapping()
    assert mapping == EXPECTED_MAPPING
