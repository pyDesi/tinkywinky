"""Pydantic models for Tinkar API responses."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


# ============================================================================
# Base
# ============================================================================


class TinkarResponse(BaseModel):
    """Base for all Tinkar API responses."""

    model_config = ConfigDict(frozen=True)

    success: bool
    error_message: str | None = None
    created_at: int | None = None


# ============================================================================
# Shared / Tier 1 concepts
# ============================================================================


class Stamp(BaseModel):
    """STAMP version info (status, author, module, path, time).

    In Tier 1 responses (search, entities, lidr), fields contain raw PublicId UUIDs.
    In Tier 2 responses (knowledge_graph semantics), fields contain human-readable strings.
    """

    model_config = ConfigDict(frozen=True)

    status: str
    author: str
    module: str
    path: str
    time: int
    formatted_time: str = ""


class Concept(BaseModel):
    """A single Tinkar concept."""

    model_config = ConfigDict(frozen=True)

    public_id: list[str]
    fully_qualified_name: str
    regular_name: str
    definition: str
    stamp: Stamp | None = None


class MatchingSemantic(BaseModel):
    """A matching semantic within a grouped search result."""

    model_config = ConfigDict(frozen=True)

    highlighted_text: str
    plain_text: str
    score: float
    field_index: int = 0
    # Store-local nids were removed from the wire. Never fabricate a zero nid.
    semantic_nid: int | None = None
    public_id: list[str] = []


class GroupedResult(BaseModel):
    """A grouped search result (by top-level component)."""

    model_config = ConfigDict(frozen=True)

    public_id: list[str]
    fully_qualified_name: str
    is_active: bool
    top_score: float
    concept_nid: int | None = None
    preferred_name: str = ""
    highlighted_name: str = ""
    matching_semantics: list[MatchingSemantic]


class SemanticResult(BaseModel):
    """A flat semantic search result with score."""

    model_config = ConfigDict(frozen=True)

    public_id: list[str]
    fully_qualified_name: str
    regular_name: str
    highlighted_text: str
    score: float
    is_active: bool


# ============================================================================
# Tier 1 responses (IkeGraphRAG)
# ============================================================================


class SearchResponse(TinkarResponse):
    """Response from search and concept search operations."""

    query: str
    total_count: int
    results: list[Concept]


class ConceptResponse(TinkarResponse):
    """Response from single concept lookup."""

    concept: Concept


class ConceptListResponse(TinkarResponse):
    """Response from operations that return a list of concepts."""

    total_count: int
    concepts: list[Concept]


class GroupedSearchResponse(TinkarResponse):
    """Response from component-grouped search."""

    query: str
    total_count: int
    results: list[GroupedResult]


class SemanticSearchResponse(TinkarResponse):
    """Response from semantic search."""

    query: str
    total_count: int
    results: list[SemanticResult]


class RebuildIndexResponse(TinkarResponse):
    """Response from rebuild index operation."""

    message: str


# ============================================================================
# Tier 2 models (IkeKnowledgeGraph)
# ============================================================================


class AllowedStates(str, Enum):
    """Status filter for STAMP coordinates."""

    ACTIVE_AND_INACTIVE = "ACTIVE_AND_INACTIVE"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class PremiseType(str, Enum):
    """Navigation premise type."""

    INFERRED = "INFERRED"
    STATED = "STATED"


class LanguagePreset(str, Enum):
    """Language coordinate presets."""

    US_ENGLISH_REGULAR_NAME = "US_ENGLISH_REGULAR_NAME"
    US_ENGLISH_FULLY_QUALIFIED_NAME = "US_ENGLISH_FULLY_QUALIFIED_NAME"
    GB_ENGLISH_PREFERRED_NAME = "GB_ENGLISH_PREFERRED_NAME"
    GB_ENGLISH_FULLY_QUALIFIED_NAME = "GB_ENGLISH_FULLY_QUALIFIED_NAME"
    ANY_LANGUAGE_REGULAR_NAME = "ANY_LANGUAGE_REGULAR_NAME"
    ANY_LANGUAGE_FULLY_QUALIFIED_NAME = "ANY_LANGUAGE_FULLY_QUALIFIED_NAME"
    ANY_LANGUAGE_DEFINITION = "ANY_LANGUAGE_DEFINITION"
    SPANISH_PREFERRED_NAME = "SPANISH_PREFERRED_NAME"
    SPANISH_FULLY_QUALIFIED_NAME = "SPANISH_FULLY_QUALIFIED_NAME"


class CoordinateOverride(BaseModel):
    """Optional coordinate overrides for Tier 2 queries."""

    model_config = ConfigDict(frozen=True)

    allowed_states: AllowedStates = AllowedStates.ACTIVE_AND_INACTIVE
    position_time: int = 0
    position_path_id: str = ""
    module_ids: list[str] = []
    excluded_module_ids: list[str] = []
    premise_type: PremiseType = PremiseType.INFERRED
    module_priority_ids: list[str] = []
    language_preset: LanguagePreset = LanguagePreset.US_ENGLISH_REGULAR_NAME


class FieldValue(BaseModel):
    """A field value from a semantic."""

    model_config = ConfigDict(frozen=True)

    field_type: str
    value: str
    name: str = ""


class ConceptSemanticInfo(BaseModel):
    """Information about a single semantic attached to a concept."""

    model_config = ConfigDict(frozen=True)

    semantic_public_id: list[str]
    # The active server can omit the pattern identifier even when its name resolves.
    # None means unavailable at the source, not an empty or fabricated identifier.
    pattern_public_id: list[str] | None = None
    pattern_name: str
    fields: list[FieldValue]
    named_fields: list[FieldValue] = []
    stamp: Stamp | None = None


class ConceptSemanticsResponse(TinkarResponse):
    """Response from concept semantics lookup."""

    concept_public_id: list[str]
    concept_description: str
    total_count: int
    semantics: list[ConceptSemanticInfo]


class TinkarConceptEntityResponse(TinkarResponse):
    """Response carrying raw entity chronologies for local entity-store hydration.

    Each item in ``entities`` is a serialized ``TinkarMsg``. Parse with::

        from tinkar._generated.Tinkar_pb2 import TinkarMsg
        for raw in response.entities:
            msg = TinkarMsg.FromString(raw)
    """

    entities: list[bytes] = []


class SavedCoordinateResponse(TinkarResponse):
    """Response from saving a coordinate."""

    id: str
    public_id: list[str] = []
    created_at: str


class StampCoordinateEntry(BaseModel):
    """A saved stamp coordinate."""

    model_config = ConfigDict(frozen=True)

    id: str
    public_id: list[str] = []
    allowed_states: str
    position_time: int
    position_path_id: str
    module_ids: list[str]
    excluded_module_ids: list[str]
    module_priority_ids: list[str]
    created_at: str


class NavigationCoordinateEntry(BaseModel):
    """A saved navigation coordinate."""

    model_config = ConfigDict(frozen=True)

    id: str
    public_id: list[str] = []
    premise_type: str
    created_at: str


class LanguageCoordinateEntry(BaseModel):
    """A saved language coordinate."""

    model_config = ConfigDict(frozen=True)

    id: str
    public_id: list[str] = []
    language_preset: str
    created_at: str


class CoordinateListResponse(TinkarResponse):
    """Response from listing saved coordinates."""

    stamps: list[StampCoordinateEntry] = []
    navigations: list[NavigationCoordinateEntry] = []
    languages: list[LanguageCoordinateEntry] = []


# ============================================================================
# Tier 3 models (IkeAdmin)
# ============================================================================


class ExportType(str, Enum):
    """Export type selection."""

    FULL = "FULL"
    TEMPORAL = "TEMPORAL"
    MEMBERSHIP = "MEMBERSHIP"


class EntityCountSummary(BaseModel):
    """Summary of entity counts from import/export operations."""

    model_config = ConfigDict(frozen=True)

    concepts_count: int
    semantics_count: int
    patterns_count: int
    stamps_count: int
    total_count: int


class ImportChangesetResponse(TinkarResponse):
    """Response from changeset import."""

    entity_counts: EntityCountSummary | None = None


class ExportEntitiesResponse(TinkarResponse):
    """Response from entity export."""

    entity_counts: EntityCountSummary | None = None
    export_data: bytes = b""


class ReasonerResults(BaseModel):
    """Summary of classification results."""

    model_config = ConfigDict(frozen=True)

    classified_concept_count: int
    inferred_changes_count: int
    navigation_changes_count: int
    equivalent_sets_count: int
    cycles_count: int
    orphans_count: int


class RunReasonerResponse(TinkarResponse):
    """Response from reasoner classification."""

    results: ReasonerResults | None = None
    duration_ms: int = 0
