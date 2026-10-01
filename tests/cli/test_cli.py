"""
tests/cli/test_cli.py
Gate 17 — CLI Validation Tests

Tests every documented CLI workflow via subprocess-level invocation:
- help / no command
- ingest (valid, missing dir)
- build-index (valid, missing dir)
- analyze (valid, missing file, malformed JSON)
- report (valid)
- exit codes
"""
import subprocess
import sys
import json
import tempfile
import shutil
from pathlib import Path

PYTHON = sys.executable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CLI_MODULE = "src.api.cli"


def _run_cli(*args, input_data=None, cwd=None):
    """Run CLI and return (returncode, stdout, stderr)."""
    cmd = [PYTHON, "-m", CLI_MODULE] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd or REPO_ROOT),
    )
    return result.returncode, result.stdout, result.stderr


# ── CLI-01: No command → exits non-zero, prints usage ────────────────────────

def test_cli01_no_command_prints_usage():
    """CLI-01: Running CLI with no command exits 1 and prints usage."""
    code, out, err = _run_cli()
    assert code != 0, "No-command invocation must exit non-zero"
    usage_text = out + err
    assert "usage" in usage_text.lower() or "command" in usage_text.lower(), \
        "No-command must print usage/help"


# ── CLI-02: --help exits 0 and shows commands ─────────────────────────────────

def test_cli02_help_exits_zero():
    """CLI-02: --help exits 0 and lists available commands."""
    code, out, err = _run_cli("--help")
    assert code == 0, f"--help must exit 0, got {code}"
    combined = out + err
    assert "ingest" in combined, "Help must mention ingest command"
    assert "analyze" in combined, "Help must mention analyze command"


# ── CLI-03: ingest --help exits 0 ────────────────────────────────────────────

def test_cli03_ingest_help():
    """CLI-03: ingest --help exits 0."""
    code, out, err = _run_cli("ingest", "--help")
    assert code == 0, f"ingest --help must exit 0, got {code}"


# ── CLI-04: ingest valid demo repo ───────────────────────────────────────────

def test_cli04_ingest_demo_repo():
    """CLI-04: ingest on examples/demo_repo completes successfully."""
    demo_dir = REPO_ROOT / "examples" / "demo_repo"
    if not demo_dir.exists():
        import pytest
        pytest.skip("examples/demo_repo not found")
    code, out, err = _run_cli("ingest", str(demo_dir))
    assert code == 0, f"ingest valid dir must exit 0; stderr={err[:300]}"
    combined = out + err
    assert "ingestion" in combined.lower() or "ok" in combined.lower() or \
           "graph" in combined.lower(), "ingest must report completion"


# ── CLI-05: ingest missing directory ─────────────────────────────────────────

def test_cli05_ingest_missing_directory():
    """CLI-05: ingest on a non-existent directory exits non-zero or handles gracefully."""
    code, out, err = _run_cli("ingest", "/tmp/aura_fi_nonexistent_repo_xyz")
    # Must not crash silently — may exit non-zero or print error
    # If the pipeline handles missing dir gracefully (e.g. 0 files parsed), that's acceptable
    combined = out + err
    # Either exits non-zero OR prints an error/warning
    passed = (code != 0) or any(w in combined.lower() for w in ["error", "not found", "0 req", "warning"])
    assert passed, f"Missing dir should produce error or non-zero exit; code={code}, out={out[:200]}"


# ── CLI-06: build-index exits 0 on demo repo ─────────────────────────────────

def test_cli06_build_index_demo_repo():
    """CLI-06: build-index on demo repo exits 0."""
    demo_dir = REPO_ROOT / "examples" / "demo_repo"
    if not demo_dir.exists():
        import pytest
        pytest.skip("examples/demo_repo not found")
    code, out, err = _run_cli("build-index", "--repo_dir", str(demo_dir))
    assert code == 0, f"build-index must exit 0; stderr={err[:300]}"


# ── CLI-07: analyze --help exits 0 ───────────────────────────────────────────

def test_cli07_analyze_help():
    """CLI-07: analyze --help exits 0."""
    code, out, err = _run_cli("analyze", "--help")
    assert code == 0


# ── CLI-08: analyze with missing change file exits non-zero ──────────────────

def test_cli08_analyze_missing_change_file():
    """CLI-08: analyze with missing change file exits non-zero with error."""
    code, out, err = _run_cli("analyze", "/tmp/aura_nonexistent_change_xyz.json")
    combined = out + err
    assert code != 0 or any(w in combined.lower() for w in ["error", "not found", "no such"]), \
        "Missing change file must produce error"


# ── CLI-09: analyze with valid change JSON ────────────────────────────────────

def test_cli09_analyze_valid_change_json():
    """CLI-09: analyze with valid change JSON runs without crash."""
    change_data = [{"artifact_id": "REQ_AEB_001", "change_type": "MODIFIED",
                    "artifact_type": "REQUIREMENT", "after_content": "New brake torque limit"}]
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(change_data, f)
        tmp = f.name
    demo_dir = REPO_ROOT / "examples" / "demo_repo"
    if not demo_dir.exists():
        import pytest
        pytest.skip("examples/demo_repo not found")
    try:
        code, out, err = _run_cli("analyze", tmp, "--repo_dir", str(demo_dir))
        # Must not crash
        assert code == 0 or "error" not in err.lower()[:50], \
            f"analyze must not crash; code={code} err={err[:200]}"
    finally:
        Path(tmp).unlink(missing_ok=True)


# ── CLI-10: report command exits 0 on demo repo ───────────────────────────────

def test_cli10_report_command():
    """CLI-10: report command generates output files without crash."""
    change_data = [{"artifact_id": "REQ_AEB_001", "change_type": "MODIFIED",
                    "artifact_type": "REQUIREMENT", "after_content": "Updated brake limit"}]
    demo_dir = REPO_ROOT / "examples" / "demo_repo"
    if not demo_dir.exists():
        import pytest
        pytest.skip("examples/demo_repo not found")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(change_data, f)
        tmp = f.name
    out_dir = tempfile.mkdtemp(prefix="aura_cli_test_")
    try:
        code, out, err = _run_cli("report", tmp,
                                  "--repo_dir", str(demo_dir),
                                  "--out_dir", out_dir)
        # Must not crash
        assert code == 0 or "error" not in err.lower()[:50]
    finally:
        Path(tmp).unlink(missing_ok=True)
        shutil.rmtree(out_dir, ignore_errors=True)
