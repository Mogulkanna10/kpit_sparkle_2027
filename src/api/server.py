import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api.pipeline import AuraImpactPipeline
from src.ingestion.git_diff import ChangedArtifact

app = FastAPI(title="AURA-Impact Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline = AuraImpactPipeline()
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Ingest default repo on startup
@app.on_event("startup")
async def startup_event():
    default_repo = REPO_ROOT / "data" / "demonstration_dataset"
    if not default_repo.exists():
        default_repo = REPO_ROOT / "examples" / "demo_repo"
    if default_repo.exists():
        pipeline.ingest_repository(default_repo)

class ChangeRequest(BaseModel):
    artifact_id: str
    artifact_type: str
    subsystem: str
    ecu: str
    change_type: str
    after_content: str
    change_semantics: str
    force_semantic: bool = False
    filter_subsystem: bool = True

@app.post("/analyze")
async def analyze_change(request: ChangeRequest):
    try:
        change_obj = ChangedArtifact(
            artifact_id=request.artifact_id,
            artifact_type=request.artifact_type,
            subsystem=request.subsystem,
            ecu=request.ecu,
            change_type=request.change_type,
            after_content=request.after_content,
            change_semantics=request.change_semantics,
            metadata={
                "force_semantic": request.force_semantic,
                "filter_subsystem_in_index": request.filter_subsystem
            }
        )
        impact_res, test_res, report = pipeline.analyze_change(change_obj)
        
        import json
        import networkx as nx
        from fastapi.encoders import jsonable_encoder
        
        graph_data = nx.node_link_data(pipeline.graph.graph) if pipeline.graph else None

        return {
            "status": "success",
            "report": jsonable_encoder(report),
            "impacted_nodes": jsonable_encoder(impact_res.final_impacts),
            "test_nodes": jsonable_encoder(test_res.selected_tests),
            "full_graph": graph_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "loaded_nodes": len(pipeline.graph.graph.nodes) if pipeline.graph else 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
