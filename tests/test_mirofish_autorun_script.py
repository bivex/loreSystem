import json
import sqlite3
import subprocess
import sys


def test_autorun_script_resets_db_and_runs_live_smoke(tmp_path):
    db_path = tmp_path / "autorun.db"
    db_path.write_text("not-a-sqlite-db", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/autorun_mirofish_live_smoke.py", "--db", str(db_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["smoke"]["promoted_count"] == 3
    assert payload["db_summary"]["counts"]["run_subjects"] == 5
    assert payload["db_summary"]["counts"]["entity_run_links"] == 3
    assert any(item["subject_ref"] == "org:town_criers" for item in payload["db_summary"]["subjects"])

    conn = sqlite3.connect(db_path)
    try:
        run_count = conn.execute("SELECT COUNT(*) FROM mirofish_scenario_runs").fetchone()[0]
    finally:
        conn.close()
    assert run_count == 1


def test_autorun_script_is_idempotent_across_two_runs_on_same_db(tmp_path):
    db_path = tmp_path / "autorun-twice.db"

    first = subprocess.run(
        [sys.executable, "scripts/autorun_mirofish_live_smoke.py", "--db", str(db_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    second = subprocess.run(
        [sys.executable, "scripts/autorun_mirofish_live_smoke.py", "--db", str(db_path), "--no-reset-db"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr

    first_payload = json.loads(first.stdout)
    second_payload = json.loads(second.stdout)

    assert first_payload["success"] is True
    assert second_payload["success"] is True
    assert first_payload["db_summary"]["counts"]["canonical_entities"] == 3
    assert second_payload["db_summary"]["counts"]["canonical_entities"] == 3
    assert first_payload["db_summary"]["counts"]["entity_run_links"] == 3
    assert second_payload["db_summary"]["counts"]["entity_run_links"] == 3
    assert second_payload["db_summary"]["counts"]["run_subjects"] == 5

    conn = sqlite3.connect(db_path)
    try:
        canonical_count = conn.execute("SELECT COUNT(*) FROM mirofish_canonical_entities").fetchone()[0]
        run_link_count = conn.execute("SELECT COUNT(*) FROM mirofish_entity_run_links").fetchone()[0]
        candidate_count = conn.execute("SELECT COUNT(*) FROM mirofish_candidate_deltas").fetchone()[0]
    finally:
        conn.close()

    assert canonical_count == 3
    assert run_link_count == 3
    assert candidate_count == 3