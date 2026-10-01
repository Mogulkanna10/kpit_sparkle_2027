"""
Evidence Report Generator
Exports comprehensive auditable analysis reports in JSON, HTML, and Markdown formats.
"""
from pathlib import Path
from typing import Optional, Dict
import json
from dataclasses import asdict
from src.evidence.evidence_model import AnalysisEvidenceReport


class ReportGenerator:
    """Renders structured reports in multiple formats."""

    def __init__(self, output_dir: Path = Path("reports/analysis")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_all(self, report: AnalysisEvidenceReport, base_name: Optional[str] = None) -> Dict[str, Path]:
        name = base_name or report.analysis_id
        paths = {}
        paths["json"] = self.export_json(report, self.output_dir / f"{name}.json")
        paths["markdown"] = self.export_markdown(report, self.output_dir / f"{name}.md")
        paths["html"] = self.export_html(report, self.output_dir / f"{name}.html")
        return paths

    def export_json(self, report: AnalysisEvidenceReport, target_file: Path) -> Path:
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2)
        return target_file

    def export_markdown(self, report: AnalysisEvidenceReport, target_file: Path) -> Path:
        md = [
            f"# AURA-Impact Analysis Report: `{report.changed_artifact_id}`",
            f"- **Analysis ID:** {report.analysis_id}",
            f"- **Timestamp:** {report.timestamp}",
            f"- **Subsystem:** {report.subsystem}",
            "",
            "## Summary Metrics",
            f"- **Structural Impacts:** {report.structural_impacts_count}",
            f"- **Semantic Recoveries:** {report.semantic_recoveries_count}",
            f"- **Review Required Items:** {report.review_required_count}",
            f"- **Total Impacted Artifacts:** {report.total_impacts_count}",
            f"- **Selected Tests:** {report.tests_selected_count} / {report.total_test_suite_size} ({report.test_reduction_pct}% reduction)",
            f"- **Safety-Critical Tests Retained:** {report.safety_tests_count}",
            f"- **Online Latency:** {report.latency_profile.get('total_ms', 0.0):.2f} ms",
            "",
            "## Impacted Engineering Artifacts",
            "| Artifact ID | Type | Stage | Confidence | Reason |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]
        for it in report.impact_items:
            md.append(f"| `{it['id']}` | {it['type']} | **{it['stage']}** | {it['confidence']:.2f} | {it['reason']} |")

        md.extend([
            "",
            "## Selected Regression Test Cases",
            "| Test ID | Description | Safety Class | Source |",
            "| :--- | :--- | :--- | :--- |"
        ])
        for t in report.test_items:
            md.append(f"| `{t['id']}` | {t['description']} | **{t['safety_class']}** | {t['source']} |")

        with open(target_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
        return target_file

    def export_html(self, report: AnalysisEvidenceReport, target_file: Path) -> Path:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AURA-Impact Analysis Report - {report.changed_artifact_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: #1e293b; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 0.5rem; }}
        h2 {{ color: #94a3b8; margin-top: 1.5rem; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
        .metric-card {{ background: #0f172a; padding: 1.2rem; border-radius: 8px; border-left: 4px solid #38bdf8; }}
        .metric-val {{ font-size: 1.8rem; font-weight: bold; color: #f1f5f9; }}
        .metric-lbl {{ font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; background: #0f172a; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #1e293b; color: #38bdf8; }}
        .tag-structural {{ color: #34d399; font-weight: bold; }}
        .tag-semantic {{ color: #38bdf8; font-weight: bold; }}
        .tag-safety {{ color: #f87171; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AURA-Impact Analysis Report</h1>
        <p><strong>Changed Artifact:</strong> <code>{report.changed_artifact_id}</code> | <strong>Subsystem:</strong> {report.subsystem} | <strong>Timestamp:</strong> {report.timestamp}</p>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-val">{report.total_impacts_count}</div>
                <div class="metric-lbl">Total Impacts</div>
            </div>
            <div class="metric-card" style="border-left-color: #34d399;">
                <div class="metric-val">{report.structural_impacts_count}</div>
                <div class="metric-lbl">Structural (Stage 1)</div>
            </div>
            <div class="metric-card" style="border-left-color: #38bdf8;">
                <div class="metric-val">{report.semantic_recoveries_count}</div>
                <div class="metric-lbl">Semantic (Stage 2)</div>
            </div>
            <div class="metric-card" style="border-left-color: #f87171;">
                <div class="metric-val">{report.tests_selected_count} / {report.total_test_suite_size}</div>
                <div class="metric-lbl">Tests Selected ({report.test_reduction_pct}% reduction)</div>
            </div>
        </div>

        <h2>Impacted Engineering Artifacts</h2>
        <table>
            <thead>
                <tr>
                    <th>Artifact ID</th>
                    <th>Type</th>
                    <th>Stage</th>
                    <th>Confidence</th>
                    <th>Reason</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td><code>{it['id']}</code></td><td>{it['type']}</td><td class='tag-{it['stage'].lower()}'>{it['stage']}</td><td>{it['confidence']:.2f}</td><td>{it['reason']}</td></tr>" for it in report.impact_items])}
            </tbody>
        </table>

        <h2>Selected Regression Tests (Safety Retained: {report.safety_tests_count})</h2>
        <table>
            <thead>
                <tr>
                    <th>Test ID</th>
                    <th>Description</th>
                    <th>Safety Class</th>
                    <th>Mapping Source</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td><code>{t['id']}</code></td><td>{t['description']}</td><td class='tag-safety'>{t['safety_class']}</td><td>{t['source']}</td></tr>" for t in report.test_items])}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(html)
        return target_file
