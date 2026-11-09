"""Current wire-format regressions. Mocks never connect to or mutate a store."""
import runpy
import tomllib
import uuid
from pathlib import Path
from types import SimpleNamespace

import grpc
import pytest

from tinkar import CoordinateOverride, TinkarClient, TinkarError
from tinkar._generated import Tinkar_pb2 as schema
from tinkar._generated import ike_types_pb2 as types
from tinkar._generated import ike_knowledge_graph_pb2 as kg
from tinkar._services.knowledge_graph import KnowledgeGraphNamespace
from tinkar._wire import public_id, public_ids, stamp_from_proto

ROOT = Path(__file__).resolve().parents[2]
ID = "0fa170be-da88-5c75-a1c2-b9606a00ad27"
OTHER = "ffffffff-ffff-ffff-ffff-ffffffffffff"
STAMP = schema.StampVersion(
    status_public_id=public_id(ID), author_public_id=public_id(OTHER),
    module_public_id=public_id(ID), path_public_id=public_id(OTHER), time=123,
)


@pytest.mark.parametrize("identifier", [ID, OTHER, str(uuid.UUID(int=0))])
def test_uuid_unsigned_bit_words_round_trip(identifier):
    value = public_id(identifier)
    assert not value.uuids
    assert public_ids(schema.PublicId.FromString(value.SerializeToString())) == [identifier]


def test_multiple_ids_and_legacy_deduplication():
    value = schema.PublicId(uuid_bits=[*public_id(ID).uuid_bits, *public_id(OTHER).uuid_bits],
                            uuids=[OTHER, ID, ID])
    assert public_ids(value) == [ID, OTHER]
    assert public_ids(schema.PublicId(uuids=[ID.upper(), ID])) == [ID]


@pytest.mark.parametrize("value", [
    schema.PublicId(), schema.PublicId(uuid_bits=[123]),
    schema.PublicId(sequence=1), schema.PublicId(uuids=["not-a-uuid"]),
    schema.PublicId(uuid_bits=public_id(ID).uuid_bits, uuids=[OTHER]),
])
def test_malformed_unresolved_or_missing_ids_fail_explicitly(value):
    with pytest.raises(TinkarError) as error:
        public_ids(value)
    assert error.value.code == "protocol_error"


def test_optional_empty_id_is_distinct_from_malformed_id():
    assert public_ids(schema.PublicId(), required=False) == []
    with pytest.raises(TinkarError):
        public_ids(schema.PublicId(sequence=3), required=False)


def test_all_stamp_ids_and_timestamp_survive():
    stamp = stamp_from_proto(STAMP)
    assert (stamp.status, stamp.author, stamp.module, stamp.path, stamp.time) == (
        ID, OTHER, ID, OTHER, 123)
    with pytest.raises(TinkarError):
        stamp_from_proto(schema.StampVersion(time=123))


