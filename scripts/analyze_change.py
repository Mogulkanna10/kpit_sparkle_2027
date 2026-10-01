"""
AURA-Impact Change Analysis Script
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api.pipeline import AuraImpactPipeline
from src.ingestion.git_diff import GitDiffParser

if __name__ == "__main__":
    change_file = sys.argv[1] if len(sys.argv) > 1 else "examples/demo_repo/change_hidden_semantic.json"
    repo_dir = sys.argv[2] if len(sys.argv) > 2 else "examples/demo_repo"

    pipeline = AuraImpactPipeline()
    pipeline.ingest_repository(Path(repo_dir))

    changes = GitDiffParser.parse_change_file(Path(change_file))
    for change in changes:
        impact_res, test_res, report = pipeline.analyze_change(change)
        print("=" * 60)
        print(f"ANALYSIS RESULT: {change.artifact_id}")
        print("=" * 60)
        print(f"Structural impacts: {len(impact_res.structural_impacts)}")
        print(f"Semantic recoveries: {len(impact_res.semantic_impacts)}")
        print(f"Tests selected: {len(test_res.selected_tests)} / {test_res.all_tests_count} ({test_res.test_reduction_pct}% reduction)")
        print(f"Safety-critical tests retained: {len(test_res.safety_tests)}")
        paths = pipeline.report_generator.export_all(report)
        print(f"Report exported to: {paths['markdown']}")
