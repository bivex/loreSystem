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