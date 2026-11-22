"""Universal NOR decomposition turning Boolean AST into a topological DAG."""

from biological_logic_compiler.models import CircuitGraph, LogicNode
from biological_logic_compiler.parser import (
    ASTNode,
    BinaryOpNode,
    NotNode,
    VarNode,
)


class NORDecomposer:
    """Translates arbitrary Boolean operations into networks of physical NOR units."""
    def __init__(self, circuit_name: str = "BioCircuit"):
        self.circuit_name = circuit_name
        self.node_counter = 0
        self.nodes: dict[str, LogicNode] = {}
        self.primary_inputs: list[str] = []

    def _next_gate_id(self, prefix: str = "g") -> str:
        self.node_counter += 1
        return f"{prefix}_{self.node_counter}"

    def build_nor_gate(self, input_ids: list[str]) -> str:
        """Create a NOR logic gate node driven by specified upstream inputs."""
        gate_id = self._next_gate_id("nor")
        self.nodes[gate_id] = LogicNode(
            node_id=gate_id,
            gate_type="NOR",
            inputs=list(input_ids),
        )
        return gate_id

    def build_not_gate(self, input_id: str) -> str:
        """Create an inverter by tying inputs into a single-input NOR unit."""
        gate_id = self._next_gate_id("inv")
        self.nodes[gate_id] = LogicNode(
            node_id=gate_id,
            gate_type="NOT",
            inputs=[input_id],
        )
        return gate_id

    def decompose_ast(self, node: ASTNode) -> str:
        """Recursively transform AST nodes into topological NOR interconnections."""
        if isinstance(node, VarNode):
            input_id = f"in_{node.name}"
            if input_id not in self.nodes:
                self.nodes[input_id] = LogicNode(
                    node_id=input_id,
                    gate_type="INPUT",
                    inputs=[],
                )
                self.primary_inputs.append(node.name)
            return input_id

        elif isinstance(node, NotNode):
            child_id = self.decompose_ast(node.child)
            return self.build_not_gate(child_id)

        elif isinstance(node, BinaryOpNode):
            left_id = self.decompose_ast(node.left)
            right_id = self.decompose_ast(node.right)
            op = node.op

            if op == "NOR":
                return self.build_nor_gate([left_id, right_id])

            elif op == "OR":
                # OR(A, B) = NOT(NOR(A, B))
                nor_id = self.build_nor_gate([left_id, right_id])
                return self.build_not_gate(nor_id)

            elif op == "AND":
                # AND(A, B) = NOR(NOT(A), NOT(B))
                not_l = self.build_not_gate(left_id)
                not_r = self.build_not_gate(right_id)
                return self.build_nor_gate([not_l, not_r])

            elif op == "NAND":
                # NAND(A, B) = NOT(AND(A, B))
                not_l = self.build_not_gate(left_id)
                not_r = self.build_not_gate(right_id)
                nor_id = self.build_nor_gate([not_l, not_r])
                return self.build_not_gate(nor_id)

            elif op == "XOR":
                # XOR(A, B) = NOR(NOR(A, B), NOR(NOT(A), NOT(B)))
                nor_ab = self.build_nor_gate([left_id, right_id])
                not_l = self.build_not_gate(left_id)
                not_r = self.build_not_gate(right_id)
                nor_not = self.build_nor_gate([not_l, not_r])
                return self.build_nor_gate([nor_ab, nor_not])

            elif op == "XNOR":
                # XNOR(A, B) = NOT(XOR(A, B))
                nor_ab = self.build_nor_gate([left_id, right_id])
                not_l = self.build_not_gate(left_id)
                not_r = self.build_not_gate(right_id)
                nor_not = self.build_nor_gate([not_l, not_r])
                xor_id = self.build_nor_gate([nor_ab, nor_not])
                return self.build_not_gate(xor_id)

            else:
                raise ValueError(f"Unsupported binary logic operation: '{op}'.")

        raise TypeError(f"Unknown AST node type: {type(node)}")


def decompose_to_nor_graph(ast: ASTNode, circuit_name: str = "BioCircuit") -> CircuitGraph:
    """Compile parsed Boolean logic into a validated CircuitGraph."""
    decomposer = NORDecomposer(circuit_name=circuit_name)
    top_gate_id = decomposer.decompose_ast(ast)
    out_node_id = "out_primary"
    decomposer.nodes[out_node_id] = LogicNode(
        node_id=out_node_id,
        gate_type="OUTPUT",
        inputs=[top_gate_id],
    )

    primary_inputs = sorted(set(decomposer.primary_inputs))
    return CircuitGraph(
        circuit_name=circuit_name,
        primary_inputs=primary_inputs,
        primary_output=out_node_id,
        nodes=decomposer.nodes,
    )
