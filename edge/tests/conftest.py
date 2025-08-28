import os
import sys
from pathlib import Path


def _ensure_import_paths() -> None:
    # edge/tests -> edge -> project root
    tests_dir = Path(__file__).resolve().parent
    edge_dir = tests_dir.parent
    project_root = edge_dir.parent

    paths_to_add = [
        str(project_root),
        str(edge_dir),
        str(edge_dir / "src"),
    ]

    # Prepend to sys.path to take precedence
    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)

    # Also export PYTHONPATH for any subprocesses
    existing = os.environ.get("PYTHONPATH", "")
    composite = ":".join([*paths_to_add, existing]) if existing else ":".join(paths_to_add)
    os.environ["PYTHONPATH"] = composite


_ensure_import_paths()


