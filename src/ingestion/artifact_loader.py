"""
Artifact Loader & Repository Scanner
Discovers and loads all engineering artifacts across requirements, ARXML, C/C++, and tests.
"""
from pathlib import Path
from typing import Dict, List, Any


class ArtifactLoader:
    """Recursively scans a repository and groups artifact files by category."""

    def __init__(self, repo_dir: Path):
        self.repo_dir = Path(repo_dir)

    def scan(self) -> Dict[str, List[Path]]:
        if not self.repo_dir.exists():
            raise FileNotFoundError(f"Repository directory does not exist: {self.repo_dir}")

        artifacts = {
            "requirements": [],
            "arxml": [],
            "c_source": [],
            "tests": []
        }

        for path in self.repo_dir.rglob("*"):
            if not path.is_file():
                continue

            name_lower = path.name.lower()
            suffix = path.suffix.lower()

            if suffix in [".arxml", ".xml"] and ("arxml" in name_lower or "autosar" in name_lower or "swc" in name_lower):
                artifacts["arxml"].append(path)
            elif suffix in [".c", ".cpp", ".h", ".hpp"]:
                artifacts["c_source"].append(path)
            elif suffix in [".json", ".csv", ".md", ".txt"] and ("req" in name_lower or "spec" in name_lower or "requirement" in name_lower):
                artifacts["requirements"].append(path)
            elif suffix in [".json", ".csv", ".yaml", ".yml"] and ("test" in name_lower or "tc_" in name_lower):
                artifacts["tests"].append(path)

        return artifacts
