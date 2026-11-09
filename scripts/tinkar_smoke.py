#!/usr/bin/env python3
"""Read-only REST / live-schema gRPC / project-managed Python client comparison.

Exit 0 means all schema, identifier, stamp and transport checks pass.
Failures are never downgraded to a successful monitoring result.
"""
import argparse
import json
import sys
import uuid
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import grpc
from google.protobuf import descriptor_pool, json_format, message_factory
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import (
    ProtoReflectionDescriptorDatabase,
)

ROOT = Path(__file__).resolve().parents[1]
SERVICE = "dev.ikm.tinkar.service."
# Deliberately not a denylist: unknown/new RPCs cannot accidentally write.
READ_ONLY = {
    "IkeGraphRAG/ConceptSearch", "IkeGraphRAG/GetEntity",
    "IkeGraphRAG/GetChildConcepts", "IkeGraphRAG/GetDescendantConcepts",
    "IkeKnowledgeGraph/InspectConcept", "IkeKnowledgeGraph/GetChildConcepts",
    "IkeKnowledgeGraph/GetDescendantConcepts",
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class LiveSchema:
    """Separate descriptor pool: independently verify the client's vendored stubs."""

    def __init__(self, channel):
        self.channel = channel
        self.db = ProtoReflectionDescriptorDatabase(channel)
        self.pool = descriptor_pool.DescriptorPool(self.db)

    def call(self, method, payload):
        require(method in READ_ONLY, f"Refusing non-allowlisted RPC: {method}")
        service, name = method.split("/")
        descriptor = self.pool.FindServiceByName(SERVICE + service).methods_by_name[name]
        request_type = message_factory.GetMessageClass(descriptor.input_type)
        response_type = message_factory.GetMessageClass(descriptor.output_type)
        request = json_format.ParseDict(payload, request_type())
        response = self.channel.unary_unary(
            "/" + SERVICE + method,
            request_serializer=request_type.SerializeToString,
            response_deserializer=response_type.FromString,
        )(request, timeout=30)
        result = json_format.MessageToDict(response, preserving_proto_field_name=True)
        require(result.get("success"), f"{method}: {result.get('error_message', result)}")
        return result


def public_ids(value):
    """Decode both supported schema representations, without patching the client."""
    bits = value.get("uuid_bits", [])
    require(len(bits) % 2 == 0, "Odd number of UUID bit halves")
    return sorted(value.get("uuids", []) + [
        str(uuid.UUID(int=(int(bits[i]) << 64) | int(bits[i + 1])))
        for i in range(0, len(bits), 2)
    ])


def grpc_records(response):
    return sorted((
        tuple(public_ids(r["public_id"])),
        r.get("descriptions", {}).get("fully_qualified_name", ""),
    ) for r in response.get("results", []))


def rest_records(response):
    return sorted((
        tuple(sorted(r["publicId"])),
        r.get("descriptions", {}).get("fullyQualifiedName", ""),
    ) for r in response.get("results", []))


def assert_client_stamps(records, http):
    expected = {
        tuple(sorted(r["publicId"])): r.get("stamp") for r in http["results"]
    }
    for record in records:
        stamp = expected[tuple(sorted(record.public_id))]
        require(stamp and record.stamp, "A real record stamp was lost")
        actual = record.stamp
        require(
            (actual.status, actual.author, actual.module, actual.path, actual.time) ==
            (stamp["statusPublicId"], stamp["authorPublicId"], stamp["modulePublicId"],
             stamp["pathPublicId"], int(stamp["time"])),
            f"Python stamp differs for {record.public_id}",
        )


def verify_client_schema(live):
    from tinkar._generated import (
        Tinkar_pb2, ike_types_pb2, ike_admin_pb2,
        ike_graph_rag_pb2, ike_knowledge_graph_pb2,
    )
    from google.protobuf.descriptor_pb2 import FileDescriptorProto

    def contract(file):
        # Ignore Java/Python generator options and source locations, not the wire contract.
        copy = FileDescriptorProto()
        file.CopyToProto(copy)
        copy.ClearField("options")
        copy.ClearField("source_code_info")
        for message in copy.message_type:
            for field in message.field:
                field.ClearField("json_name")
                field.ClearField("options")
        return copy

    for module in (Tinkar_pb2, ike_types_pb2, ike_admin_pb2,
                   ike_graph_rag_pb2, ike_knowledge_graph_pb2):
        expected = live.pool.FindFileByName(module.DESCRIPTOR.name)
        require(contract(module.DESCRIPTOR) == contract(expected),
                f"Client schema differs from reflected server: {module.DESCRIPTOR.name}")
    print("PASS vendored schemas match the active reflected wire contracts")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grpc-port", type=int, default=9000)
    parser.add_argument("--rest-base", default="http://localhost:8099/tinkar/api")
    parser.add_argument("--client-source", type=Path,
                        default=ROOT / "vendor/ikm-python/src")
    args = parser.parse_args()
    # This utility is intentionally internal-only; external forwarding is out of scope.
    require(args.grpc_port in (9000, 9001), "Only internal verification ports are supported")
    require(args.client_source.is_dir(), "The project-managed Python client is missing")
    sys.path.insert(0, str(args.client_source))
    from tinkar import TinkarClient, TinkarError

    def rest(path, **params):
        with urlopen(args.rest_base.rstrip("/") + "/" + path + "?" + urlencode(params),
                     timeout=30) as response:
            data = json.load(response)
        require(data.get("success"), f"REST {path}: {data}")
        return data

    with grpc.insecure_channel(f"localhost:{args.grpc_port}") as channel, \
            TinkarClient(host="localhost", port=args.grpc_port, timeout=30) as client:
        grpc.channel_ready_future(channel).result(timeout=15)
        live = LiveSchema(channel)
        verify_client_schema(live)
        services = list(live.db.get_services())
        print("gRPC services:", ", ".join(sorted(services)))
        fixture = None
        for query in ("device", "albumin", "catheter"):
            remote = live.call("IkeGraphRAG/ConceptSearch",
                               {"query": query, "max_results": 3})
            http = rest("ike/graphrag/concept-search", query=query, maxResults=3)
            expected = rest_records(http)
            require(expected and grpc_records(remote) == expected,
                    f"Search differs or is empty: {query}")
            response = client.search.concepts(query, max_results=3)
            actual = sorted((tuple(sorted(r.public_id)), r.fully_qualified_name)
                            for r in response.results)
            require(actual == expected, f"Python search IDs/names differ: {actual} vs {expected}")
            assert_client_stamps(response.results, http)
            require(response.created_at and response.created_at > 0,
                    "Python search response timestamp was lost")
            print(f"PASS search {query!r}: {len(expected)} UUID/name pairs match REST")
            fixture = fixture or expected[0]

        concept_id, name = fixture[0][0], fixture[1]
        print("Fixture:", concept_id, name)
        payload = {"public_id": {"uuids": [concept_id]}}
        # InspectConcept takes the same public_id request as Tier 1.
        remote = live.call("IkeGraphRAG/GetEntity", payload)
        http = rest("ike/graphrag/entity", conceptId=concept_id)
        require(grpc_records(remote) == rest_records(http), "Entity UUID/name differs")
        concept = client.entities.get(concept_id).concept
        require(concept.fully_qualified_name == name, "Python entity name differs")
        require(concept.public_id == list(fixture[0]), "Python entity public IDs differ")
        assert_client_stamps([concept], http)
        print("PASS entity: current-schema gRPC and REST agree; Python name agrees")
        # Public GUDID parent of the device fixture: exercises non-empty navigation
        # rather than accepting only the empty children of a leaf.
        parent_id = "f816dfb5-cc6d-5334-a0b4-c6e844689a30"
        parent_payload = {"public_id": {"uuids": [parent_id]}}

        for tier, prefix in (("IkeGraphRAG", "graphrag"),
                             ("IkeKnowledgeGraph", "knowledgegraph")):
            for rpc, endpoint in (("GetChildConcepts", "children"),
                                  ("GetDescendantConcepts", "descendants")):
                remote = live.call(f"{tier}/{rpc}", parent_payload)
                http = rest(f"ike/{prefix}/{endpoint}", conceptId=parent_id)
                require(grpc_records(remote) and grpc_records(remote) == rest_records(http),
                        f"Hierarchy differs or is empty: {tier}/{rpc}")
                namespace = client.entities if tier == "IkeGraphRAG" else client.knowledge_graph
                result = getattr(namespace, endpoint)(parent_id)
                require(
                    sorted((tuple(sorted(r.public_id)), r.fully_qualified_name)
                           for r in result.concepts) == rest_records(http),
                    f"Python hierarchy differs: {tier}/{rpc}",
                )
                assert_client_stamps(result.concepts, http)
                print(f"PASS {tier}/{rpc}: {len(grpc_records(remote))} matching records")

        remote = live.call("IkeKnowledgeGraph/InspectConcept", payload)
        http = rest("ike/knowledgegraph/semantics", conceptId=concept_id)
        grpc_sem = sorted((tuple(public_ids(s["semantic_public_id"])),
                           s.get("pattern_name", ""),
                           tuple(f.get("value", "") for f in s.get("named_fields", [])),
                           int(s.get("stamp", {}).get("time", 0)))
                          for s in remote.get("semantics", []))
        rest_sem = sorted(((s["semanticId"],), s.get("patternName", ""),
                           tuple(f["value"] for f in s.get("fields", [])),
                           int(s.get("stamp", {}).get("time", 0)))
                          for s in http.get("semantics", []))
        require(grpc_sem and grpc_sem == rest_sem, "Semantic IDs/patterns differ or are empty")
        semantics = client.knowledge_graph.semantics(concept_id)
        require(semantics.total_count == len(rest_sem), "Python semantics count differs")
        require(semantics.concept_public_id == [concept_id] and
                sorted(tuple(sorted(s.semantic_public_id)) for s in semantics.semantics)
                == sorted(record[0] for record in rest_sem),
                "Python semantic public IDs differ")
        reflected = {tuple(public_ids(s["semantic_public_id"])): s
                     for s in remote["semantics"]}
        for semantic in semantics.semantics:
            item = reflected[tuple(sorted(semantic.semantic_public_id))]
            require(semantic.pattern_public_id ==
                    (public_ids(item.get("pattern_public_id", {})) or None),
                    "Python semantic pattern ID differs")
            require(
                [(f.name, f.value) for f in semantic.named_fields] ==
                [(f.get("name", ""), f.get("value", ""))
                 for f in item.get("named_fields", [])],
                "Python named semantic fields differ",
            )
            require(semantic.stamp and semantic.stamp.time ==
                    int(item.get("stamp", {}).get("time", 0)),
                    "Python semantic stamp was lost")
        print(f"PASS semantics: {len(rest_sem)} UUID/pattern/field/stamp records match REST")
        for operation in ("inspect_concept", "get_entity_by_public_id",
                          "load_concept_entity_graph"):
            try:
                result = getattr(client.tinkar, operation)(concept_id)
            except TinkarError as error:
                raise RuntimeError(f"Legacy adapter {operation} failed: {error}") from error
            else:
                if operation == "inspect_concept":
                    require(result.concept_public_id == [concept_id] and
                            sorted(tuple(sorted(s.semantic_public_id)) for s in result.semantics)
                            == sorted(record[0] for record in rest_sem),
                            "Legacy inspection adapter lost semantic IDs")
                else:
                    from tinkar._generated.Tinkar_pb2 import TinkarMsg
                    entity_ids = []
                    for raw in result.entities:
                        message = json_format.MessageToDict(
                            TinkarMsg.FromString(raw), preserving_proto_field_name=True)
                        for chronology in message.values():
                            if isinstance(chronology, dict) and "public_id" in chronology:
                                entity_ids.extend(public_ids(chronology["public_id"]))
                    require(concept_id in entity_ids, f"{operation} lost the concept ID")
                print(f"PASS legacy adapter {operation}: current service, real IDs")
    print("Read-only transport/data parity: PASS")
    print("Python client compatibility: PASS")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"FAIL: {type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
