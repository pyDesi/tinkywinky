"""Entities namespace — client.entities.* (Tier 1: IkeGraphRAG)"""

from __future__ import annotations

import grpc

from .._generated import ike_types_pb2 as pb2
from .._wire import public_id, public_ids, stamp_from_proto
from .._generated import ike_graph_rag_pb2_grpc as rag_grpc
from ..exceptions import TinkarError
from ..models import Concept, ConceptListResponse, ConceptResponse, Stamp


class EntityNamespace:
    """Concept operations (Tier 1: IkeGraphRAG)."""

    def __init__(self, stub: rag_grpc.IkeGraphRAGStub, timeout: float):
        self._stub = stub
        self._timeout = timeout

    def get(self, concept_id: str, *, timeout: float | None = None) -> ConceptResponse:
        """Get a single entity by UUID."""
        request = self._make_id_request(concept_id)
        response = self._call(self._stub.GetEntity, request, timeout)
        if not response.success:
            raise TinkarError.from_response(response.error_message)
        if not response.results:
            raise TinkarError(message=f"Concept not found: {concept_id}", code="not_found")
        r = response.results[0]
        return ConceptResponse(
            created_at=response.created_at,
            concept=Concept(
                public_id=public_ids(r.public_id),
                fully_qualified_name=r.descriptions.fully_qualified_name,
                regular_name=r.descriptions.regular_name,
                definition=r.descriptions.definition,
                stamp=self._to_stamp(r.stamp) if r.HasField("stamp") else None,
            ),
            success=True,
        )

    def children(
        self, concept_id: str, *, timeout: float | None = None
    ) -> ConceptListResponse:
        """Get direct children of a concept."""
        request = self._make_id_request(concept_id)
        response = self._call(self._stub.GetChildConcepts, request, timeout)
        return self._to_concept_list(response)

    def descendants(
        self, concept_id: str, *, timeout: float | None = None
    ) -> ConceptListResponse:
        """Get all descendants of a concept."""
        request = self._make_id_request(concept_id)
        response = self._call(self._stub.GetDescendantConcepts, request, timeout)
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
