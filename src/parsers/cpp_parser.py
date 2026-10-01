"""
C/C++ Parser using Tree-sitter
Extracts function definitions, function calls, variables, reads, writes, RTE API calls, and line numbers.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import re

from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel

try:
    import tree_sitter_c
    from tree_sitter import Language, Parser
    C_LANGUAGE = Language(tree_sitter_c.language())
    TREE_SITTER_AVAILABLE = True
except Exception:
    TREE_SITTER_AVAILABLE = False


@dataclass
class CFunctionDef:
    name: str
    return_type: str
    file_path: str
    start_line: int
    end_line: int
    callees: List[str] = field(default_factory=list)
    variables_read: List[str] = field(default_factory=list)
    variables_written: List[str] = field(default_factory=list)
    rte_apis: List[str] = field(default_factory=list)
    source_snippet: str = ""


@dataclass
class CVariableDef:
    name: str
    var_type: str
    file_path: str
    line_number: int


class CppTreeSitterParser:
    """Extracts C functions, calls, variables, and RTE invocations."""

    def __init__(self, project_name: str = "ADAS", **kwargs):
        self.project_name = project_name
        self.parser = None
        if TREE_SITTER_AVAILABLE:
            try:
                self.parser = Parser(C_LANGUAGE)
            except Exception:
                self.parser = None

    def parse_file(self, file_path: Path) -> Tuple[List[GraphNode], List[GraphEdge]]:
        fns, vars_found = self.parse_records(file_path)
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        for fn in fns:
            nodes.append(GraphNode(
                id=fn.name,
                type=NodeType.C_FUNCTION,
                name=fn.name,
                subsystem=self.project_name,
                ecu="ECU_1",
                source_file=str(file_path),
                file_path=str(file_path),
                project=self.project_name,
                source_location=f"L{fn.start_line}-L{fn.end_line}",
                metadata={"callees": fn.callees, "rte_apis": fn.rte_apis}
            ))
            for callee in fn.callees:
                edges.append(GraphEdge(
                    source=fn.name,
                    target=callee,
                    relation=RelationType.CALLS,
                    provenance="C Call Graph"
                ))

        for v in vars_found:
            nodes.append(GraphNode(
                id=v.name,
                type=NodeType.C_VARIABLE,
                name=v.name,
                subsystem=self.project_name,
                ecu="ECU_1",
                source_file=str(file_path),
                file_path=str(file_path),
                project=self.project_name,
                source_location=f"L{v.line_number}"
            ))

        return nodes, edges

    def parse_records(self, file_path: Path) -> Tuple[List[CFunctionDef], List[CVariableDef]]:
        file_path = Path(file_path)
        if not file_path.exists():
            return [], []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        if self.parser:
            return self._parse_with_treesitter(code, str(file_path))
        else:
            return self._parse_with_ast_fallback(code, str(file_path))

    def _parse_with_treesitter(self, code: str, file_path: str) -> Tuple[List[CFunctionDef], List[CVariableDef]]:
        tree = self.parser.parse(bytes(code, "utf-8"))
        functions: List[CFunctionDef] = []
        variables: List[CVariableDef] = []

        def traverse(node):
            if node.type == "function_definition":
                fn = self._extract_function(node, code, file_path)
                if fn:
                    functions.append(fn)
            elif node.type == "declaration":
                vars_found = self._extract_variables(node, code, file_path)
                variables.extend(vars_found)

            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return functions, variables

    def _extract_function(self, node, code: str, file_path: str) -> Optional[CFunctionDef]:
        declarator = node.child_by_field_name("declarator")
        type_node = node.child_by_field_name("type")
        return_type = code[type_node.start_byte:type_node.end_byte] if type_node else "void"

        fn_name = None
        if declarator:
            def find_identifier(d):
                if d.type == "identifier":
                    return code[d.start_byte:d.end_byte]
                for c in d.children:
                    res = find_identifier(c)
                    if res:
                        return res
                return None
            fn_name = find_identifier(declarator)

        if not fn_name:
            return None

        callees = []
        rte_apis = []
        vars_read = []
        vars_written = []

        body = node.child_by_field_name("body")
        if body:
            def scan_body(b_node):
                if b_node.type == "call_expression":
                    fn_call = b_node.child_by_field_name("function")
                    if fn_call:
                        call_name = code[fn_call.start_byte:fn_call.end_byte]
                        callees.append(call_name)
                        if "Rte_" in call_name:
                            rte_apis.append(call_name)
                elif b_node.type == "assignment_expression":
                    left = b_node.child_by_field_name("left")
                    if left and left.type == "identifier":
                        vars_written.append(code[left.start_byte:left.end_byte])
                elif b_node.type == "identifier":
                    name = code[b_node.start_byte:b_node.end_byte]
                    if name != fn_name:
                        vars_read.append(name)

                for c in b_node.children:
                    scan_body(c)

            scan_body(body)

        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        snippet = code[node.start_byte:node.end_byte]

        return CFunctionDef(
            name=fn_name,
            return_type=return_type,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            callees=list(set(callees)),
            variables_read=list(set(vars_read) - set(callees)),
            variables_written=list(set(vars_written)),
            rte_apis=list(set(rte_apis)),
            source_snippet=snippet
        )

    def _extract_variables(self, node, code: str, file_path: str) -> List[CVariableDef]:
        vars_list = []
        type_node = node.child_by_field_name("type")
        var_type = code[type_node.start_byte:type_node.end_byte] if type_node else "int"
        
        for c in node.children:
            if c.type == "init_declarator" or c.type == "identifier":
                v_name = code[c.start_byte:c.end_byte].split("=")[0].strip()
                if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v_name):
                    vars_list.append(CVariableDef(
                        name=v_name,
                        var_type=var_type,
                        file_path=file_path,
                        line_number=node.start_point[0] + 1
                    ))
        return vars_list

    def _parse_with_ast_fallback(self, code: str, file_path: str) -> Tuple[List[CFunctionDef], List[CVariableDef]]:
        functions = []
        variables = []
        lines = code.split("\n")
        fn_pattern = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_*\s]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)\s*\{?")
        call_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")

        for idx, line in enumerate(lines):
            match = fn_pattern.match(line)
            if match and not line.strip().startswith("//"):
                ret_type = match.group(1).strip()
                fn_name = match.group(2).strip()
                if fn_name not in ["if", "for", "while", "switch"]:
                    callees = []
                    rte_apis = []
                    block = "\n".join(lines[idx:min(len(lines), idx+40)])
                    for c_match in call_pattern.finditer(block):
                        c_name = c_match.group(1)
                        if c_name != fn_name and c_name not in ["if", "for", "while", "switch", "sizeof"]:
                            callees.append(c_name)
                            if "Rte_" in c_name:
                                rte_apis.append(c_name)

                    functions.append(CFunctionDef(
                        name=fn_name,
                        return_type=ret_type,
                        file_path=file_path,
                        start_line=idx + 1,
                        end_line=min(len(lines), idx + 20),
                        callees=list(set(callees)),
                        rte_apis=list(set(rte_apis)),
                        source_snippet=block[:300]
                    ))
        return functions, variables


# Backward-compatible alias
CppParser = CppTreeSitterParser
