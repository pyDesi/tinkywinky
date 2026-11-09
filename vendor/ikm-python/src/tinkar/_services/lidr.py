"""LIDR namespace — client.lidr.* (Tier 1: IkeGraphRAG)"""

from __future__ import annotations

import grpc

from .._generated import ike_types_pb2 as pb2
from .._wire import public_id, public_ids, stamp_from_proto
from .._generated import ike_graph_rag_pb2_grpc as rag_grpc
from ..exceptions import TinkarError
from ..models import Concept, ConceptListResponse, Stamp


class LidrNamespace:
    """Lab/diagnostics (LIDR) operations (Tier 1: IkeGraphRAG)."""

    def __init__(self, stub: rag_grpc.IkeGraphRAGStub, timeout: float):
        self._stub = stub
        self._timeout = timeout

    def records(
        self, test_kit_id: str, *, timeout: float | None = None
    ) -> ConceptListResponse:
        """Get LIDR record concepts from a test kit."""
        request = self._make_id_request(test_kit_id)
        response = self._call(
            self._stub.GetLIDRRecordConceptsFromTestKit, request, timeout
        )
        return self._to_concept_list(response)

    def result_conformances(
        self, lidr_record_id: str, *, timeout: float | None = None
    ) -> ConceptListResponse:
        """Get result conformance concepts from a LIDR record."""
        request = self._make_id_request(lidr_record_id)
        response = self._call(
            self._stub.GetResultConformanceConceptsFromLIDRRecord, request, timeout
        )
        return self._to_concept_list(response)

    def allowed_results(
        self, conformance_id: str, *, timeout: float | None = None
    ) -> ConceptListResponse:
        """Get allowed result concepts from a result conformance."""
        request = self._make_id_request(conformance_id)
        response = self._call(
            self._stub.GetAllowedResultConceptsFromResultConformance, request, timeout
        )
        return self._to_concept_list(response)

    # -- Private helpers --

    def _call(self, method, request, timeout: float | None):
        try:
            return method(request, timeout=timeout or self._timeout)
        except grpc.RpcError as e:
            raise TinkarError.from_grpc_error(e) from e

    def _make_id_request(self, concept_id: str) -> pb2.TinkarConceptIdRequest:
        return pb2.TinkarConceptIdRequest(public_id=public_id(concept_id))

    @staticmethod
    def _to_stamp(stamp) -> Stamp:
        return stamp_from_proto(stamp)

    def _to_concept_list(self, response) -> ConceptListResponse:
        if not response.success:
            raise TinkarError.from_response(response.error_message)
        return ConceptListResponse(
            created_at=response.created_at,
            total_count=response.total_count,
            concepts=[
                Concept(
                    public_id=public_ids(r.public_id),
                    fully_qualified_name=r.descriptions.fully_qualified_name,
                    regular_name=r.descriptions.regular_name,
                    definition=r.descriptions.definition,
                    stamp=self._to_stamp(r.stamp) if r.HasField("stamp") else None,
                )
                for r in response.results
            ],
            success=True,
        )