class RecordingChannel:
    """Exercise generated stubs, serializers, response converters and full RPC paths."""
    def __init__(self):
        self.calls = []

    def close(self):
        pass

    def unary_unary(self, path, request_serializer, response_deserializer, **kwargs):
        def call(request, timeout=None):
            request_serializer(request)
            self.calls.append((path, request, timeout))
            operation = path.rsplit("/", 1)[1]
            if operation == "InspectConcept":
                response = types.TinkarConceptSemanticsResponse(
                    success=True, concept_public_id=public_id(ID), total_count=1,
                    created_at=123, semantics=[types.TinkarConceptSemanticInfo(
                        semantic_public_id=public_id(OTHER), pattern_public_id=public_id(ID),
                        named_fields=[types.TinkarSemanticField(name="GS1", value="1234")],
                        stamp=types.TinkarStampInfo(status="Active", time=123))])
            elif operation in ("GetEntityByPublicId", "LoadConceptEntityGraph"):
                response = types.TinkarConceptEntityResponse(success=True, entities=[
                    schema.TinkarMsg(concept_chronology=schema.ConceptChronology(
                        public_id=public_id(ID)))])
            elif operation == "RebuildSearchIndex":
                response = types.TinkarRebuildIndexResponse(success=True, message="mock only")
            elif operation == "ConceptSearchWithSort":
                response = types.TinkarConceptSearchWithSortResponse(
                    success=True, total_count=1, created_at=123,
                    results=[types.TinkarSemanticSearchResult(public_id=public_id(ID))],
                    grouped_results=[types.TinkarGroupedSearchResult(
                        public_id=public_id(ID), preferred_name="Device",
                        matching_semantics=[types.TinkarMatchingSemantic(
                            public_id=public_id(OTHER))])])
            else:
                response = types.TinkarSearchQueryResponse(
                    success=True, total_count=1, created_at=123,
                    results=[types.TinkarSearchResult(public_id=public_id(ID), stamp=STAMP)])
            # Deserialize through the generated stub, not a hand-built model.
            return response_deserializer(response.SerializeToString())
        return call

    def unary_stream(self, *args, **kwargs):
        return self._stream_not_supported

    def stream_stream(self, *args, **kwargs):
        return self._stream_not_supported

    @staticmethod
    def _stream_not_supported(*args, **kwargs):
        raise AssertionError("Legacy admin guard must reject before sending")


@pytest.fixture
def client(monkeypatch):
    channel = RecordingChannel()
    monkeypatch.setattr(grpc, "insecure_channel", lambda address: channel)
    with TinkarClient(port=9000) as result:
        yield result, channel


@pytest.mark.parametrize("operation,args,rpc,tier", [
    ("search", ["device"], "Search", "IkeGraphRAG"),
    ("concept_search", ["device"], "ConceptSearch", "IkeGraphRAG"),
    ("concept_search_with_sort", ["device"], "ConceptSearchWithSort", "IkeGraphRAG"),
    ("get_entity", [ID], "GetEntity", "IkeGraphRAG"),
    ("get_child_concepts", [ID], "GetChildConcepts", "IkeGraphRAG"),
    ("get_descendant_concepts", [ID], "GetDescendantConcepts", "IkeGraphRAG"),
    ("get_lidr_record_concepts_from_test_kit", [ID], "GetLIDRRecordConceptsFromTestKit", "IkeGraphRAG"),
    ("get_result_conformance_concepts_from_lidr_record", [ID],
     "GetResultConformanceConceptsFromLIDRRecord", "IkeGraphRAG"),
    ("get_allowed_result_concepts_from_result_conformance", [ID],
     "GetAllowedResultConceptsFromResultConformance", "IkeGraphRAG"),
    ("rebuild_search_index", [], "RebuildSearchIndex", "IkeGraphRAG"),
    ("inspect_concept", [ID], "InspectConcept", "IkeKnowledgeGraph"),
    ("get_entity_by_public_id", [ID], "GetEntityByPublicId", "IkeKnowledgeGraph"),
    ("load_concept_entity_graph", [ID], "LoadConceptEntityGraph", "IkeKnowledgeGraph"),
])
def test_every_legacy_method_routes_to_current_service(client, operation, args, rpc, tier):
    sdk, channel = client
    response = getattr(sdk.tinkar, operation)(*args, timeout=17)
    assert response.success
    path, request, timeout = channel.calls[-1]
    assert path == f"/dev.ikm.tinkar.service.{tier}/{rpc}"
    assert timeout == 17
    assert "TinkarSearchService" not in path
    if tier == "IkeKnowledgeGraph":
        assert request.DESCRIPTOR.full_name.endswith(".KnowledgeGraphConceptRequest")
        assert public_ids(request.public_id) == [ID]


