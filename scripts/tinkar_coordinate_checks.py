"""Write-capable checks: hard-wired to the disposable runner, NEVER the smoke suite."""
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import grpc
from google.protobuf import descriptor_pool, json_format, message_factory
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import (
    ProtoReflectionDescriptorDatabase,
)

from tinkar_smoke import public_ids, require

BASE = "http://127.0.0.1:8100/tinkar/api/ike/"
PREFIX = "dev.ikm.tinkar.service."
CAPABILITY = "COORDINATE_REGISTRY_UNAVAILABLE"


def owned_store():
    root = Path(os.environ["TINKAR_COORDINATE_DISPOSABLE"]).resolve(strict=True)
    expected = Path(__file__).resolve().parents[1] / ".local/tinkar-verification"
    require(root.parent == expected and root.name.startswith("run-"), "Not a disposable store")
    require((root / "DISPOSABLE").read_text() == "fresh-public-gudid\n", "Missing ownership marker")
    pid = int(os.environ["TINKAR_COORDINATE_PID"])
    require(Path(f"/proc/{pid}/cwd").resolve() == root, "Not the disposable process")
    cmd = Path(f"/proc/{pid}/cmdline").read_bytes()
    require(b"--grpc.server.port=9001" in cmd and b"--server.port=8100" in cmd,
            "Wrong process ports")
    return root


def http(endpoint, payload=None, **params):
    owned_store()
    url = BASE + endpoint + ("?" + urlencode(params, doseq=True) if params else "")
    req = Request(url, data=None if payload is None else json.dumps(payload).encode(),
                  headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=30) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


class DisposableRPC:
    """Independent schema client; deliberately does NOT extend the smoke allowlist."""
    def __init__(self, channel):
        self.channel = channel
        self.pool = descriptor_pool.DescriptorPool(ProtoReflectionDescriptorDatabase(channel))

    def call(self, method, payload):
        owned_store()
        service, rpc = method.split("/")
        descriptor = self.pool.FindServiceByName(PREFIX + service).methods_by_name[rpc]
        request_type = message_factory.GetMessageClass(descriptor.input_type)
        response_type = message_factory.GetMessageClass(descriptor.output_type)
        request = json_format.ParseDict(payload, request_type())
        response = self.channel.unary_unary(
            "/" + PREFIX + method,
            request_serializer=request_type.SerializeToString,
            response_deserializer=response_type.FromString,
        )(request, timeout=30)
        return json_format.MessageToDict(response, preserving_proto_field_name=True)


def semantic_ids(value, transport):
    require(value.get("success"), f"{transport} failed: {value}")
    if transport == "REST":
        return {semantic["semanticId"] for semantic in value.get("semantics", [])}
    return {public_ids(semantic["semantic_public_id"])[0]
            for semantic in value.get("semantics", [])}


