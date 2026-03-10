import subprocess


def test_writeback_bootstrap_script_prints_help():
    result = subprocess.run(
        ["bash", "mirofish_writeback_bootstrap.sh", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "loreSystem write-back API" in result.stdout
    assert "MiroFish backend" in result.stdout
    assert "MiroFish frontend" in result.stdout


def test_writeback_bootstrap_script_supports_dry_run_with_custom_ports(tmp_path):
    env_file = tmp_path / "mirofish.env"
    env_file.write_text("LLM_API_KEY=dummy\n", encoding="utf-8")
    db_path = tmp_path / "writeback.db"

    result = subprocess.run(
        [
            "bash",
            "mirofish_writeback_bootstrap.sh",
            "--dry-run",
            "--mirofish-env",
            str(env_file),
            "--db",
            str(db_path),
            "--writeback-port",
            "18080",
            "--backend-port",
            "15001",
            "--frontend-port",
            "13000",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "writeback_url: http://127.0.0.1:18080" in result.stdout
    assert "backend_url: http://127.0.0.1:15001" in result.stdout
    assert "frontend_url: http://127.0.0.1:13000" in result.stdout
    assert "MIROFISH_WRITEBACK_BASE_URL=http://127.0.0.1:18080" in result.stdout
    assert "VITE_API_BASE_URL=http://127.0.0.1:15001" in result.stdout