def test_packed_ids_survive_all_result_shapes(client):
    sdk, _ = client
    assert sdk.search.concepts("device").results[0].public_id == [ID]
    assert sdk.entities.get(ID).concept.stamp.author == OTHER
    assert sdk.lidr.records(ID).concepts[0].public_id == [ID]
    assert sdk.knowledge_graph.children(ID).concepts[0].stamp.path == OTHER
    grouped = sdk.search.concepts_by_component("device").results[0]
    assert grouped.public_id == [ID] and grouped.concept_nid is None
    assert grouped.preferred_name == "Device"
    assert grouped.matching_semantics[0].public_id == [OTHER]
    assert grouped.matching_semantics[0].semantic_nid is None
    assert sdk.search.concepts_by_semantic("device").results[0].public_id == [ID]
    semantics = sdk.knowledge_graph.semantics(ID)
    assert semantics.concept_public_id == [ID]
    assert semantics.semantics[0].semantic_public_id == [OTHER]
    assert semantics.semantics[0].pattern_public_id == [ID]
    assert semantics.semantics[0].named_fields[0].name == "GS1"
    assert semantics.semantics[0].stamp.time == 123
    assert semantics.created_at == 123


def test_override_public_id_fields_use_current_numbers_and_preserve_order():
    namespace = KnowledgeGraphNamespace(None, 30)
    override = CoordinateOverride(position_path_id=ID, module_ids=[ID, OTHER],
                                  excluded_module_ids=[OTHER],
                                  module_priority_ids=[OTHER, ID], position_time=123)
    request = namespace._make_kg_request(ID, override)
    decoded = kg.KnowledgeGraphConceptRequest.FromString(request.SerializeToString())
    wire = decoded.coordinate_override
    assert public_ids(decoded.public_id) == [ID]
    assert public_ids(wire.position_path_id) == [ID]
    assert [public_ids(item) for item in wire.module_ids] == [[ID], [OTHER]]
    assert [public_ids(item) for item in wire.excluded_module_ids] == [[OTHER]]
    assert [public_ids(item) for item in wire.module_priority_ids] == [[OTHER], [ID]]
    for name, number in (("position_path_id", 9), ("module_ids", 10),
                         ("excluded_module_ids", 11), ("module_priority_ids", 12)):
        assert wire.DESCRIPTOR.fields_by_name[name].number == number
    assert wire.position_time == 123
    assert not namespace._make_kg_request(ID, None).HasField("coordinate_override")
    assert not namespace._make_kg_request(ID, CoordinateOverride()).coordinate_override.HasField(
        "position_path_id")


def test_saved_settings_conversion_without_a_dataset():
    captured = []

    def save(request, timeout):
        captured.append(kg.SaveStampCoordinateRequest.FromString(request.SerializeToString()))
        return kg.SavedStampCoordinateResponse(id=public_id(ID), created_at="2026-11-09T00:00:00Z")

    namespace = KnowledgeGraphNamespace(SimpleNamespace(SaveStampCoordinate=save), 30)
    response = namespace.save_stamp_coordinate(
        position_path_id=ID, module_ids=[OTHER], excluded_module_ids=[ID],
        module_priority_ids=[OTHER, ID],
    )
    settings = captured[0].settings
    assert public_ids(settings.position_path_id) == [ID]
    assert [public_ids(v) for v in settings.module_ids] == [[OTHER]]
    assert [public_ids(v) for v in settings.excluded_module_ids] == [[ID]]
    assert [public_ids(v) for v in settings.module_priority_ids] == [[OTHER], [ID]]
    assert response.id == ID
    assert response.public_id == [ID]
    with pytest.raises(TinkarError):
        namespace._saved_coordinate(kg.SavedStampCoordinateResponse())


def test_saved_coordinate_references_use_public_id_messages():
    captured = []

    def inspect(request, timeout):
        captured.append(kg.SemanticsWithCoordinateRequest.FromString(request.SerializeToString()))
        return types.TinkarConceptSemanticsResponse(success=True, concept_public_id=public_id(ID))

    namespace = KnowledgeGraphNamespace(SimpleNamespace(GetSemanticsWithCoordinate=inspect), 30)
    namespace.semantics_with_coordinate(
        ID, stamp_coordinate_id=ID, navigation_coordinate_id=OTHER, language_coordinate_id=ID)
    request = captured[0]
    assert public_ids(request.stamp_coordinate_id) == [ID]
    assert public_ids(request.navigation_coordinate_id) == [OTHER]
    assert public_ids(request.language_coordinate_id) == [ID]
    namespace.semantics_with_coordinate(ID)
    assert not captured[1].HasField("stamp_coordinate_id")


