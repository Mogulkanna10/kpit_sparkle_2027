"""
AURA-Impact Command Line Interface (CLI)
Provides commands for repository ingestion, indexing, change impact analysis, and report generation.
"""
import sys
import argparse
from pathlib import Path
import json

from src.api.pipeline import AuraImpactPipeline
from src.ingestion.git_diff import GitDiffParser, ChangedArtifact


def main():
    parser = argparse.ArgumentParser(description="AURA-Impact Production Prototype CLI (Locked Architecture B)")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest repository artifacts and construct engineering graph")
    ingest_parser.add_argument("repo_dir", type=str, help="Path to automotive repository directory")

    # 2. build-index
    index_parser = subparsers.add_parser("build-index", help="Build semantic vector index from repository")
    index_parser.add_argument("--repo_dir", type=str, default="examples/demo_repo", help="Path to repository")

    # 3. analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze change impact across graph and semantic layers")
    analyze_parser.add_argument("change_file", type=str, help="Path to change JSON or diff file")
    analyze_parser.add_argument("--repo_dir", type=str, default="examples/demo_repo", help="Repository directory")
    analyze_parser.add_argument("--threshold", type=float, default=None, help="Semantic similarity threshold")

    # 4. report
    report_parser = subparsers.add_parser("report", help="Generate analysis reports (JSON, Markdown, HTML)")
    report_parser.add_argument("change_file", type=str, help="Path to change JSON or diff file")
    report_parser.add_argument("--repo_dir", type=str, default="examples/demo_repo", help="Repository directory")
    report_parser.add_argument("--out_dir", type=str, default="reports/analysis", help="Output directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    pipeline = AuraImpactPipeline()

    if args.command == "ingest" or args.command == "build-index":
        target_dir = Path(args.repo_dir)
        print(f"Ingesting repository from: {target_dir.resolve()}")
        counts = pipeline.ingest_repository(target_dir)
        print("\n[OK] Repository Ingestion Complete:")
        print(f"  - Requirements parsed: {counts['requirements']}")
        print(f"  - Software Components (SWCs): {counts['swcs']}")
        print(f"  - C Functions parsed: {counts['c_functions']}")
        print(f"  - Verification Tests: {counts['tests']}")
        print(f"  - Graph Nodes: {len(pipeline.graph.node_store)}, Edges: {len(pipeline.graph.edge_store)}")
        print(f"  - Semantic Index Artifacts: {len(pipeline.index.artifacts)}")

    elif args.command in ["analyze", "report"]:
        target_dir = Path(args.repo_dir)
        if not pipeline.graph.node_store:
            pipeline.ingest_repository(target_dir)

        change_file = Path(args.change_file)
        changes = GitDiffParser.parse_change_file(change_file)

        for change in changes:
            impact_res, test_res, report = pipeline.analyze_change(
                change=change,
                threshold_override=getattr(args, "threshold", None)
            )

            # Print CLI Output
            print("\n" + "=" * 55)
            print("AURA-IMPACT ANALYSIS")
            print("=" * 55)
            print(f"\nChanged:\n{change.artifact_id}")

            print("\nSTRUCTURAL IMPACTS:")
            if impact_res.structural_impacts:
                for imp in impact_res.structural_impacts:
                    print(f"- {imp.artifact_id} ({imp.artifact_type})")
            else:
                print("None (0 explicit graph links found)")

            print("\nSEMANTIC RECOVERY:")
            if impact_res.semantic_impacts:
                for imp in impact_res.semantic_impacts:
                    print(f"- {imp.artifact_id}")
                    print(f"  similarity: {imp.confidence:.2f}")
                    print("  context: PASS")
            else:
                print("None")

            print("\nREVIEW REQUIRED:")
            if impact_res.review_required_items:
                for rev in impact_res.review_required_items:
                    print(f"- {rev.artifact_id}")
                    print(f"  reason: {rev.rejection_reason}")
            else:
                print("None")

            print("\nTESTS:")
            print(f"Selected: {len(test_res.selected_tests)} / {test_res.all_tests_count}")
            print(f"\nSafety-critical retained:\n{len(test_res.safety_tests)} / {len(test_res.safety_tests)}")
            print("=" * 55)

            if args.command == "report":
                out_dir = Path(getattr(args, "out_dir", "reports/analysis"))
                pipeline.report_generator.output_dir = out_dir
                paths = pipeline.report_generator.export_all(report)
                print(f"\n[OK] Reports generated:")
                for fmt, p in paths.items():
                    print(f"  - {fmt.upper()}: {p.resolve()}")


if __name__ == "__main__":
    main()
