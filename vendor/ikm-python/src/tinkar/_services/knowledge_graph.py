"""Knowledge Graph namespace — client.knowledge_graph.* (Tier 2: IkeKnowledgeGraph)"""

from __future__ import annotations

import grpc

from .._wire import public_id, public_ids, stamp_from_proto
from .._generated import ike_knowledge_graph_pb2 as kg_pb2
from .._generated import ike_knowledge_graph_pb2_grpc as kg_grpc
from ..exceptions import TinkarError
from ..models import (
    AllowedStates,
    ConceptSemanticInfo,
    ConceptSemanticsResponse,
    CoordinateListResponse,
    CoordinateOverride,
    Concept,
    ConceptListResponse,
    FieldValue,
    LanguageCoordinateEntry,
    LanguagePreset,
    NavigationCoordinateEntry,
    PremiseType,
    SavedCoordinateResponse,
    StampCoordinateEntry,
    Stamp,
)


class KnowledgeGraphNamespace:
    """Concept-aware operations with coordinate support (Tier 2: IkeKnowledgeGraph)."""

    def __init__(self, stub: kg_grpc.IkeKnowledgeGraphStub, timeout: float):
        self._stub = stub
        self._timeout = timeout

    # -- Concept queries --

    def semantics(
        self,
        concept_id: str,
        *,
        coordinate_override: CoordinateOverride | None = None,
        timeout: float | None = None,
    ) -> ConceptSemanticsResponse:
        """Get all semantics attached to a concept."""
        request = self._make_kg_request(concept_id, coordinate_override)
        response = self._call(self._stub.InspectConcept, request, timeout)
        return self._to_semantics_response(response)

    def children(
        self,
        concept_id: str,
        *,
        coordinate_override: CoordinateOverride | None = None,
        timeout: float | None = None,
    ) -> ConceptListResponse:
        """Get direct children with coordinate-aware navigation."""
        request = self._make_kg_request(concept_id, coordinate_override)
        response = self._call(self._stub.GetChildConcepts, request, timeout)
        return self._to_concept_list(response)

    def descendants(
        self,
        concept_id: str,
        *,
        coordinate_override: CoordinateOverride | None = None,
        timeout: float | None = None,
    ) -> ConceptListResponse:
        """Get all descendants with coordinate-aware navigation."""
        request = self._make_kg_request(concept_id, coordinate_override)
        response = self._call(self._stub.GetDescendantConcepts, request, timeout)
        return self._to_concept_list(response)

    def semantics_with_coordinate(
        self,
        concept_id: str,
        *,
        stamp_coordinate_id: str = "",
        navigation_coordinate_id: str = "",
        language_coordinate_id: str = "",
        timeout: float | None = None,
    ) -> ConceptSemanticsResponse:
        """Get semantics using previously saved coordinate IDs."""
        request = kg_pb2.SemanticsWithCoordinateRequest(
            concept_public_id=public_id(concept_id),
            stamp_coordinate_id=public_id(stamp_coordinate_id) if stamp_coordinate_id else None,
            navigation_coordinate_id=public_id(navigation_coordinate_id) if navigation_coordinate_id else None,
            language_coordinate_id=public_id(language_coordinate_id) if language_coordinate_id else None,
        )
        response = self._call(self._stub.GetSemanticsWithCoordinate, request, timeout)
        return self._to_semantics_response(response)

    # -- Coordinate management --

    def save_stamp_coordinate(
        self,
        *,
        allowed_states: AllowedStates = AllowedStates.ACTIVE_AND_INACTIVE,
        position_time: int = 0,
        position_path_id: str = "",
        module_ids: list[str] | None = None,
        excluded_module_ids: list[str] | None = None,
        module_priority_ids: list[str] | None = None,
        timeout: float | None = None,
    ) -> SavedCoordinateResponse:
        """Save a StampCoordinate (idempotent)."""
        grpc_states = {
            AllowedStates.ACTIVE_AND_INACTIVE: kg_pb2.AllowedStates.ACTIVE_AND_INACTIVE,
            AllowedStates.ACTIVE: kg_pb2.AllowedStates.ACTIVE,
            AllowedStates.INACTIVE: kg_pb2.AllowedStates.INACTIVE,
        }
        settings = kg_pb2.StampCoordinateSettings(
            allowed_states=grpc_states[allowed_states],
            position_time=position_time,
            position_path_id=public_id(position_path_id) if position_path_id else None,
            module_ids=[public_id(v) for v in module_ids or []],
            excluded_module_ids=[public_id(v) for v in excluded_module_ids or []],
            module_priority_ids=[public_id(v) for v in module_priority_ids or []],
        )
        request = kg_pb2.SaveStampCoordinateRequest(settings=settings)
        response = self._call(self._stub.SaveStampCoordinate, request, timeout)
        return self._saved_coordinate(response)

    def list_stamp_coordinates(
        self, *, timeout: float | None = None
    ) -> CoordinateListResponse:
        """List all saved StampCoordinates."""
        request = kg_pb2.ListStampCoordinatesRequest()
        response = self._call(self._stub.ListStampCoordinates, request, timeout)
        return CoordinateListResponse(
            stamps=[
                StampCoordinateEntry(
                    **self._coordinate_fields(c),
                    allowed_states=kg_pb2.AllowedStates.Name(c.settings.allowed_states),
                    position_time=c.settings.position_time,
                    position_path_id=",".join(public_ids(c.settings.position_path_id, required=False)),
                    module_ids=[identifier for v in c.settings.module_ids for identifier in public_ids(v)],
                    excluded_module_ids=[identifier for v in c.settings.excluded_module_ids for identifier in public_ids(v)],
                    module_priority_ids=[identifier for v in c.settings.module_priority_ids for identifier in public_ids(v)],
                )
                for c in response.coordinates
            ],
            success=True,
        )

    def save_navigation_coordinate(
        self,
        *,
        premise_type: PremiseType = PremiseType.INFERRED,
        timeout: float | None = None,
    ) -> SavedCoordinateResponse:
        """Save a NavigationCoordinate (idempotent)."""
        grpc_premise = {
            PremiseType.INFERRED: kg_pb2.ProtoPremiseType.INFERRED,
            PremiseType.STATED: kg_pb2.ProtoPremiseType.STATED,
        }
        settings = kg_pb2.NavigationCoordinateSettings(
            premise_type=grpc_premise[premise_type]
        )
        request = kg_pb2.SaveNavigationCoordinateRequest(settings=settings)
        response = self._call(self._stub.SaveNavigationCoordinate, request, timeout)
        return self._saved_coordinate(response)

    def list_navigation_coordinates(
        self, *, timeout: float | None = None
    ) -> CoordinateListResponse:
        """List all saved NavigationCoordinates."""
        request = kg_pb2.ListNavigationCoordinatesRequest()
        response = self._call(self._stub.ListNavigationCoordinates, request, timeout)
        return CoordinateListResponse(
            navigations=[
                NavigationCoordinateEntry(
                    **self._coordinate_fields(c),
                    premise_type=kg_pb2.ProtoPremiseType.Name(c.settings.premise_type),
                )
                for c in response.coordinates
            ],
            success=True,
        )

    def save_language_coordinate(
        self,
        *,
        language_preset: LanguagePreset = LanguagePreset.US_ENGLISH_REGULAR_NAME,
        timeout: float | None = None,
    ) -> SavedCoordinateResponse:
        """Save a LanguageCoordinate (idempotent)."""
        grpc_preset = {
            LanguagePreset.US_ENGLISH_REGULAR_NAME: kg_pb2.ProtoLanguagePreset.US_ENGLISH_REGULAR_NAME,
            LanguagePreset.US_ENGLISH_FULLY_QUALIFIED_NAME: kg_pb2.ProtoLanguagePreset.US_ENGLISH_FULLY_QUALIFIED_NAME,
            LanguagePreset.GB_ENGLISH_PREFERRED_NAME: kg_pb2.ProtoLanguagePreset.GB_ENGLISH_PREFERRED_NAME,
            LanguagePreset.GB_ENGLISH_FULLY_QUALIFIED_NAME: kg_pb2.ProtoLanguagePreset.GB_ENGLISH_FULLY_QUALIFIED_NAME,
            LanguagePreset.ANY_LANGUAGE_REGULAR_NAME: kg_pb2.ProtoLanguagePreset.ANY_LANGUAGE_REGULAR_NAME,
            LanguagePreset.ANY_LANGUAGE_FULLY_QUALIFIED_NAME: kg_pb2.ProtoLanguagePreset.ANY_LANGUAGE_FULLY_QUALIFIED_NAME,
            LanguagePreset.ANY_LANGUAGE_DEFINITION: kg_pb2.ProtoLanguagePreset.ANY_LANGUAGE_DEFINITION,
            LanguagePreset.SPANISH_PREFERRED_NAME: kg_pb2.ProtoLanguagePreset.SPANISH_PREFERRED_NAME,
            LanguagePreset.SPANISH_FULLY_QUALIFIED_NAME: kg_pb2.ProtoLanguagePreset.SPANISH_FULLY_QUALIFIED_NAME,
        }
        settings = kg_pb2.LanguageCoordinateSettings(
            language_preset=grpc_preset[language_preset]
        )
        request = kg_pb2.SaveLanguageCoordinateRequest(settings=settings)
        response = self._call(self._stub.SaveLanguageCoordinate, request, timeout)
        return self._saved_coordinate(response)

    def list_language_coordinates(
        self, *, timeout: float | None = None
    ) -> CoordinateListResponse:
        """List all saved LanguageCoordinates."""
        request = kg_pb2.ListLanguageCoordinatesRequest()
        response = self._call(self._stub.ListLanguageCoordinates, request, timeout)
        return CoordinateListResponse(
            languages=[
                LanguageCoordinateEntry(
                    **self._coordinate_fields(c),
                    language_preset=kg_pb2.ProtoLanguagePreset.Name(c.settings.language_preset),
                )
                for c in response.coordinates
            ],
            success=True,
        )

    # -- Private helpers --

    @staticmethod
    def _coordinate_fields(response):
        identifiers = public_ids(response.id)
        return dict(id=identifiers[0], public_id=identifiers, created_at=response.created_at)

    def _saved_coordinate(self, response):
        return SavedCoordinateResponse(
            **self._coordinate_fields(response), success=True,
        )

    def _call(self, method, request, timeout: float | None):
        try:
            return method(request, timeout=timeout or self._timeout)
        except grpc.RpcError as e:
            raise TinkarError.from_grpc_error(e) from e

    def _make_kg_request(
        self, concept_id: str, override: CoordinateOverride | None
    ) -> kg_pb2.KnowledgeGraphConceptRequest:
        concept_public_id = public_id(concept_id)
        coord = None
        if override is not None:
            grpc_states = {
                AllowedStates.ACTIVE_AND_INACTIVE: kg_pb2.AllowedStates.ACTIVE_AND_INACTIVE,
                AllowedStates.ACTIVE: kg_pb2.AllowedStates.ACTIVE,
                AllowedStates.INACTIVE: kg_pb2.AllowedStates.INACTIVE,
            }
            grpc_premise = {
                PremiseType.INFERRED: kg_pb2.ProtoPremiseType.INFERRED,
                PremiseType.STATED: kg_pb2.ProtoPremiseType.STATED,
            }
            grpc_lang = {
                LanguagePreset.US_ENGLISH_REGULAR_NAME: kg_pb2.ProtoLanguagePreset.US_ENGLISH_REGULAR_NAME,
                LanguagePreset.US_ENGLISH_FULLY_QUALIFIED_NAME: kg_pb2.ProtoLanguagePreset.US_ENGLISH_FULLY_QUALIFIED_NAME,
                LanguagePreset.GB_ENGLISH_PREFERRED_NAME: kg_pb2.ProtoLanguagePreset.GB_ENGLISH_PREFERRED_NAME,
                LanguagePreset.GB_ENGLISH_FULLY_QUALIFIED_NAME: kg_pb2.ProtoLanguagePreset.GB_ENGLISH_FULLY_QUALIFIED_NAME,
                LanguagePreset.ANY_LANGUAGE_REGULAR_NAME: kg_pb2.ProtoLanguagePreset.ANY_LANGUAGE_REGULAR_NAME,
                LanguagePreset.ANY_LANGUAGE_FULLY_QUALIFIED_NAME: kg_pb2.ProtoLanguagePreset.ANY_LANGUAGE_FULLY_QUALIFIED_NAME,
                LanguagePreset.ANY_LANGUAGE_DEFINITION: kg_pb2.ProtoLanguagePreset.ANY_LANGUAGE_DEFINITION,
                LanguagePreset.SPANISH_PREFERRED_NAME: kg_pb2.ProtoLanguagePreset.SPANISH_PREFERRED_NAME,
                LanguagePreset.SPANISH_FULLY_QUALIFIED_NAME: kg_pb2.ProtoLanguagePreset.SPANISH_FULLY_QUALIFIED_NAME,
            }
            coord = kg_pb2.CoordinateOverride(
                allowed_states=grpc_states[override.allowed_states],
                position_time=override.position_time,
                position_path_id=public_id(override.position_path_id) if override.position_path_id else None,
                module_ids=[public_id(v) for v in override.module_ids],
                excluded_module_ids=[public_id(v) for v in override.excluded_module_ids],
                premise_type=grpc_premise[override.premise_type],
                module_priority_ids=[public_id(v) for v in override.module_priority_ids],
                language_preset=grpc_lang[override.language_preset],
            )
        return kg_pb2.KnowledgeGraphConceptRequest(
            public_id=concept_public_id, coordinate_override=coord
        )

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
                    stamp=stamp_from_proto(r.stamp) if r.HasField("stamp") else None,
                )
                for r in response.results
            ],
            success=True,
        )

    def _to_semantics_response(self, response) -> ConceptSemanticsResponse:
        if not response.success:
            raise TinkarError.from_response(response.error_message)
        return ConceptSemanticsResponse(
            created_at=response.created_at,
            concept_public_id=public_ids(response.concept_public_id),
            concept_description=response.concept_description,
            total_count=response.total_count,
            semantics=[
                ConceptSemanticInfo(
                    semantic_public_id=public_ids(s.semantic_public_id),
                    pattern_public_id=public_ids(s.pattern_public_id, required=False) or None,
                    pattern_name=s.pattern_name,
                    fields=[
                        FieldValue(
                            field_type=f.WhichOneof("Value") or "unknown",
                            value=str(getattr(f, f.WhichOneof("Value")))
                            if f.WhichOneof("Value")
                            else "",
                        )
                        for f in s.fields
                    ],
                    named_fields=[
                        FieldValue(name=f.name, value=f.value, field_type="formatted")
                        for f in s.named_fields
                    ],
                    stamp=Stamp(
                        status=s.stamp.status,
                        author=s.stamp.author,
                        module=s.stamp.module,
                        path=s.stamp.path,
                        time=s.stamp.time,
                        formatted_time=s.stamp.formatted_time,
                    )
                    if s.HasField("stamp")
                    else None,
                )
                for s in response.semantics
            ],
            success=True,
        )
