"""
AURA-Impact Full Demo Runner
Executes all 4 automotive scenarios:
1. Explicit Structural
2. Hidden Semantic Recovery
3. Semantic Decoy Rejection
4. Ambiguous / Review Required
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api.pipeline import AuraImpactPipeline
from src.ingestion.git_diff import GitDiffParser

def main():
    print("=" * 70)
    print("      AURA-IMPACT PRODUCTION PROTOTYPE (ARCHITECTURE B) DEMO")
    print("=" * 70)

    pipeline = AuraImpactPipeline()
    print("\n[Step 1] Ingesting Demo Automotive Repository...")
    counts = pipeline.ingest_repository(Path("examples/demo_repo"))
    print(f"  - Scanned: {counts['requirements']} Reqs, {counts['swcs']} SWCs, {counts['c_functions']} Functions, {counts['tests']} Tests.")
    print(f"  - Graph Nodes: {len(pipeline.graph.node_store)}, Edges: {len(pipeline.graph.edge_store)}")

    scenarios = [
        ("SCENARIO 1: EXPLICIT STRUCTURAL TRACEABILITY", "examples/demo_repo/change_structural.json"),
        ("SCENARIO 2: HIDDEN SEMANTIC RECOVERY (GRAPH-BLIND)", "examples/demo_repo/change_hidden_semantic.json"),
        ("SCENARIO 3: SEMANTIC DECOY DISTRACTOR REJECTION", "examples/demo_repo/change_decoy.json"),
        ("SCENARIO 4: AMBIGUOUS REQUIREMENT ABSTENTION", "examples/demo_repo/change_ambiguous.json")
    ]

    for title, change_path in scenarios:
        print("\n" + "-" * 70)
        print(title)
        print("-" * 70)

        changes = GitDiffParser.parse_change_file(Path(change_path))
        for change in changes:
            impact_res, test_res, report = pipeline.analyze_change(change)

            print(f"Changed Artifact: {change.artifact_id} ({change.subsystem})")
            print(f"  - Stage 1 Structural Impacts: {len(impact_res.structural_impacts)}")
            for imp in impact_res.structural_impacts:
                print(f"      • {imp.artifact_id} [{imp.artifact_type}]")

            print(f"  - Stage 2 Semantic Recoveries: {len(impact_res.semantic_impacts)}")
            for imp in impact_res.semantic_impacts:
                print(f"      • {imp.artifact_id} [{imp.artifact_type}] (Similarity: {imp.confidence:.2f}, Context: PASS)")

            print(f"  - Review Required Items: {len(impact_res.review_required_items)}")
            for rev in impact_res.review_required_items:
                print(f"      • {rev.artifact_id}: {rev.rejection_reason}")

            print(f"  - Test Suite Selection: {len(test_res.selected_tests)} / {test_res.all_tests_count} ({test_res.test_reduction_pct}% reduction)")
            print(f"  - Safety-Critical Tests Retained: {len(test_res.safety_tests)}")
            for t in test_res.safety_tests:
                print(f"      [SAFETY-GATE ASIL-D] {t.test_id}: {t.description}")

    print("\n" + "=" * 70)
    print("[SUCCESS] All 4 Demo Scenarios Executed Successfully.")
    print("=" * 70)

if __name__ == "__main__":
    main()
