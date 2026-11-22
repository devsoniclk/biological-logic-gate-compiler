"""Tests for command-line interface execution."""

from click.testing import CliRunner

from biological_logic_compiler.cli import cli


def test_cli_compile():
    runner = CliRunner()
    res = runner.invoke(cli, ["compile", "A AND B"])
    assert res.exit_code == 0
    assert "Synthesized Gate Assignments" in res.output

def test_cli_library():
    runner = CliRunner()
    res = runner.invoke(cli, ["library"])
    assert res.exit_code == 0
    assert "Orthogonal Repressor Library" in res.output
