"""Network-free safety and matching tests for the UI's read-only scenario runner."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

spec = importlib.util.spec_from_file_location(
    "tinkar_workbench", Path(__file__).resolve().parents[1] / "tinkar_workbench.py")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


def test_write_rpc_is_rejected_before_dispatch():
    def dispatch(*args):
        pytest.fail("A write was dispatched")
    with pytest.raises(RuntimeError, match="Refusing"):
        worker.ReadOnlyInterceptor().intercept_unary_unary(
            dispatch, SimpleNamespace(method="/dev.ikm.tinkar.service.IkeKnowledgeGraph/SaveStampCoordinate"), None)


def test_read_rpc_is_allowed():
    assert worker.ReadOnlyInterceptor().intercept_unary_unary(
        lambda details, request: "ok",
        SimpleNamespace(method="/dev.ikm.tinkar.service.IkeGraphRAG/ConceptSearch"), None) == "ok"


@pytest.mark.parametrize("case,count", [(1, 1), (2, 4), (3, 12)])
def test_cases_use_fixed_upstream_fixture_counts(case, count):
    def fake_inspect(label, query, expected):
        return dict(label=label, status="missing", parity="match",
                    semanticCount=0, stampCount=0, message="missing")
    with patch.object(worker, "inspect_device", side_effect=fake_inspect):
        result = worker.run(case)
    assert len(result["devices"]) == count
    assert result["missing"] == count
    assert result["found"] == result["errors"] == 0


def test_search_parity_ignores_record_order_not_identifiers():
    grpc = [SimpleNamespace(public_id=["a"], fully_qualified_name="A"),
            SimpleNamespace(public_id=["b"], fully_qualified_name="B")]
    rest = [{"publicId": ["b"], "descriptions": {"fullyQualifiedName": "B"}},
            {"publicId": ["a"], "descriptions": {"fullyQualifiedName": "A"}}]
    assert worker.record_pairs(grpc) == worker.record_pairs(rest, rest=True)
    rest[0]["publicId"] = ["c"]
    assert worker.record_pairs(grpc) != worker.record_pairs(rest, rest=True)
