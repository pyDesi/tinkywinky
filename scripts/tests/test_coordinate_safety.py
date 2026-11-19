"""No service or dataset is opened here."""
from types import SimpleNamespace
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from coordinate_safety import has_coordinate_write, pytest_collection_modifyitems
from tinkar_smoke import LiveSchema, READ_ONLY


@pytest.mark.parametrize("kind", ["stamp", "navigation", "language"])
def test_all_coordinate_mutations_and_lazy_lists_refused_by_read_only_boundary(kind):
    live = LiveSchema.__new__(LiveSchema)
    suffix = kind.capitalize()
    for method in (f"Save{suffix}Coordinate", f"List{suffix}Coordinates"):
        rpc = f"IkeKnowledgeGraph/{method}"
        assert rpc not in READ_ONLY
        with pytest.raises(RuntimeError, match="Refusing non-allowlisted"):
            live.call(rpc, {})


def unmarked_example():
    client.knowledge_graph.save_language_coordinate()


def test_collection_audit_rejects_an_unmarked_save():
    item = SimpleNamespace(obj=unmarked_example, nodeid="unsafe-test",
                           get_closest_marker=lambda name: None)
    with pytest.raises(pytest.UsageError, match="Unmarked coordinate write"):
        pytest_collection_modifyitems([item])


def test_collection_audit_accepts_explicit_write_marker():
    item = SimpleNamespace(obj=unmarked_example, nodeid="write-test",
                           get_closest_marker=lambda name: object())
    pytest_collection_modifyitems([item])


def test_audit_detects_save_passed_to_a_skip_wrapper():
    assert has_coordinate_write(
        "save_or_skip(client.knowledge_graph.save_stamp_coordinate, allowed_states='ACTIVE')"
    )
