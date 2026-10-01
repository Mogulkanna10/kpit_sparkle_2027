# Gate 17 — CLI Validation Report

**Date:** 2026-09-30  
**Status:** PASS  
**Test Suite:** `tests/cli/test_cli.py`  
**Passed Tests:** 10 / 10 (100%)  
**Evidence Artifact:** `artifacts/gates/stage_17_gate.json`  
**Commit:** `ffc284ce5eb8e6b5fd25c7f09ea7822f2c27de72`  

---

## 1. Executive Summary

Gate 17 validates every documented Command-Line Interface (CLI) workflow of AURA-Impact through real subprocess invocations (`subprocess.run([sys.executable, "src/api/cli.py", ...])`). In production automotive development, engineers and CI runners interact with the tool through shell scripts and pipeline jobs. The CLI must execute predictably, provide clear help documentation, validate file paths, enforce proper exit codes, and generate deterministic outputs.

All 10 integration tests passed successfully.

---

## 2. Documented CLI Workflows and Validation Results

| Test Case | Command Invoked | Expected Outcome | Observed Outcome | Result |
|---|---|---|---|---|
| `test_cli_help` | `python src/api/cli.py --help` | Exit code 0, lists subcommands | Clean usage output displayed | PASS |
| `test_cli_no_args` | `python src/api/cli.py` | Shows usage/help or non-zero exit | Usage output displayed | PASS |
| `test_cli_ingest_valid` | `python src/api/cli.py ingest data/synthetic/ADAS` | Parses SWCs, tests, requirements | 100% parsed, exit 0 | PASS |
| `test_cli_ingest_missing_dir` | `python src/api/cli.py ingest non_existent_dir` | Non-zero exit code, error message | Exits with error code, message displayed | PASS |
| `test_cli_build_index_valid` | `python src/api/cli.py build-index ...` | Generates semantic index | Index created cleanly | PASS |
| `test_cli_build_index_missing_dir` | `python src/api/cli.py build-index non_existent` | Non-zero exit code | Clean error handling | PASS |
| `test_cli_analyze_valid` | `python src/api/cli.py analyze ...` | Computes impact & selected tests | Outputs valid JSON impact result | PASS |
| `test_cli_analyze_missing_file` | `python src/api/cli.py analyze --change non_existent.json` | Non-zero exit code | Proper path error reported | PASS |
| `test_cli_report` | `python src/api/cli.py report ...` | Formats evidence audit report | Report written successfully | PASS |
| `test_cli_deterministic_output` | Repeated `analyze` executions | Identical selected tests and hashes | Deterministic output confirmed | PASS |

---

## 3. Exit Code Semantics

The CLI strictly obeys Unix exit code conventions:
- `0`: Successful execution.
- `1`: Validation error, missing required arguments, or unhandled exception.
- `2`: Command line parsing / flag syntax error (handled by `argparse`).

---

## 4. Acceptance Criteria Verification

- [x] Subprocess-level execution verified across all documented commands: **VERIFIED**
- [x] Help text matches actual flags and subcommands: **VERIFIED**
- [x] Missing and invalid files rejected with non-zero exit codes: **VERIFIED**
- [x] Output paths and artifacts generated deterministically: **VERIFIED**
- [x] Stage 17 gate artifact recorded (`artifacts/gates/stage_17_gate.json`): **VERIFIED**

**Gate 17 Status: PASS**
