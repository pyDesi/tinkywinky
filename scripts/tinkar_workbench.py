#!/usr/bin/env python3
"""Bounded, read-only DeX demonstration using the tracked Python gRPC client."""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import grpc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor/ikm-python/src"))

# Positive allowlist protects the active store even if client internals change.
READ_ONLY = {
    "/dev.ikm.tinkar.service.IkeGraphRAG/ConceptSearch",
    "/dev.ikm.tinkar.service.IkeGraphRAG/GetLIDRRecordConceptsFromTestKit",
    "/dev.ikm.tinkar.service.IkeKnowledgeGraph/InspectConcept",
}
QUERIES = [
    ("Albumin Gen.2", "Albumin Gen.2"),
    ("Panther Fusion SARS Flu RSV", "Panther Fusion"),
    ("ARIES Flu RSV Assay", "ARIES"),
    ("Simplexa COVID-19 Flu", "Simplexa COVID-19"),
    ("Xpert Xpress Flu RSV", "Xpert"),
    ("Atellica IM Troponin", "Atellica IM"),
    ("i-STAT Troponin", "i-STAT"),
    ("Architect Hemoglobin A1c", "Architect"),
    ("VITROS HbA1c", "VITROS"),
    ("HER2 IQFISH", "HER2 IQFISH"),
    ("RealTime IDH1", "IDH1"),
    ("UniCel DxH", "UniCel DxH"),
]


class ReadOnlyInterceptor(grpc.UnaryUnaryClientInterceptor):
    def intercept_unary_unary(self, continuation, details, request):
        if details.method not in READ_ONLY:
            raise RuntimeError(f"Refusing non-read-only RPC: {details.method}")
        return continuation(details, request)


def rest_search(query):
    url = "http://localhost:80/tinkar/api/ike/graphrag/concept-search?"
    with urlopen(url + urlencode({"query": query, "maxResults": 10}), timeout=12) as response:
        data = json.load(response)
    if not data.get("success"):
        raise RuntimeError(data.get("errorMessage") or "REST search was unsuccessful")
    return data


def record_pairs(items, rest=False):
    if rest:
        return sorted((tuple(sorted(i["publicId"])), i["descriptions"]["fullyQualifiedName"])
                      for i in items)
    return sorted((tuple(sorted(i.public_id)), i.fully_qualified_name) for i in items)


def inspect_device(label, query, expected):
    result = dict(label=label, query=query, status="error", message="",
                  publicIds=[], name="", semanticCount=0, stampCount=0,
                  lidrCount=0, lidrMessage="Not checked", semanticJson="{}",
                  searchJson="{}", restJson="{}", parity="not_checked", patterns=[])
    channel = grpc.intercept_channel(grpc.insecure_channel("localhost:9000"),
                                    ReadOnlyInterceptor())
    # Use the vendored client's namespaces with a safety-wrapped channel.
    from tinkar._generated import ike_graph_rag_pb2_grpc as rag
    from tinkar._generated import ike_knowledge_graph_pb2_grpc as kg
    from tinkar._services import SearchNamespace, KnowledgeGraphNamespace, LidrNamespace
    search = SearchNamespace(rag.IkeGraphRAGStub(channel), 12)
    knowledge = KnowledgeGraphNamespace(kg.IkeKnowledgeGraphStub(channel), 12)
    lidr = LidrNamespace(rag.IkeGraphRAGStub(channel), 12)
    try:
        response = search.concepts(query, max_results=10)
        if not response.success:
            raise RuntimeError(response.error_message or "gRPC search unsuccessful")
        result["searchJson"] = response.model_dump_json(indent=2)
        try:
            rest = rest_search(query)
            result["restJson"] = json.dumps(rest, indent=2)
            result["parity"] = ("match" if record_pairs(response.results) ==
                                record_pairs(rest.get("results", []), rest=True)
                                else "mismatch")
        except Exception as exc:
            result["parity"] = "unavailable"
            result["restJson"] = json.dumps({"error": str(exc)})
        matches = [r for r in response.results
                   if expected.casefold() in r.fully_qualified_name.casefold()]
        if not matches:
            result.update(status="missing", message=(
                "No matching fixture in the public GUDID subset. "
                "No substitute device was selected."))
            return result
        concept = matches[0]
        result.update(publicIds=concept.public_id, name=concept.fully_qualified_name)
        semantics = knowledge.semantics(concept.public_id[0])
        if not semantics.success:
            raise RuntimeError(semantics.error_message or "Semantics unsuccessful")
        result.update(semanticCount=semantics.total_count,
                      semanticJson=semantics.model_dump_json(indent=2),
                      patterns=sorted({s.pattern_name for s in semantics.semantics}),
                      stampCount=sum(s.stamp is not None for s in semantics.semantics))
        try:
            records = lidr.records(concept.public_id[0])
            if not records.success:
                raise RuntimeError(records.error_message or "LIDR unsuccessful")
            result.update(lidrCount=records.total_count, lidrMessage=(
                f"{records.total_count} LIDR records returned" if records.total_count
                else "No LIDR records returned by this dataset"))
        except Exception as exc:
            result["lidrMessage"] = f"LIDR unavailable: {exc}"
        result.update(status="found", message=(
            f"Selected the first of {len(matches)} matching search candidates. "
            "Review the returned name to confirm the product variant."))
    except Exception as exc:
        result.update(status="error", message=str(exc))
    finally:
        channel.close()
    return result


def run(scenario_id):
    started = time.monotonic()
    scenarios = json.loads((ROOT / "scripts/tinkar-scenarios.json").read_text())
    scenario = scenarios[scenario_id - 1]
    indices = [0] if scenario_id == 1 else list(range(1, 5)) if scenario_id == 2 else list(range(12))
    # The service's search context can mix queries under concurrent requests.
    # Serialize devices and transports so the comparison has consistent inputs.
    devices = [inspect_device(label, *QUERIES[index])
               for label, index in zip(scenario["devices"], indices)]
    counts = {status: sum(d["status"] == status for d in devices)
              for status in ("found", "missing", "error")}
    return dict(
        scenarioId=scenario_id, executedAt=datetime.now(timezone.utc).isoformat(),
        durationMs=round((time.monotonic() - started) * 1000),
        found=counts["found"], missing=counts["missing"], errors=counts["error"],
        devices=devices,
        logs=["Read-only allowlist enabled. No dataset mutations performed."] + [
            f"{d['label']}: {d['status']}; REST/gRPC parity: {d['parity']}; "
            f"{d['semanticCount']} semantics; {d['stampCount']} stamps. {d['message']}"
            for d in devices],
        limitations=[
            "These are the three upstream DeX retrieval scenarios, not a claim that the full upstream test suite passes.",
            "Public GUDID is a subset: fixtures, LIDR patterns and full clinical DeX data may be absent.",
            "Sensitivity, limit of detection, reference ranges, specimen types and units are not inferred. This tool does not rank clinical performance.",
            "Search selects the first name-matching candidate, not a verified exact product variant; inspect the returned name and raw candidates.",
            "Optional pattern identifiers omitted by the source remain null. Required record identifiers are never fabricated.",
            "REST/gRPC parity checks the returned search UUIDs and names, not full semantic equivalence.",
        ],
    )


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"1", "2", "3"}:
        sys.exit("Expected scenario 1, 2, or 3")
    print(json.dumps(run(int(sys.argv[1]))))
