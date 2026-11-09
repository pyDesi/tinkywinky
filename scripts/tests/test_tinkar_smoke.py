"""Pure smoke-helper checks; no network or dataset is used."""
import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tinkar_smoke import LiveSchema, grpc_records, public_ids, rest_records


def test_bit_uuid_matches_rest():
    assert public_ids({"uuid_bits": ["1126305346831801461", "11656082609334693159"]}) == [
        "0fa170be-da88-5c75-a1c2-b9606a00ad27"
    ]


def test_multiple_unsigned_uuid_pairs():
    values = [uuid.UUID(int=0), uuid.UUID(int=(1 << 128) - 1)]
    bits = [str(half) for value in values
            for half in (value.int >> 64, value.int & ((1 << 64) - 1))]
    assert public_ids({"uuid_bits": bits}) == sorted(map(str, values))


def test_legacy_string_ids():
    assert public_ids({"uuids": ["b", "a"]}) == ["a", "b"]


def test_malformed_bits_fail():
    with pytest.raises(RuntimeError, match="Odd number"):
        public_ids({"uuid_bits": ["123"]})


@pytest.mark.parametrize("method", [
    "IkeAdmin/ImportChangeset", "IkeAdmin/RunReasoner",
    "IkeGraphRAG/RebuildSearchIndex", "IkeKnowledgeGraph/SaveStampCoordinate",
    "IkeKnowledgeGraph/CommitEntities", "IkeKnowledgeGraph/UnknownFutureMethod",
])
def test_mutations_rejected_before_any_network_access(method):
    live = LiveSchema.__new__(LiveSchema)
    # No channel/pool initialized: any access would fail this test.
    with pytest.raises(RuntimeError, match="Refusing non-allowlisted"):
        live.call(method, {})


def test_record_comparison_keeps_uuid_and_name():
    remote = {"results": [{"public_id": {"uuids": ["id"]},
                           "descriptions": {"fully_qualified_name": "Device"}}]}
    http = {"results": [{"publicId": ["id"],
                         "descriptions": {"fullyQualifiedName": "Device"}}]}
    assert grpc_records(remote) == rest_records(http)
