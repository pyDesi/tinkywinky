from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VertexUUID(_message.Message):
    __slots__ = ("uuid", "most_significant_bits", "least_significant_bits")
    UUID_FIELD_NUMBER: _ClassVar[int]
    MOST_SIGNIFICANT_BITS_FIELD_NUMBER: _ClassVar[int]
    LEAST_SIGNIFICANT_BITS_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    most_significant_bits: int
    least_significant_bits: int
    def __init__(self, uuid: _Optional[str] = ..., most_significant_bits: _Optional[int] = ..., least_significant_bits: _Optional[int] = ...) -> None: ...

class PublicId(_message.Message):
    __slots__ = ("uuids", "uuid_bits", "sequence")
    UUIDS_FIELD_NUMBER: _ClassVar[int]
    UUID_BITS_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    uuids: _containers.RepeatedScalarFieldContainer[str]
    uuid_bits: _containers.RepeatedScalarFieldContainer[int]
    sequence: int
    def __init__(self, uuids: _Optional[_Iterable[str]] = ..., uuid_bits: _Optional[_Iterable[int]] = ..., sequence: _Optional[int] = ...) -> None: ...

class PublicIdList(_message.Message):
    __slots__ = ("public_ids",)
    PUBLIC_IDS_FIELD_NUMBER: _ClassVar[int]
    public_ids: _containers.RepeatedCompositeFieldContainer[PublicId]
    def __init__(self, public_ids: _Optional[_Iterable[_Union[PublicId, _Mapping]]] = ...) -> None: ...

class PublicIdSet(_message.Message):
    __slots__ = ("public_ids",)
    PUBLIC_IDS_FIELD_NUMBER: _ClassVar[int]
    public_ids: _containers.RepeatedCompositeFieldContainer[PublicId]
    def __init__(self, public_ids: _Optional[_Iterable[_Union[PublicId, _Mapping]]] = ...) -> None: ...

class Field(_message.Message):
    __slots__ = ("string_value", "boolean_value", "int_value", "float_value", "bytes_value", "time_value", "public_id", "vertex_uuid", "public_ids", "public_idset", "di_graph", "di_tree", "graph", "vertex", "planar_point", "spatial_point", "int_to_int_map", "int_to_multiple_int_map", "big_decimal", "long", "object_array")
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOLEAN_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    BYTES_VALUE_FIELD_NUMBER: _ClassVar[int]
    TIME_VALUE_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    VERTEX_UUID_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_IDS_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_IDSET_FIELD_NUMBER: _ClassVar[int]
    DI_GRAPH_FIELD_NUMBER: _ClassVar[int]
    DI_TREE_FIELD_NUMBER: _ClassVar[int]
    GRAPH_FIELD_NUMBER: _ClassVar[int]
    VERTEX_FIELD_NUMBER: _ClassVar[int]
    PLANAR_POINT_FIELD_NUMBER: _ClassVar[int]
    SPATIAL_POINT_FIELD_NUMBER: _ClassVar[int]
    INT_TO_INT_MAP_FIELD_NUMBER: _ClassVar[int]
    INT_TO_MULTIPLE_INT_MAP_FIELD_NUMBER: _ClassVar[int]
    BIG_DECIMAL_FIELD_NUMBER: _ClassVar[int]
    LONG_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ARRAY_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    boolean_value: bool
    int_value: int
    float_value: float
    bytes_value: bytes
    time_value: int
    public_id: PublicId
    vertex_uuid: VertexUUID
    public_ids: PublicIdList
    public_idset: PublicIdSet
    di_graph: DiGraph
    di_tree: DiTree
    graph: Graph
    vertex: Vertex
    planar_point: PlanarPoint
    spatial_point: SpatialPoint
    int_to_int_map: IntToIntMap
    int_to_multiple_int_map: IntToMultipleIntMap
    big_decimal: BigDecimal
    long: Long
    object_array: FieldArray
    def __init__(self, string_value: _Optional[str] = ..., boolean_value: _Optional[bool] = ..., int_value: _Optional[int] = ..., float_value: _Optional[float] = ..., bytes_value: _Optional[bytes] = ..., time_value: _Optional[int] = ..., public_id: _Optional[_Union[PublicId, _Mapping]] = ..., vertex_uuid: _Optional[_Union[VertexUUID, _Mapping]] = ..., public_ids: _Optional[_Union[PublicIdList, _Mapping]] = ..., public_idset: _Optional[_Union[PublicIdSet, _Mapping]] = ..., di_graph: _Optional[_Union[DiGraph, _Mapping]] = ..., di_tree: _Optional[_Union[DiTree, _Mapping]] = ..., graph: _Optional[_Union[Graph, _Mapping]] = ..., vertex: _Optional[_Union[Vertex, _Mapping]] = ..., planar_point: _Optional[_Union[PlanarPoint, _Mapping]] = ..., spatial_point: _Optional[_Union[SpatialPoint, _Mapping]] = ..., int_to_int_map: _Optional[_Union[IntToIntMap, _Mapping]] = ..., int_to_multiple_int_map: _Optional[_Union[IntToMultipleIntMap, _Mapping]] = ..., big_decimal: _Optional[_Union[BigDecimal, _Mapping]] = ..., long: _Optional[_Union[Long, _Mapping]] = ..., object_array: _Optional[_Union[FieldArray, _Mapping]] = ...) -> None: ...

