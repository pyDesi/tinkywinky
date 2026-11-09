#!/usr/bin/env python3
"""Regenerate committed client stubs using this project's pinned grpcio-tools."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "vendor/ikm-python"
PROTOS = ["Tinkar", "ike_types", "ike_graph_rag", "ike_knowledge_graph", "ike_admin"]


def generate(output):
    output.mkdir(parents=True, exist_ok=True)
    for name in PROTOS:
        command = [sys.executable, "-m", "grpc_tools.protoc",
                   f"-I{CLIENT / 'proto'}", f"--python_out={output}",
                   f"--pyi_out={output}"]
        if name not in ("Tinkar", "ike_types"):
            command.append(f"--grpc_python_out={output}")
        subprocess.run(command + [str(CLIENT / "proto" / f"{name}.proto")], check=True)
    for path in output.glob("*.py"):
        path.write_text(re.sub(
            r"^import ((?:Tinkar|ike_\w+)_pb2)(?=\s|$)", r"from . import \1",
            path.read_text(), flags=re.MULTILINE,
        ))
    (output / "__init__.py").write_text("")


if __name__ == "__main__":
    generate(CLIENT / "src/tinkar/_generated")