def test_coordinate_lists_preserve_all_ids_and_settings():
    identifier = schema.PublicId(uuid_bits=[*public_id(ID).uuid_bits, *public_id(OTHER).uuid_bits])
    def list_stamps(request, timeout):
        return kg.ListStampCoordinatesResponse(coordinates=[
            kg.SavedStampCoordinateResponse(
                id=identifier, settings=kg.StampCoordinateSettings(
                    position_path_id=public_id(ID), module_ids=[public_id(OTHER)],
                    excluded_module_ids=[public_id(ID)],
                    module_priority_ids=[public_id(OTHER), public_id(ID)]))])
    namespace = KnowledgeGraphNamespace(SimpleNamespace(ListStampCoordinates=list_stamps), 30)
    stamp = namespace.list_stamp_coordinates().stamps[0]
    assert stamp.id == ID and stamp.public_id == [ID, OTHER]
    assert stamp.position_path_id == ID and stamp.module_ids == [OTHER]
    assert stamp.excluded_module_ids == [ID] and stamp.module_priority_ids == [OTHER, ID]


def test_missing_pattern_id_is_explicitly_unavailable_not_invented():
    response = types.TinkarConceptSemanticsResponse(
        success=True, concept_public_id=public_id(ID), semantics=[
            types.TinkarConceptSemanticInfo(semantic_public_id=public_id(OTHER),
                                          pattern_name="Resolved name, absent ID")])
    converted = KnowledgeGraphNamespace(None, 30)._to_semantics_response(response)
    assert converted.semantics[0].semantic_public_id == [OTHER]
    assert converted.semantics[0].pattern_public_id is None


def test_success_flag_cannot_hide_missing_record_identifiers(client):
    sdk, _ = client
    response = types.TinkarSearchQueryResponse(
        success=True, total_count=1, results=[types.TinkarSearchResult()])
    with pytest.raises(TinkarError) as error:
        sdk.search._to_search_response(response, "device")
    assert error.value.code == "protocol_error"
    semantic_response = types.TinkarConceptSemanticsResponse(
        success=True, concept_public_id=public_id(ID),
        semantics=[types.TinkarConceptSemanticInfo(pattern_name="name is not an ID")])
    with pytest.raises(TinkarError):
        sdk.knowledge_graph._to_semantics_response(semantic_response)


@pytest.mark.parametrize("method,args", [
    ("import_changeset", [b"never sent"]), ("export_entities", []), ("run_reasoner", []),
])
def test_obsolete_unary_admin_methods_fail_before_any_rpc(client, method, args):
    sdk, channel = client
    with pytest.raises(TinkarError, match="No request was sent") as error:
        getattr(sdk.admin, method)(*args)
    assert error.value.code == "unsupported_operation"
    assert channel.calls == []


def test_generated_stubs_match_committed_schema_and_minimum_runtime(tmp_path):
    generate = runpy.run_path(str(ROOT / "scripts/generate-tinkar-client.py"))["generate"]
    generate(tmp_path)
    committed = ROOT / "vendor/ikm-python/src/tinkar/_generated"
    files = {p.name for p in tmp_path.iterdir() if p.is_file()}
    assert files == {p.name for p in committed.iterdir() if p.is_file()}
    for name in files:
        assert (tmp_path / name).read_bytes() == (committed / name).read_bytes(), name
    metadata = tomllib.loads((ROOT / "vendor/ikm-python/pyproject.toml").read_text())
    assert "grpcio>=1.81.0" in metadata["project"]["dependencies"]
    for name in ("ike_graph_rag", "ike_knowledge_graph", "ike_admin"):
        assert "GRPC_GENERATED_VERSION = '1.81.0'" in (
            committed / f"{name}_pb2_grpc.py").read_text()
