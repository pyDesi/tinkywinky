import Tinkar_pb2 as _Tinkar_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SearchSortOption(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TOP_COMPONENT: _ClassVar[SearchSortOption]
    TOP_COMPONENT_ALPHA: _ClassVar[SearchSortOption]
    SEMANTIC: _ClassVar[SearchSortOption]
    SEMANTIC_ALPHA: _ClassVar[SearchSortOption]
TOP_COMPONENT: SearchSortOption
TOP_COMPONENT_ALPHA: SearchSortOption
SEMANTIC: SearchSortOption
SEMANTIC_ALPHA: SearchSortOption

class TinkarSearchQueryRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...

class TinkarConceptSearchRequest(_message.Message):
    __slots__ = ("query", "max_results")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    query: str
    max_results: int
    def __init__(self, query: _Optional[str] = ..., max_results: _Optional[int] = ...) -> None: ...

class TinkarConceptIdRequest(_message.Message):
    __slots__ = ("public_id",)
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    public_id: _Tinkar_pb2.PublicId
    def __init__(self, public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ...) -> None: ...

class TinkarSearchResult(_message.Message):
    __slots__ = ("public_id", "descriptions", "stamp")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    STAMP_FIELD_NUMBER: _ClassVar[int]
    public_id: _Tinkar_pb2.PublicId
    descriptions: TinkarConceptDescriptions
    stamp: _Tinkar_pb2.StampVersion
    def __init__(self, public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., descriptions: _Optional[_Union[TinkarConceptDescriptions, _Mapping]] = ..., stamp: _Optional[_Union[_Tinkar_pb2.StampVersion, _Mapping]] = ...) -> None: ...

class TinkarConceptDescriptions(_message.Message):
    __slots__ = ("fully_qualified_name", "regular_name", "definition")
    FULLY_QUALIFIED_NAME_FIELD_NUMBER: _ClassVar[int]
    REGULAR_NAME_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    fully_qualified_name: str
    regular_name: str
    definition: str
    def __init__(self, fully_qualified_name: _Optional[str] = ..., regular_name: _Optional[str] = ..., definition: _Optional[str] = ...) -> None: ...

class TinkarSearchQueryResponse(_message.Message):
    __slots__ = ("query", "total_count", "results", "success", "error_message", "created_at")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    query: str
    total_count: int
    results: _containers.RepeatedCompositeFieldContainer[TinkarSearchResult]
    success: bool
    error_message: str
    created_at: int
    def __init__(self, query: _Optional[str] = ..., total_count: _Optional[int] = ..., results: _Optional[_Iterable[_Union[TinkarSearchResult, _Mapping]]] = ..., success: _Optional[bool] = ..., error_message: _Optional[str] = ..., created_at: _Optional[int] = ...) -> None: ...

class TinkarRebuildIndexResponse(_message.Message):
    __slots__ = ("message", "success", "created_at")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    created_at: int
    def __init__(self, message: _Optional[str] = ..., success: _Optional[bool] = ..., created_at: _Optional[int] = ...) -> None: ...

class TinkarRebuildIndexRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TinkarConceptSearchWithSortRequest(_message.Message):
    __slots__ = ("query", "max_results", "sort_by")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    query: str
    max_results: int
    sort_by: SearchSortOption
    def __init__(self, query: _Optional[str] = ..., max_results: _Optional[int] = ..., sort_by: _Optional[_Union[SearchSortOption, str]] = ...) -> None: ...

class TinkarSemanticSearchResult(_message.Message):
    __slots__ = ("public_id", "fully_qualified_name", "regular_name", "highlighted_text", "score", "active")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    FULLY_QUALIFIED_NAME_FIELD_NUMBER: _ClassVar[int]
    REGULAR_NAME_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHTED_TEXT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    public_id: _Tinkar_pb2.PublicId
    fully_qualified_name: str
    regular_name: str
    highlighted_text: str
    score: float
    active: bool
    def __init__(self, public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., fully_qualified_name: _Optional[str] = ..., regular_name: _Optional[str] = ..., highlighted_text: _Optional[str] = ..., score: _Optional[float] = ..., active: _Optional[bool] = ...) -> None: ...

class TinkarMatchingSemantic(_message.Message):
    __slots__ = ("highlighted_text", "plain_text", "score", "field_index", "public_id")
    HIGHLIGHTED_TEXT_FIELD_NUMBER: _ClassVar[int]
    PLAIN_TEXT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    FIELD_INDEX_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    highlighted_text: str
    plain_text: str
    score: float
    field_index: int
    public_id: _Tinkar_pb2.PublicId
    def __init__(self, highlighted_text: _Optional[str] = ..., plain_text: _Optional[str] = ..., score: _Optional[float] = ..., field_index: _Optional[int] = ..., public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ...) -> None: ...

class TinkarGroupedSearchResult(_message.Message):
    __slots__ = ("public_id", "fully_qualified_name", "active", "top_score", "matching_semantics", "preferred_name", "highlighted_name")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    FULLY_QUALIFIED_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    TOP_SCORE_FIELD_NUMBER: _ClassVar[int]
    MATCHING_SEMANTICS_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_NAME_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHTED_NAME_FIELD_NUMBER: _ClassVar[int]
    public_id: _Tinkar_pb2.PublicId
    fully_qualified_name: str
    active: bool
    top_score: float
    matching_semantics: _containers.RepeatedCompositeFieldContainer[TinkarMatchingSemantic]
    preferred_name: str
    highlighted_name: str
    def __init__(self, public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., fully_qualified_name: _Optional[str] = ..., active: _Optional[bool] = ..., top_score: _Optional[float] = ..., matching_semantics: _Optional[_Iterable[_Union[TinkarMatchingSemantic, _Mapping]]] = ..., preferred_name: _Optional[str] = ..., highlighted_name: _Optional[str] = ...) -> None: ...

class TinkarConceptSearchWithSortResponse(_message.Message):
    __slots__ = ("query", "total_count", "sort_by", "results", "grouped_results", "success", "error_message", "created_at")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    GROUPED_RESULTS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    query: str
    total_count: int
    sort_by: SearchSortOption
    results: _containers.RepeatedCompositeFieldContainer[TinkarSemanticSearchResult]
    grouped_results: _containers.RepeatedCompositeFieldContainer[TinkarGroupedSearchResult]
    success: bool
    error_message: str
    created_at: int
    def __init__(self, query: _Optional[str] = ..., total_count: _Optional[int] = ..., sort_by: _Optional[_Union[SearchSortOption, str]] = ..., results: _Optional[_Iterable[_Union[TinkarSemanticSearchResult, _Mapping]]] = ..., grouped_results: _Optional[_Iterable[_Union[TinkarGroupedSearchResult, _Mapping]]] = ..., success: _Optional[bool] = ..., error_message: _Optional[str] = ..., created_at: _Optional[int] = ...) -> None: ...

class TinkarStampInfo(_message.Message):
    __slots__ = ("status", "author", "module", "path", "time", "formatted_time")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    MODULE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    FORMATTED_TIME_FIELD_NUMBER: _ClassVar[int]
    status: str
    author: str
    module: str
    path: str
    time: int
    formatted_time: str
    def __init__(self, status: _Optional[str] = ..., author: _Optional[str] = ..., module: _Optional[str] = ..., path: _Optional[str] = ..., time: _Optional[int] = ..., formatted_time: _Optional[str] = ...) -> None: ...

class TinkarSemanticField(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class TinkarConceptSemanticInfo(_message.Message):
    __slots__ = ("semantic_public_id", "pattern_public_id", "pattern_name", "fields", "stamp", "named_fields")
    SEMANTIC_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_NAME_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    STAMP_FIELD_NUMBER: _ClassVar[int]
    NAMED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    semantic_public_id: _Tinkar_pb2.PublicId
    pattern_public_id: _Tinkar_pb2.PublicId
    pattern_name: str
    fields: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.Field]
    stamp: TinkarStampInfo
    named_fields: _containers.RepeatedCompositeFieldContainer[TinkarSemanticField]
    def __init__(self, semantic_public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., pattern_public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., pattern_name: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[_Tinkar_pb2.Field, _Mapping]]] = ..., stamp: _Optional[_Union[TinkarStampInfo, _Mapping]] = ..., named_fields: _Optional[_Iterable[_Union[TinkarSemanticField, _Mapping]]] = ...) -> None: ...