def main():
    root = owned_store()
    with grpc.insecure_channel("127.0.0.1:9001") as channel:
        rpc = DisposableRPC(channel)
        status, search = http("graphrag/concept-search", query="device", maxResults=1)
        require(status == 200 and search.get("success") and search.get("results"),
                "Public dataset has no device fixture")
        concept_id = search["results"][0]["publicId"][0]
        (root / "concept-id").write_text(concept_id)
        print("Verified public fixture:", concept_id,
              search["results"][0]["descriptions"]["fullyQualifiedName"])

        for kind, settings in (
            ("stamp", {"allowedStates": "ACTIVE"}),
            ("navigation", {"premiseType": "INFERRED"}),
            ("language", {"languagePreset": "US_ENGLISH_REGULAR_NAME"}),
        ):
            endpoint = "knowledgegraph/coordinates/" + kind
            for payload in (None, settings):
                status, body = http(endpoint, payload)
                require(status == 412 and body.get("code") == CAPABILITY,
                        f"Unexpected REST capability response: {status} {body}")
            name = kind.capitalize()
            for verb, request in (("List", {}), ("Save", {"settings": {}})):
                method = f"IkeKnowledgeGraph/{verb}{name}Coordinate" + ("s" if verb == "List" else "")
                try:
                    rpc.call(method, request)
                except grpc.RpcError as error:
                    require(error.code() == grpc.StatusCode.FAILED_PRECONDITION
                            and error.details().startswith(CAPABILITY + ":"),
                            f"Unexpected gRPC capability response: {error}")
                else:
                    raise AssertionError(f"{method} unexpectedly succeeded on unprovisioned public subset")
            print(f"PASS {kind}: REST 412 and gRPC FAILED_PRECONDITION for save AND list")

        # IDs, not counts: require meaningful nonempty baseline and exact parity.
        base_payload = {"public_id": {"uuids": [concept_id]}}
        status, baseline = http("knowledgegraph/semantics", conceptId=concept_id)
        baseline_ids = semantic_ids(baseline, "REST")
        require(status == 200 and baseline_ids, "Empty semantics fixture")
        remote = rpc.call("IkeKnowledgeGraph/InspectConcept", base_payload)
        require(semantic_ids(remote, "gRPC") == baseline_ids, "Baseline semantic IDs differ")
        for query, override in (
            ({"allowedStates": "ACTIVE"}, {"allowed_states": "ACTIVE"}),
            ({"allowedStates": "INACTIVE"}, {"allowed_states": "INACTIVE"}),
            ({"positionTime": 1}, {"position_time": "1"}),
        ):
            status, filtered = http("knowledgegraph/semantics", conceptId=concept_id, **query)
            actual = semantic_ids(filtered, "REST")
            remote = rpc.call("IkeKnowledgeGraph/InspectConcept",
                              dict(base_payload, coordinate_override=override))
            require(status == 200 and actual == semantic_ids(remote, "gRPC"),
                    f"Filtered semantic IDs differ: {query}")
            require(actual <= baseline_ids, "Filtering introduced unexpected semantics")
            if query.get("allowedStates") == "ACTIVE":
                require(actual, "ACTIVE removed all known active device semantics")
                require(all(s["stamp"]["status"].lower() == "active"
                            for s in filtered["semantics"]), "ACTIVE returned inactive semantics")
            else:
                require(not actual, f"Expected empty inactive/prehistory subset, got {actual}")
            print(f"PASS filtering {query}: {len(actual)} exact semantic IDs agree")
        entity = rpc.call("IkeGraphRAG/GetEntity", base_payload)
        module_ids = public_ids(entity["results"][0]["stamp"]["module_public_id"])
        require(module_ids, "Fixture concept lacks an identifiable module")
        module_id = module_ids[0]
        module_sets = []
        for parameter, wire in (("modules", "module_ids"),
                                ("excludedModules", "excluded_module_ids")):
            status, filtered = http("knowledgegraph/semantics", conceptId=concept_id,
                                    **{parameter: module_id})
            actual = semantic_ids(filtered, "REST")
            remote = rpc.call("IkeKnowledgeGraph/InspectConcept", dict(
                base_payload, coordinate_override={wire: [{"uuids": [module_id]}]}))
            require(status == 200 and actual == semantic_ids(remote, "gRPC"),
                    f"Module filtering differs: {parameter}")
            module_sets.append(actual)
        included, excluded = module_sets
        require(included and not (included & excluded) and included | excluded == baseline_ids,
                "Include/exclude must form an exact, nontrivial partition of baseline semantic IDs")
        print(f"PASS module include/exclude {module_id}: disjoint partition "
              f"{len(included)} + {len(excluded)} = {len(baseline_ids)} semantic IDs")
        # Explicit optional fixture discovery: missing restricted terminology is a skip,
        # not a broken public-device example or a reason to download restricted data.
        for fixture in ("f6978e15-e169-58c2-a93d-eac1511974da",
                        "2716e9c0-b454-5973-8d2e-4c068897b244"):
            status, response = http("graphrag/entity", conceptId=fixture)
            require(status == 200 and not response.get("success"),
                    f"Optional fixture behavior changed: {fixture}: {status} {response}")
            require("No component in this knowledge base has the public id" in response.get("errorMessage", ""),
                    "Unexpected optional-fixture failure")
            print("SKIP unsupported SNOMED fixture absent from public GUDID:", fixture)


if __name__ == "__main__":
    main()
