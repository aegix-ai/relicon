"""Learning code must never see the simulator's hidden truth."""
import ast
import subprocess
import sys
from pathlib import Path

LEARNING = Path(__file__).parents[1] / "relicon" / "learning"


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            out.append("." * node.level + mod)
            out += ["." * node.level + mod + "." + a.name for a in node.names]
    return out


def test_learning_source_never_imports_simulator():
    bad = [(p.name, i) for p in LEARNING.rglob("*.py") for i in _imports(p) if "simulator" in i or "truth" in i]
    assert not bad, f"learning/ imports simulator code: {bad}"


def test_learning_runtime_does_not_load_truth():
    code = ("import sys, relicon.learning.engine, relicon.learning.bandit, relicon.learning.insights;"
            "bad=[m for m in sys.modules if m.startswith('relicon.simulator')];print(bad);sys.exit(1 if bad else 0)")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_boundary_check_catches_a_violation(tmp_path):
    f = tmp_path / "leak.py"
    f.write_text("from ..simulator.truth import model\n")
    assert any("truth" in i for i in _imports(f))