class TinkarConceptSemanticsResponse(_message.Message):
    __slots__ = ("concept_public_id", "concept_description", "total_count", "semantics", "success", "error_message", "created_at")
    CONCEPT_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    CONCEPT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    SEMANTICS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    concept_public_id: _Tinkar_pb2.PublicId
    concept_description: str
    total_count: int
    semantics: _containers.RepeatedCompositeFieldContainer[TinkarConceptSemanticInfo]
    success: bool
    error_message: str
    created_at: int
    def __init__(self, concept_public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., concept_description: _Optional[str] = ..., total_count: _Optional[int] = ..., semantics: _Optional[_Iterable[_Union[TinkarConceptSemanticInfo, _Mapping]]] = ..., success: _Optional[bool] = ..., error_message: _Optional[str] = ..., created_at: _Optional[int] = ...) -> None: ...

class TinkarSemanticInfoResponse(_message.Message):
    __slots__ = ("success", "error_message", "semantic", "created_at")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SEMANTIC_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    semantic: TinkarConceptSemanticInfo
    created_at: int
    def __init__(self, success: _Optional[bool] = ..., error_message: _Optional[str] = ..., semantic: _Optional[_Union[TinkarConceptSemanticInfo, _Mapping]] = ..., created_at: _Optional[int] = ...) -> None: ...

class TinkarConceptEntityResponse(_message.Message):
    __slots__ = ("success", "error_message", "entities", "created_at")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    entities: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.TinkarMsg]
    created_at: int
    def __init__(self, success: _Optional[bool] = ..., error_message: _Optional[str] = ..., entities: _Optional[_Iterable[_Union[_Tinkar_pb2.TinkarMsg, _Mapping]]] = ..., created_at: _Optional[int] = ...) -> None: ...
