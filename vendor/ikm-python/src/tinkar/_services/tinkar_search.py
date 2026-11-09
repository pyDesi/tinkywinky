"""Compatibility facade for the removed TinkarSearchService.

Keep the public method names, but send every call to its current tiered service.
No RPC is ever sent to the removed service.
"""
import grpc

from .._generated import ike_types_pb2 as pb2
from .._generated import ike_knowledge_graph_pb2 as kg_pb2
from .._wire import public_id
from ..exceptions import TinkarError
from ..models import TinkarConceptEntityResponse
from .search import SearchNamespace
from .entities import EntityNamespace
from .lidr import LidrNamespace
from .knowledge_graph import KnowledgeGraphNamespace


class TinkarSearchNamespace:
    def __init__(self, stub, timeout, kg_stub):
        self._search = SearchNamespace(stub, timeout)
        self._entities = EntityNamespace(stub, timeout)
        self._lidr = LidrNamespace(stub, timeout)
        self._kg = KnowledgeGraphNamespace(kg_stub, timeout)
        self._kg_stub = kg_stub
        self._timeout = timeout

    def search(self, query, *, timeout=None):
        return self._search.query(query, timeout=timeout)

    def concept_search(self, query, *, max_results=100, timeout=None):
        return self._search.concepts(query, max_results=max_results, timeout=timeout)

    def concept_search_with_sort(self, query, *, sort_by=pb2.TOP_COMPONENT,
                                 max_results=100, timeout=None):
        operations = {
            pb2.TOP_COMPONENT: self._search.concepts_by_component,
            pb2.TOP_COMPONENT_ALPHA: self._search.concepts_by_component_alpha,
            pb2.SEMANTIC: self._search.concepts_by_semantic,
            pb2.SEMANTIC_ALPHA: self._search.concepts_by_semantic_alpha,
        }
        if sort_by not in operations:
            raise TinkarError(f"Unsupported search sort: {sort_by}", "invalid_argument")
        return operations[sort_by](query, max_results=max_results, timeout=timeout)

    def get_entity(self, public_id, *, timeout=None):
        return self._entities.get(public_id, timeout=timeout)

    def get_child_concepts(self, public_id, *, timeout=None):
        return self._entities.children(public_id, timeout=timeout)

    def get_descendant_concepts(self, public_id, *, timeout=None):
        return self._entities.descendants(public_id, timeout=timeout)

    def get_lidr_record_concepts_from_test_kit(self, test_kit_id, *, timeout=None):
        return self._lidr.records(test_kit_id, timeout=timeout)

    def get_result_conformance_concepts_from_lidr_record(self, lidr_record_id, *, timeout=None):
        return self._lidr.result_conformances(lidr_record_id, timeout=timeout)

    def get_allowed_result_concepts_from_result_conformance(self, conformance_id, *, timeout=None):
        return self._lidr.allowed_results(conformance_id, timeout=timeout)

    def rebuild_search_index(self, *, timeout=None):
        return self._search.rebuild_index(timeout=timeout)

    def inspect_concept(self, public_id, *, timeout=None):
        return self._kg.semantics(public_id, timeout=timeout)

    def load_concept_entity_graph(self, public_id, *, timeout=None):
        return self._entity_call(self._kg_stub.LoadConceptEntityGraph, public_id, timeout)

    def get_entity_by_public_id(self, public_id, *, timeout=None):
        return self._entity_call(self._kg_stub.GetEntityByPublicId, public_id, timeout)

    def _entity_call(self, method, identifier, timeout):
        request = kg_pb2.KnowledgeGraphConceptRequest(public_id=public_id(identifier))
        try:
            response = method(request, timeout=self._timeout if timeout is None else timeout)
        except grpc.RpcError as error:
            raise TinkarError.from_grpc_error(error) from error
        if not response.success:
            raise TinkarError.from_response(response.error_message)
        if not response.entities:
            raise TinkarError(f"Entity not found: {identifier}", "not_found")
        return TinkarConceptEntityResponse(
            entities=[entity.SerializeToString() for entity in response.entities],
            success=True,
        )