class FieldArray(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[Field]
    def __init__(self, values: _Optional[_Iterable[_Union[Field, _Mapping]]] = ...) -> None: ...

class PlanarPoint(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class SpatialPoint(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...

class IntToIntMap(_message.Message):
    __slots__ = ("source", "target")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    source: int
    target: int
    def __init__(self, source: _Optional[int] = ..., target: _Optional[int] = ...) -> None: ...

class IntToMultipleIntMap(_message.Message):
    __slots__ = ("source", "targets")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TARGETS_FIELD_NUMBER: _ClassVar[int]
    source: int
    targets: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, source: _Optional[int] = ..., targets: _Optional[_Iterable[int]] = ...) -> None: ...

class BigDecimal(_message.Message):
    __slots__ = ("scale", "precision", "value")
    SCALE_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    scale: int
    precision: int
    value: str
    def __init__(self, scale: _Optional[int] = ..., precision: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...

class Long(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class DiTree(_message.Message):
    __slots__ = ("vertices", "root", "predecessor_map", "successor_map")
    VERTICES_FIELD_NUMBER: _ClassVar[int]
    ROOT_FIELD_NUMBER: _ClassVar[int]
    PREDECESSOR_MAP_FIELD_NUMBER: _ClassVar[int]
    SUCCESSOR_MAP_FIELD_NUMBER: _ClassVar[int]
    vertices: _containers.RepeatedCompositeFieldContainer[Vertex]
    root: int
    predecessor_map: _containers.RepeatedCompositeFieldContainer[IntToIntMap]
    successor_map: _containers.RepeatedCompositeFieldContainer[IntToMultipleIntMap]
    def __init__(self, vertices: _Optional[_Iterable[_Union[Vertex, _Mapping]]] = ..., root: _Optional[int] = ..., predecessor_map: _Optional[_Iterable[_Union[IntToIntMap, _Mapping]]] = ..., successor_map: _Optional[_Iterable[_Union[IntToMultipleIntMap, _Mapping]]] = ...) -> None: ...

class DiGraph(_message.Message):
    __slots__ = ("vertices", "roots", "successor_map", "predecessor_map")
    VERTICES_FIELD_NUMBER: _ClassVar[int]
    ROOTS_FIELD_NUMBER: _ClassVar[int]
    SUCCESSOR_MAP_FIELD_NUMBER: _ClassVar[int]
    PREDECESSOR_MAP_FIELD_NUMBER: _ClassVar[int]
    vertices: _containers.RepeatedCompositeFieldContainer[Vertex]
    roots: _containers.RepeatedScalarFieldContainer[int]
    successor_map: _containers.RepeatedCompositeFieldContainer[IntToMultipleIntMap]
    predecessor_map: _containers.RepeatedCompositeFieldContainer[IntToMultipleIntMap]
    def __init__(self, vertices: _Optional[_Iterable[_Union[Vertex, _Mapping]]] = ..., roots: _Optional[_Iterable[int]] = ..., successor_map: _Optional[_Iterable[_Union[IntToMultipleIntMap, _Mapping]]] = ..., predecessor_map: _Optional[_Iterable[_Union[IntToMultipleIntMap, _Mapping]]] = ...) -> None: ...

class Graph(_message.Message):
    __slots__ = ("vertices", "successor_map", "roots")
    VERTICES_FIELD_NUMBER: _ClassVar[int]
    SUCCESSOR_MAP_FIELD_NUMBER: _ClassVar[int]
    ROOTS_FIELD_NUMBER: _ClassVar[int]
    vertices: _containers.RepeatedCompositeFieldContainer[Vertex]
    successor_map: _containers.RepeatedCompositeFieldContainer[IntToMultipleIntMap]
    roots: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, vertices: _Optional[_Iterable[_Union[Vertex, _Mapping]]] = ..., successor_map: _Optional[_Iterable[_Union[IntToMultipleIntMap, _Mapping]]] = ..., roots: _Optional[_Iterable[int]] = ...) -> None: ...

class Vertex(_message.Message):
    __slots__ = ("vertex_uuid", "index", "meaning_public_id", "properties")
    class Property(_message.Message):
        __slots__ = ("public_id", "field")
        PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
        FIELD_FIELD_NUMBER: _ClassVar[int]
        public_id: PublicId
        field: Field
        def __init__(self, public_id: _Optional[_Union[PublicId, _Mapping]] = ..., field: _Optional[_Union[Field, _Mapping]] = ...) -> None: ...
    VERTEX_UUID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    MEANING_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    vertex_uuid: VertexUUID
    index: int
    meaning_public_id: PublicId
    properties: _containers.RepeatedCompositeFieldContainer[Vertex.Property]
    def __init__(self, vertex_uuid: _Optional[_Union[VertexUUID, _Mapping]] = ..., index: _Optional[int] = ..., meaning_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., properties: _Optional[_Iterable[_Union[Vertex.Property, _Mapping]]] = ...) -> None: ...

class StampChronology(_message.Message):
    __slots__ = ("public_id", "first_stamp_version", "second_stamp_version", "pattern_for_stamp_public_id")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_STAMP_VERSION_FIELD_NUMBER: _ClassVar[int]
    SECOND_STAMP_VERSION_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FOR_STAMP_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    public_id: PublicId
    first_stamp_version: StampVersion
    second_stamp_version: StampVersion
    pattern_for_stamp_public_id: PublicId
    def __init__(self, public_id: _Optional[_Union[PublicId, _Mapping]] = ..., first_stamp_version: _Optional[_Union[StampVersion, _Mapping]] = ..., second_stamp_version: _Optional[_Union[StampVersion, _Mapping]] = ..., pattern_for_stamp_public_id: _Optional[_Union[PublicId, _Mapping]] = ...) -> None: ...

class StampVersion(_message.Message):
    __slots__ = ("status_public_id", "author_public_id", "module_public_id", "path_public_id", "time")
    STATUS_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    status_public_id: PublicId
    author_public_id: PublicId
    module_public_id: PublicId
    path_public_id: PublicId
    time: int
    def __init__(self, status_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., author_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., module_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., path_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., time: _Optional[int] = ...) -> None: ...

class ConceptChronology(_message.Message):
    __slots__ = ("public_id", "concept_versions", "pattern_for_concept_public_id")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    CONCEPT_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FOR_CONCEPT_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    public_id: PublicId
    concept_versions: _containers.RepeatedCompositeFieldContainer[ConceptVersion]
    pattern_for_concept_public_id: PublicId
    def __init__(self, public_id: _Optional[_Union[PublicId, _Mapping]] = ..., concept_versions: _Optional[_Iterable[_Union[ConceptVersion, _Mapping]]] = ..., pattern_for_concept_public_id: _Optional[_Union[PublicId, _Mapping]] = ...) -> None: ...

class ConceptVersion(_message.Message):
    __slots__ = ("stamp_chronology_public_id",)
    STAMP_CHRONOLOGY_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    stamp_chronology_public_id: PublicId
    def __init__(self, stamp_chronology_public_id: _Optional[_Union[PublicId, _Mapping]] = ...) -> None: ...

class FieldDefinition(_message.Message):
    __slots__ = ("meaning_public_id", "data_type_public_id", "purpose_public_id", "index")
    MEANING_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    meaning_public_id: PublicId
    data_type_public_id: PublicId
    purpose_public_id: PublicId
    index: int
    def __init__(self, meaning_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., data_type_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., purpose_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., index: _Optional[int] = ...) -> None: ...

class PatternChronology(_message.Message):
    __slots__ = ("public_id", "pattern_versions", "pattern_for_pattern_public_id")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FOR_PATTERN_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    public_id: PublicId
    pattern_versions: _containers.RepeatedCompositeFieldContainer[PatternVersion]
    pattern_for_pattern_public_id: PublicId
    def __init__(self, public_id: _Optional[_Union[PublicId, _Mapping]] = ..., pattern_versions: _Optional[_Iterable[_Union[PatternVersion, _Mapping]]] = ..., pattern_for_pattern_public_id: _Optional[_Union[PublicId, _Mapping]] = ...) -> None: ...

class PatternVersion(_message.Message):
    __slots__ = ("stamp_chronology_public_id", "referenced_component_purpose_public_id", "referenced_component_meaning_public_id", "field_definitions")
    STAMP_CHRONOLOGY_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCED_COMPONENT_PURPOSE_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCED_COMPONENT_MEANING_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    FIELD_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    stamp_chronology_public_id: PublicId
    referenced_component_purpose_public_id: PublicId
    referenced_component_meaning_public_id: PublicId
    field_definitions: _containers.RepeatedCompositeFieldContainer[FieldDefinition]
    def __init__(self, stamp_chronology_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., referenced_component_purpose_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., referenced_component_meaning_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., field_definitions: _Optional[_Iterable[_Union[FieldDefinition, _Mapping]]] = ...) -> None: ...

class SemanticChronology(_message.Message):
    __slots__ = ("public_id", "referenced_component_public_id", "pattern_for_semantic_public_id", "semantic_versions")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCED_COMPONENT_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FOR_SEMANTIC_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    SEMANTIC_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    public_id: PublicId
    referenced_component_public_id: PublicId
    pattern_for_semantic_public_id: PublicId
    semantic_versions: _containers.RepeatedCompositeFieldContainer[SemanticVersion]
    def __init__(self, public_id: _Optional[_Union[PublicId, _Mapping]] = ..., referenced_component_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., pattern_for_semantic_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., semantic_versions: _Optional[_Iterable[_Union[SemanticVersion, _Mapping]]] = ...) -> None: ...

class SemanticVersion(_message.Message):
    __slots__ = ("stamp_chronology_public_id", "fields")
    STAMP_CHRONOLOGY_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    stamp_chronology_public_id: PublicId
    fields: _containers.RepeatedCompositeFieldContainer[Field]
    def __init__(self, stamp_chronology_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., fields: _Optional[_Iterable[_Union[Field, _Mapping]]] = ...) -> None: ...

class PatternMembers(_message.Message):
    __slots__ = ("pattern_public_id", "component_public_ids")
    PATTERN_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_PUBLIC_IDS_FIELD_NUMBER: _ClassVar[int]
    pattern_public_id: PublicId
    component_public_ids: _containers.RepeatedCompositeFieldContainer[PublicId]
    def __init__(self, pattern_public_id: _Optional[_Union[PublicId, _Mapping]] = ..., component_public_ids: _Optional[_Iterable[_Union[PublicId, _Mapping]]] = ...) -> None: ...

class ComponentTable(_message.Message):
    __slots__ = ("components",)
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    components: _containers.RepeatedCompositeFieldContainer[ComponentEntry]
    def __init__(self, components: _Optional[_Iterable[_Union[ComponentEntry, _Mapping]]] = ...) -> None: ...

class ComponentEntry(_message.Message):
    __slots__ = ("pattern_sequence", "uuid_bits", "referenced_only")
    PATTERN_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    UUID_BITS_FIELD_NUMBER: _ClassVar[int]
    REFERENCED_ONLY_FIELD_NUMBER: _ClassVar[int]
    pattern_sequence: int
    uuid_bits: _containers.RepeatedScalarFieldContainer[int]
    referenced_only: bool
    def __init__(self, pattern_sequence: _Optional[int] = ..., uuid_bits: _Optional[_Iterable[int]] = ..., referenced_only: _Optional[bool] = ...) -> None: ...

class TinkarMsg(_message.Message):
    __slots__ = ("concept_chronology", "semantic_chronology", "pattern_chronology", "stamp_chronology")
    CONCEPT_CHRONOLOGY_FIELD_NUMBER: _ClassVar[int]
    SEMANTIC_CHRONOLOGY_FIELD_NUMBER: _ClassVar[int]
    PATTERN_CHRONOLOGY_FIELD_NUMBER: _ClassVar[int]
    STAMP_CHRONOLOGY_FIELD_NUMBER: _ClassVar[int]
    concept_chronology: ConceptChronology
    semantic_chronology: SemanticChronology
    pattern_chronology: PatternChronology
    stamp_chronology: StampChronology
    def __init__(self, concept_chronology: _Optional[_Union[ConceptChronology, _Mapping]] = ..., semantic_chronology: _Optional[_Union[SemanticChronology, _Mapping]] = ..., pattern_chronology: _Optional[_Union[PatternChronology, _Mapping]] = ..., stamp_chronology: _Optional[_Union[StampChronology, _Mapping]] = ...) -> None: ...
