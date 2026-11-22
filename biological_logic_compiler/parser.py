"""Formal Boolean logic AST parser and tokenizer."""

import re


class ASTNode:
    """Abstract syntax tree node representing a Boolean sub-expression."""


class VarNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, env: dict[str, bool]) -> bool:
        if self.name not in env:
            raise KeyError(f"Variable '{self.name}' missing from evaluation environment.")
        return env[self.name]

    def __repr__(self) -> str:
        return f"Var({self.name})"


class NotNode(ASTNode):
    def __init__(self, child: ASTNode):
        self.child = child

    def evaluate(self, env: dict[str, bool]) -> bool:
        return not self.child.evaluate(env)

    def __repr__(self) -> str:
        return f"NOT({self.child})"


class BinaryOpNode(ASTNode):
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op.upper()
        self.left = left
        self.right = right

    def evaluate(self, env: dict[str, bool]) -> bool:
        l_val = self.left.evaluate(env)
        r_val = self.right.evaluate(env)
        if self.op == "AND":
            return l_val and r_val
        elif self.op == "OR":
            return l_val or r_val
        elif self.op == "NAND":
            return not (l_val and r_val)
        elif self.op == "NOR":
            return not (l_val or r_val)
        elif self.op == "XOR":
            return l_val != r_val
        elif self.op == "XNOR":
            return l_val == r_val
        else:
            raise ValueError(f"Unknown binary operator '{self.op}'.")

    def __repr__(self) -> str:
        return f"{self.op}({self.left}, {self.right})"


def tokenize(expression: str) -> list[str]:
    """Tokenize a Boolean logic expression string."""
    pattern = r'\s*([A-Za-z0-9_]+|\(|\)|NOT|AND|OR|NAND|NOR|XOR|XNOR)\s*'
    tokens = []
    pos = 0
    while pos < len(expression):
        match = re.match(pattern, expression[pos:], re.IGNORECASE)
        if not match:
            if expression[pos].isspace():
                pos += 1
                continue
            raise ValueError(f"Syntax error near character '{expression[pos]}' at index {pos}")
        token = match.group(1)
        tokens.append(token)
        pos += match.end()
    return tokens


class Parser:
    """Recursive descent Boolean logic expression parser."""
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> str | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected: str | None = None) -> str:
        token = self.current_token()
        if token is None:
            raise ValueError(f"Unexpected end of input; expected '{expected}'.")
        if expected and token.upper() != expected.upper():
            raise ValueError(f"Expected '{expected}', found '{token}'.")
        self.pos += 1
        return token

    def parse(self) -> ASTNode:
        node = self.parse_or()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token '{self.current_token()}' after expression.")
        return node

    def parse_or(self) -> ASTNode:
        left = self.parse_xor()
        while self.current_token() and self.current_token().upper() in ("OR", "NOR"):
            op = self.consume().upper()
            right = self.parse_xor()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_xor(self) -> ASTNode:
        left = self.parse_and()
        while self.current_token() and self.current_token().upper() in ("XOR", "XNOR"):
            op = self.consume().upper()
            right = self.parse_and()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_and(self) -> ASTNode:
        left = self.parse_not()
        while self.current_token() and self.current_token().upper() in ("AND", "NAND"):
            op = self.consume().upper()
            right = self.parse_not()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_not(self) -> ASTNode:
        if self.current_token() and self.current_token().upper() == "NOT":
            self.consume("NOT")
            child = self.parse_not()
            return NotNode(child)
        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        token = self.current_token()
        if token == "(":
            self.consume("(")
            node = self.parse_or()
            self.consume(")")
            return node
        elif token and re.match(r'^[A-Za-z0-9_]+$', token):
            var_name = self.consume()
            return VarNode(var_name)
        else:
            raise ValueError(f"Unexpected token in expression: '{token}'.")


def parse_boolean_expression(expression: str) -> ASTNode:
    """Parse text representation into an executable ASTNode tree."""
    tokens = tokenize(expression)
    if not tokens:
        raise ValueError("Cannot parse empty expression.")
    parser = Parser(tokens)
    return parser.parse()


def extract_variables(ast: ASTNode) -> list[str]:
    """Retrieve unique variable symbols used across an AST."""
    vars_set = set()

    def traverse(node: ASTNode):
        if isinstance(node, VarNode):
            vars_set.add(node.name)
        elif isinstance(node, NotNode):
            traverse(node.child)
        elif isinstance(node, BinaryOpNode):
            traverse(node.left)
            traverse(node.right)

    traverse(ast)
    return sorted(vars_set)
