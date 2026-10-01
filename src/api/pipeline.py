"""
AURA-Impact End-to-End Execution Pipeline (Locked Architecture B)
Orchestrates ingestion, graph construction, semantic indexing, two-stage impact analysis, safety-gated test selection, and evidence generation.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
import yaml
import time

from src.ingestion.artifact_loader import ArtifactLoader
from src.ingestion.git_diff import GitDiffParser, ChangedArtifact
from src.parsers.cpp_parser import CppTreeSitterParser
from src.parsers.arxml_parser import AutosarARXMLParser
from src.parsers.requirement_parser import RequirementParser, RequirementRecord
from src.parsers.test_parser import TestParser, TestRecord

from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel
from src.graph.builder import EngineeringGraph

from src.semantic.embedder import SemanticEmbedder
from src.semantic.index import FAISSSemanticIndex, IndexedArtifact
from src.semantic.context_filter import ContextFilter
from src.semantic.retriever import ContextualRetriever

from src.impact.semantic_fallback import SemanticFallback
from src.impact.impact_engine import TwoStageImpactEngine, ImpactEngineResult

from src.testing.test_mapper import TestMapper
from src.testing.safety_gate import SafetyGate
from src.testing.regression_selector import RegressionSelector, RegressionSelectionResult

from src.evidence.evidence_logger import EvidenceLogger
from src.evidence.report_generator import ReportGenerator
from src.evidence.evidence_model import AnalysisEvidenceReport


class StaleIndexError(Exception):
    """Raised when repository artifacts have changed without rebuilding the semantic/graph index."""
    pass


class AuraImpactPipeline:
    """Production-grade prototype orchestrator for AURA-Impact."""

    def __init__(self, config_dir: Path = Path("configs")):
        self.config_dir = Path(config_dir)
        self.configs = self._load_configs()
        self.repo_file_hashes: Dict[str, str] = {}
        self.index_timestamp: float = 0.0
        self.last_ingested_repo: Optional[Path] = None

        # Core components
        self.graph = EngineeringGraph(project_id="AURA_SYSTEM")
        self.embedder = SemanticEmbedder(
            model_name=self.configs.get("semantic", {}).get("model", "AURA-DomainHashEmbedder-384"),
            dimension=self.configs.get("semantic", {}).get("embedding_dim", 384)
        )
        self.index = FAISSSemanticIndex(dimension=self.embedder.dimension)
        self.context_filter = ContextFilter(
            enforce_subsystem=self.configs.get("semantic", {}).get("context_constraints", {}).get("enforce_subsystem_isolation", True),
            enforce_artifact_type=self.configs.get("semantic", {}).get("context_constraints", {}).get("enforce_artifact_type_compatibility", True),
            min_context_score=self.configs.get("semantic", {}).get("context_constraints", {}).get("min_context_score", 0.50)
        )
        self.retriever = ContextualRetriever(
            embedder=self.embedder,
            index=self.index,
            context_filter=self.context_filter,
            similarity_threshold=self.configs.get("semantic", {}).get("threshold", 0.75),
            top_k=self.configs.get("semantic", {}).get("top_k", 10)
        )
        self.semantic_fallback = SemanticFallback(self.retriever)
        self.impact_engine = TwoStageImpactEngine(
            graph=self.graph,
            semantic_fallback=self.semantic_fallback,
            max_graph_depth=self.configs.get("graph", {}).get("max_depth", 3),
            default_threshold=self.configs.get("semantic", {}).get("threshold", 0.75)
        )

        self.all_tests: List[TestRecord] = []
        self.test_mapper = TestMapper(all_tests=[], graph=self.graph)
        self.safety_gate = SafetyGate(
            critical_levels=self.configs.get("safety", {}).get("asil_critical_classes", ["ASIL-C", "ASIL-D"])
        )
        self.regression_selector = RegressionSelector(
            test_mapper=self.test_mapper,
            safety_gate=self.safety_gate,
            all_tests=[]
        )
        self.report_generator = ReportGenerator()

    def _load_configs(self) -> Dict[str, Any]:
        cfg = {}
        for name in ["architecture", "graph", "semantic", "safety", "test_selection"]:
            p = self.config_dir / f"{name}.yaml"
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    cfg[name] = yaml.safe_load(f) or {}
        return cfg

    def ingest_repository(self, repo_dir: Path) -> Dict[str, int]:
        """Ingests and parses all repository artifacts into the graph and semantic index."""
        loader = ArtifactLoader(repo_dir)
        scanned = loader.scan()

        counts = {"requirements": 0, "swcs": 0, "c_functions": 0, "tests": 0}
        indexed_artifacts: List[IndexedArtifact] = []
        indexed_texts: List[str] = []

        # 1. Parse Requirements
        req_parser = RequirementParser()
        for r_path in scanned["requirements"]:
            reqs = req_parser.parse_records(r_path)
            for r in reqs:
                node = GraphNode(
                    id=r.req_id,
                    type=NodeType.REQUIREMENT,
                    name=r.title or r.req_id,
                    subsystem=r.subsystem,
                    ecu=r.ecu,
                    source_file=str(r_path),
                    safety_level=SafetyLevel[r.asil] if r.asil in SafetyLevel.__members__ else SafetyLevel.QM,
                    metadata={"description": r.description}
                )
                self.graph.add_node(node)
                counts["requirements"] += 1

                for target in r.trace_links:
                    self.graph.add_edge(GraphEdge(
                        source=r.req_id,
                        target=target,
                        relation=RelationType.MAPS_TO,
                        provenance="Requirement Trace Link"
                    ))

                # Index requirement text
                text = f"{r.req_id} {r.title} {r.description} {r.subsystem}"
                indexed_artifacts.append(IndexedArtifact(
                    artifact_id=r.req_id,
                    artifact_type="Requirement",
                    subsystem=r.subsystem,
                    ecu=r.ecu,
                    text_content=text,
                    source_file=str(r_path)
                ))
                indexed_texts.append(text)

        # 2. Parse ARXML
        arxml_parser = AutosarARXMLParser()
        for a_path in scanned["arxml"]:
            ar_data = arxml_parser.parse_records(a_path)
            for swc in ar_data["swcs"]:
                swc_node = GraphNode(
                    id=swc.name,
                    type=NodeType.SOFTWARE_COMPONENT,
                    name=swc.name,
                    subsystem=swc.subsystem,
                    ecu=swc.ecu,
                    source_file=str(a_path)
                )
                self.graph.add_node(swc_node)
                counts["swcs"] += 1

                for port in swc.ports:
                    p_node = GraphNode(
                        id=port.name,
                        type=NodeType.PORT,
                        name=port.name,
                        subsystem=swc.subsystem,
                        ecu=swc.ecu,
                        source_file=str(a_path)
                    )
                    self.graph.add_node(p_node)
                    self.graph.add_edge(GraphEdge(
                        source=swc.name,
                        target=port.name,
                        relation=RelationType.PROVIDES if port.port_type == "P_PORT" else RelationType.REQUIRES,
                        provenance="ARXML Port Prototype"
                    ))

                for run in swc.runnables:
                    r_node = GraphNode(
                        id=run.name,
                        type=NodeType.RUNNABLE,
                        name=run.name,
                        subsystem=swc.subsystem,
                        ecu=swc.ecu,
                        source_file=str(a_path)
                    )
                    self.graph.add_node(r_node)
                    self.graph.add_edge(GraphEdge(
                        source=swc.name,
                        target=run.name,
                        relation=RelationType.OWNS,
                        provenance="ARXML Runnable Entity"
                    ))

        # 3. Parse C/C++ Source
        cpp_parser = CppTreeSitterParser()
        for c_path in scanned["c_source"]:
            fns, vars_found = cpp_parser.parse_records(c_path)
            if "body" in str(c_path).lower():
                subsystem = "Body_Electronics"
            elif "powertrain" in str(c_path).lower():
                subsystem = "Powertrain"
            elif "bms" in str(c_path).lower() or "battery" in str(c_path).lower():
                subsystem = "Battery_EV"
            else:
                subsystem = "ADAS"

            for fn in fns:
                fn_node = GraphNode(
                    id=fn.name,
                    type=NodeType.C_FUNCTION,
                    name=fn.name,
                    subsystem=subsystem,
                    ecu="ECU_1",
                    source_file=str(c_path),
                    source_location=f"L{fn.start_line}-L{fn.end_line}",
                    metadata={"callees": fn.callees, "rte_apis": fn.rte_apis}
                )
                self.graph.add_node(fn_node)
                counts["c_functions"] += 1

                for callee in fn.callees:
                    self.graph.add_edge(GraphEdge(
                        source=fn.name,
                        target=callee,
                        relation=RelationType.CALLS,
                        provenance="C Call Graph"
                    ))

                # Index function code snippet and identifiers
                text = f"{fn.name} {fn.source_snippet} {' '.join(fn.callees)} {subsystem}"
                indexed_artifacts.append(IndexedArtifact(
                    artifact_id=fn.name,
                    artifact_type="C_Function",
                    subsystem=subsystem,
                    ecu="ECU_1",
                    text_content=text,
                    source_file=str(c_path)
                ))
                indexed_texts.append(text)

        # 4. Parse Tests
        test_parser = TestParser()
        for t_path in scanned["tests"]:
            t_records = test_parser.parse_records(t_path)
            for t in t_records:
                self.all_tests.append(t)
                lvl = SafetyLevel[t.safety_class] if t.safety_class in SafetyLevel.__members__ else SafetyLevel.QM
                t_node = GraphNode(
                    id=t.test_id,
                    type=NodeType.TEST,
                    name=t.test_id,
                    subsystem=t.subsystem,
                    ecu=t.ecu,
                    source_file=str(t_path),
                    safety_level=lvl
                )
                self.graph.add_node(t_node)
                counts["tests"] += 1

                for target in t.artifact_targets:
                    self.graph.add_edge(GraphEdge(
                        source=t.test_id,
                        target=target,
                        relation=RelationType.VERIFIES,
                        provenance="Test Mapping Specification"
                    ))

        # Build Semantic FAISS Index
        if indexed_texts:
            embeddings = self.embedder.embed_batch(indexed_texts)
            self.index.add_artifacts(indexed_artifacts, embeddings)

        # Update test selector references
        self.test_mapper = TestMapper(all_tests=self.all_tests, graph=self.graph)
        self.regression_selector = RegressionSelector(
            test_mapper=self.test_mapper,
            safety_gate=self.safety_gate,
            all_tests=self.all_tests
        )

        # Store file hashes and timestamp
        import hashlib
        self.last_ingested_repo = repo_dir
        self.index_timestamp = time.time()
        self.repo_file_hashes = {}
        for cat, flist in scanned.items():
            for fpath in flist:
                try:
                    with open(fpath, "rb") as fb:
                        self.repo_file_hashes[str(fpath)] = hashlib.md5(fb.read()).hexdigest()
                except Exception:
                    pass

        return counts

    def check_staleness(self, repo_dir: Optional[Path] = None) -> Tuple[bool, List[str]]:
        """Checks if files in the repository have been modified, added, or deleted since ingestion."""
        import hashlib
        target_dir = repo_dir or self.last_ingested_repo
        if not target_dir or not self.repo_file_hashes:
            return False, []

        loader = ArtifactLoader(target_dir)
        scanned = loader.scan()
        stale_files = []

        all_current = []
        for cat, flist in scanned.items():
            for fpath in flist:
                p_str = str(fpath)
                all_current.append(p_str)
                if p_str not in self.repo_file_hashes:
                    stale_files.append(f"NEW_FILE:{p_str}")
                else:
                    try:
                        with open(fpath, "rb") as fb:
                            cur_h = hashlib.md5(fb.read()).hexdigest()
                            if cur_h != self.repo_file_hashes[p_str]:
                                stale_files.append(f"MODIFIED:{p_str}")
                    except Exception:
                        stale_files.append(f"UNREADABLE:{p_str}")

        for old_p in self.repo_file_hashes.keys():
            if old_p not in all_current:
                stale_files.append(f"DELETED:{old_p}")

        return (len(stale_files) > 0, stale_files)

    def analyze_change(self,
                       change: ChangedArtifact,
                       threshold_override: Optional[float] = None,
                       mandatory_safety_tests: Optional[Set[str]] = None,
                       repo_dir: Optional[Path] = None,
                       enforce_freshness: bool = False,
                       force_semantic: bool = False) -> Tuple[ImpactEngineResult, RegressionSelectionResult, AnalysisEvidenceReport]:
        if enforce_freshness:
            is_stale, stale_reasons = self.check_staleness(repo_dir)
            if is_stale:
                raise StaleIndexError(f"Semantic/Graph index is stale: {stale_reasons}")

        # 1. Run Impact Engine
        impact_res = self.impact_engine.analyze_change(
            change,
            threshold_override=threshold_override,
            force_semantic=force_semantic
        )

        # 2. Run Test Selection with Safety Gate
        test_res = self.regression_selector.select(
            impacts=impact_res.final_impacts,
            mandatory_safety_test_ids=mandatory_safety_tests
        )

        # 3. Generate Evidence Report
        logger = EvidenceLogger()
        report = logger.build_report(change, impact_res, test_res)

        return impact_res, test_res, report
