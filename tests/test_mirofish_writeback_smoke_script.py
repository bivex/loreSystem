import json
import subprocess
import sys


def test_smoke_script_runs_full_review_promote_flow(tmp_path):
    db_path = tmp_path / "smoke.db"
    result = subprocess.run(
        [sys.executable, "scripts/smoke_mirofish_writeback_workflow.py", "--db", str(db_path), "--keep-db"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["candidate_count"] == 3
    assert payload["promoted_count"] == 3
    assert sorted(payload["canonical_types"]) == ["CharacterRelationship", "Event", "Rumor"]
    assert sorted(item["status"] for item in payload["promotions"]) == ["promoted", "promoted", "promoted"]