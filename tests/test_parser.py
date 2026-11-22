"""Tests for Boolean expression tokenizer and recursive descent parser."""

import pytest

from biological_logic_compiler.parser import (
    NotNode,
    extract_variables,
    parse_boolean_expression,
    tokenize,
)


def test_tokenize_valid():
    tokens = tokenize("A AND NOT(B) OR C")
    assert tokens == ["A", "AND", "NOT", "(", "B", ")", "OR", "C"]

def test_tokenize_invalid():
    with pytest.raises(ValueError):
        tokenize("A @ B")

def test_parse_simple_not():
    ast = parse_boolean_expression("NOT A")
    assert isinstance(ast, NotNode)
    assert ast.evaluate({"A": True}) is False
    assert ast.evaluate({"A": False}) is True

def test_parse_binary_ops():
    cases = [
        ("A AND B", {"A": True, "B": False}, False),
        ("A OR B", {"A": True, "B": False}, True),
        ("A NAND B", {"A": True, "B": True}, False),
        ("A NOR B", {"A": False, "B": False}, True),
        ("A XOR B", {"A": True, "B": True}, False),
        ("A XNOR B", {"A": True, "B": True}, True),
    ]
    for expr, env, expected in cases:
        ast = parse_boolean_expression(expr)
        assert ast.evaluate(env) == expected

def test_extract_variables():
    ast = parse_boolean_expression("(A AND B) OR (NOT(C) AND A)")
    vars_found = extract_variables(ast)
    assert vars_found == ["A", "B", "C"]

def test_parse_errors():
    with pytest.raises(ValueError):
        parse_boolean_expression("")
    with pytest.raises(ValueError):
        parse_boolean_expression("A AND")
