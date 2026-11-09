"""Tinkar gRPC client."""

from __future__ import annotations

import grpc

from ._generated import ike_admin_pb2_grpc as admin_grpc
from ._generated import ike_graph_rag_pb2_grpc as rag_grpc
from ._generated import ike_knowledge_graph_pb2_grpc as kg_grpc
from ._services import (
    AdminNamespace,
    EntityNamespace,
    KnowledgeGraphNamespace,
    LidrNamespace,
    SearchNamespace,
    TinkarSearchNamespace,
)


class TinkarClient:
    """Client for the Tinkar gRPC terminology service.

    Exposes three service tiers as namespaced properties:

    - **Tier 1** (``search``, ``entities``, ``lidr``): Simple, opinionated API
      via the IkeGraphRAG service.
    - **Tier 2** (``knowledge_graph``): Concept-aware API with coordinate
      overrides via the IkeKnowledgeGraph service.
    - **Tier 3** (``admin``): Import, export, and reasoner operations
      via the IkeAdmin service.

    Example::

        with TinkarClient() as client:
            # Tier 1: search
            response = client.search.query("diabetes")
            for entity in response.results:
                print(entity.fully_qualified_name)

            # Tier 2: knowledge graph
            sem = client.knowledge_graph.semantics("concept-uuid")

            # Tier 3: admin
            result = client.admin.run_reasoner()
    """

    def __init__(
        self, host: str = "localhost", port: int = 9095, timeout: float = 30.0
    ):
        self._address = f"{host}:{port}"
        self._timeout = timeout
        self._channel: grpc.Channel | None = None

        # Tier 1: IkeGraphRAG
        self._search: SearchNamespace | None = None
        self._entities: EntityNamespace | None = None
        self._lidr: LidrNamespace | None = None
        # Tier 2: IkeKnowledgeGraph
        self._knowledge_graph: KnowledgeGraphNamespace | None = None
        # Tier 3: IkeAdmin
        self._admin: AdminNamespace | None = None
        # TinkarSearchService (raw 1:1 wrapper, including entity-graph RPCs)
        self._tinkar: TinkarSearchNamespace | None = None

    def connect(self) -> None:
        """Establish connection to the gRPC server."""
        self._channel = grpc.insecure_channel(self._address)

        # Tier 1
        rag_stub = rag_grpc.IkeGraphRAGStub(self._channel)
        self._search = SearchNamespace(rag_stub, self._timeout)
        self._entities = EntityNamespace(rag_stub, self._timeout)
        self._lidr = LidrNamespace(rag_stub, self._timeout)

        # Tier 2
        kg_stub = kg_grpc.IkeKnowledgeGraphStub(self._channel)
        self._knowledge_graph = KnowledgeGraphNamespace(kg_stub, self._timeout)

        # Tier 3
        admin_stub = admin_grpc.IkeAdminStub(self._channel)
        self._admin = AdminNamespace(admin_stub, self._timeout)

        # Compatibility methods route to the registered tiered services.
        self._tinkar = TinkarSearchNamespace(rag_stub, self._timeout, kg_stub)

    def close(self) -> None:
        """Close the connection."""
        if self._channel:
            self._channel.close()
            self._channel = None
            self._search = None
            self._entities = None
            self._lidr = None
            self._knowledge_graph = None
            self._admin = None
            self._tinkar = None

    def __enter__(self) -> TinkarClient:
        self.connect()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _ensure_connected(self) -> None:
        if self._channel is None:
            self.connect()

    @property
    def search(self) -> SearchNamespace:
        """Tier 1: Search operations."""
        self._ensure_connected()
        assert self._search is not None
        return self._search

    @property
    def entities(self) -> EntityNamespace:
        """Tier 1: Entity lookup operations."""
        self._ensure_connected()
        assert self._entities is not None
        return self._entities

    @property
    def lidr(self) -> LidrNamespace:
        """Tier 1: LIDR (lab/diagnostics) operations."""
        self._ensure_connected()
        assert self._lidr is not None
        return self._lidr

    @property
    def knowledge_graph(self) -> KnowledgeGraphNamespace:
        """Tier 2: Concept-aware operations with coordinate support."""
        self._ensure_connected()
        assert self._knowledge_graph is not None
        return self._knowledge_graph

    @property
    def admin(self) -> AdminNamespace:
        """Tier 3: Administrative operations (import, export, reasoner)."""
        self._ensure_connected()
        assert self._admin is not None
        return self._admin

    @property
    def tinkar(self) -> TinkarSearchNamespace:
        """Compatibility facade over the tiered services. Use for the entity-graph
        RPCs (load_concept_entity_graph, get_entity_by_public_id) and
        inspect_concept; the search/hierarchy/LIDR operations here overlap
        functionally with .search/.entities/.lidr (which target IkeGraphRAG)."""
        self._ensure_connected()
        assert self._tinkar is not None
        return self._tinkar
