#!/usr/bin/env python3
"""Read-only REST / live-schema gRPC / unmodified ikm-python comparison.

Default exit: 0=all checks pass, 1=transport/data failure, 2=client mismatch.
--allow-known-client-mismatch permits only the explicitly identified old-client
UUID and removed-service mismatches; it never suppresses transport/data failures.
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
    """Separate descriptor pool: never contaminate the client's vendored stubs."""

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grpc-port", type=int, default=9000)
    parser.add_argument("--rest-base", default="http://localhost:8099/tinkar/api")
    parser.add_argument("--client-source", type=Path,
                        default=ROOT / ".local/upstream/ikm-python/src")
    parser.add_argument("--allow-known-client-mismatch", action="store_true")
    args = parser.parse_args()
    # This utility is intentionally internal-only; external forwarding is out of scope.
    require(args.grpc_port in (9000, 9001), "Only internal verification ports are supported")
    require(args.client_source.is_dir(), "Restore the pinned ikm-python checkout first")
    sys.path.insert(0, str(args.client_source))
    from tinkar import TinkarClient, TinkarError

    def rest(path, **params):
        with urlopen(args.rest_base.rstrip("/") + "/" + path + "?" + urlencode(params),
                     timeout=30) as response:
            data = json.load(response)
        require(data.get("success"), f"REST {path}: {data}")
        return data

    mismatches = set()
    with grpc.insecure_channel(f"localhost:{args.grpc_port}") as channel, \
            TinkarClient(host="localhost", port=args.grpc_port, timeout=30) as client:
        grpc.channel_ready_future(channel).result(timeout=15)
        live = LiveSchema(channel)
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
            if actual != expected:
                require(len(actual) == len(expected) and all(not ids for ids, _ in actual)
                        and sorted(n for _, n in actual) == sorted(n for _, n in expected),
                        f"Unrecognized client search mismatch: {actual} vs {expected}")
                mismatches.add("Client search silently drops public IDs (uuid_bits unsupported)")
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
        if concept.public_id != list(fixture[0]):
            require(not concept.public_id, "Unexpected Python entity public IDs")
            mismatches.add("Client entity response silently drops public IDs")
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
        if not semantics.concept_public_id:
            require(all(not s.semantic_public_id for s in semantics.semantics),
                    "Unrecognized partial Python semantic ID mismatch")
            mismatches.add("Client semantics silently drops concept/semantic public IDs")
        else:
            require(semantics.concept_public_id == [concept_id] and
                    sorted(tuple(sorted(s.semantic_public_id)) for s in semantics.semantics)
                    == sorted(record[0] for record in rest_sem),
                    "Unexpected Python semantic public IDs")
        print(f"PASS semantics: {len(rest_sem)} UUID/pattern/field/stamp records match REST")
        for operation in ("inspect_concept", "get_entity_by_public_id",
                          "load_concept_entity_graph"):
            try:
                getattr(client.tinkar, operation)(concept_id)
            except TinkarError as error:
                require("Method not found" in str(error),
                        f"Unexpected legacy error: {error}")
                mismatches.add("Legacy client.tinkar RPCs return UNIMPLEMENTED (service removed)")
            else:
                require(SERVICE + "TinkarSearchService" in services,
                        "Legacy RPC succeeded but service not reflected")
    for mismatch in sorted(mismatches):
        print("CLIENT MISMATCH:", mismatch)
    print("Read-only transport/data parity: PASS")
    if mismatches:
        print("Python client compatibility: FAIL; no client stubs were patched")
        return 0 if args.allow_known_client_mismatch else 2
    print("Python client compatibility: PASS")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"FAIL: {type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
