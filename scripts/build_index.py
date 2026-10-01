"""
AURA-Impact Index Construction Script
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api.pipeline import AuraImpactPipeline

if __name__ == "__main__":
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "examples/demo_repo"
    pipeline = AuraImpactPipeline()
    print(f"Building semantic vector index for: {repo_dir}")
    counts = pipeline.ingest_repository(Path(repo_dir))
    print(f"[OK] Index Constructed: {len(pipeline.index.artifacts)} artifacts indexed in FAISS vector store.")
