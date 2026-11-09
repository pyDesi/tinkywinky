"""Search namespace — client.search.* (Tier 1: IkeGraphRAG)"""

from __future__ import annotations

import grpc

from .._generated import ike_types_pb2 as pb2
from .._wire import public_ids, stamp_from_proto
from .._generated import ike_graph_rag_pb2_grpc as rag_grpc
from ..exceptions import TinkarError
from ..models import (
    Concept,
    GroupedResult,
    GroupedSearchResponse,
    MatchingSemantic,
    RebuildIndexResponse,
    SearchResponse,
    SemanticResult,
    SemanticSearchResponse,
    Stamp,
)


class SearchNamespace:
    """Search operations (Tier 1: IkeGraphRAG)."""

    def __init__(self, stub: rag_grpc.IkeGraphRAGStub, timeout: float):
        self._stub = stub
        self._timeout = timeout

    def query(self, query: str, *, timeout: float | None = None) -> SearchResponse:
        """Basic text search for concepts."""
        request = pb2.TinkarSearchQueryRequest(query=query)
        response = self._call(self._stub.Search, request, timeout)
        return self._to_search_response(response, query)

    def concepts(
        self, query: str, *, max_results: int = 100, timeout: float | None = None
    ) -> SearchResponse:
        """Search for concepts with a result limit."""
        request = pb2.TinkarConceptSearchRequest(query=query, max_results=max_results)
        response = self._call(self._stub.ConceptSearch, request, timeout)
        return self._to_search_response(response, query)

    def concepts_by_component(
        self, query: str, *, max_results: int = 100, timeout: float | None = None
    ) -> GroupedSearchResponse:
        """Search concepts grouped by top-level component."""
        request = pb2.TinkarConceptSearchWithSortRequest(
            query=query,
            max_results=max_results,
            sort_by=pb2.SearchSortOption.TOP_COMPONENT,
        )
        response = self._call(self._stub.ConceptSearchWithSort, request, timeout)
        return self._to_grouped_response(response, query)

    def concepts_by_component_alpha(
        self, query: str, *, max_results: int = 100, timeout: float | None = None
    ) -> GroupedSearchResponse:
        """Search concepts grouped by top-level component, sorted alphabetically."""
        request = pb2.TinkarConceptSearchWithSortRequest(
            query=query,
            max_results=max_results,
            sort_by=pb2.SearchSortOption.TOP_COMPONENT_ALPHA,
        )
        response = self._call(self._stub.ConceptSearchWithSort, request, timeout)
        return self._to_grouped_response(response, query)

    def concepts_by_semantic(
        self, query: str, *, max_results: int = 100, timeout: float | None = None
    ) -> SemanticSearchResponse:
        """Search concepts as flat semantic matches, sorted by score."""
        request = pb2.TinkarConceptSearchWithSortRequest(
            query=query,
            max_results=max_results,
            sort_by=pb2.SearchSortOption.SEMANTIC,
        )
        response = self._call(self._stub.ConceptSearchWithSort, request, timeout)
        return self._to_semantic_response(response, query)

    def concepts_by_semantic_alpha(
        self, query: str, *, max_results: int = 100, timeout: float | None = None
    ) -> SemanticSearchResponse:
        """Search concepts as flat semantic matches, sorted alphabetically."""
        request = pb2.TinkarConceptSearchWithSortRequest(
            query=query,
            max_results=max_results,
            sort_by=pb2.SearchSortOption.SEMANTIC_ALPHA,
        )
        response = self._call(self._stub.ConceptSearchWithSort, request, timeout)
        return self._to_semantic_response(response, query)

    def rebuild_index(self, *, timeout: float | None = None) -> RebuildIndexResponse:
        """Trigger a rebuild of the Lucene search index."""
        request = pb2.TinkarRebuildIndexRequest()
        response = self._call(self._stub.RebuildSearchIndex, request, timeout)
        if not response.success:
            raise TinkarError.from_response(response.message)
        return RebuildIndexResponse(message=response.message, success=True)

    # -- Private helpers --

    def _call(self, method, request, timeout: float | None):
        try:
            return method(request, timeout=timeout or self._timeout)
        except grpc.RpcError as e:
            raise TinkarError.from_grpc_error(e) from e

    @staticmethod
    def _to_stamp(stamp) -> Stamp:
        """Convert a proto StampVersion to a Stamp model."""
        return stamp_from_proto(stamp)

    def _to_search_response(self, response, query: str) -> SearchResponse:
        if not response.success:
            raise TinkarError.from_response(response.error_message)
        return SearchResponse(
            created_at=response.created_at,
            query=query,
            total_count=response.total_count,
            results=[
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

    def _to_grouped_response(self, response, query: str) -> GroupedSearchResponse:
        if not response.success:
            raise TinkarError.from_response(response.error_message)
        return GroupedSearchResponse(
            created_at=response.created_at,
            query=query,
            total_count=response.total_count,
            results=[
                GroupedResult(
                    public_id=public_ids(r.public_id),
                    fully_qualified_name=r.fully_qualified_name,
                    is_active=r.active,
                    top_score=r.top_score,
                    preferred_name=r.preferred_name,
                    highlighted_name=r.highlighted_name,
                    matching_semantics=[
                        MatchingSemantic(
                            highlighted_text=m.highlighted_text,
                            plain_text=m.plain_text,
                            score=m.score,
                            field_index=m.field_index,
                            public_id=public_ids(m.public_id, required=False),
                        )
                        for m in r.matching_semantics
                    ],
                )
                for r in response.grouped_results
            ],
            success=True,
        )

    def _to_semantic_response(self, response, query: str) -> SemanticSearchResponse:
        if not response.success:
            raise TinkarError.from_response(response.error_message)
        return SemanticSearchResponse(
            created_at=response.created_at,
            query=query,
            total_count=response.total_count,
            results=[
                SemanticResult(
                    public_id=public_ids(r.public_id),
                    fully_qualified_name=r.fully_qualified_name,
                    regular_name=r.regular_name,
                    highlighted_text=r.highlighted_text,
                    score=r.score,
                    is_active=r.active,
                )
                for r in response.results
            ],
            success=True,
        )
