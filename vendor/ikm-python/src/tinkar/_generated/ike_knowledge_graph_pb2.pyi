import Tinkar_pb2 as _Tinkar_pb2
import ike_types_pb2 as _ike_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AllowedStates(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVE_AND_INACTIVE: _ClassVar[AllowedStates]
    ACTIVE: _ClassVar[AllowedStates]
    INACTIVE: _ClassVar[AllowedStates]

class ProtoPremiseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INFERRED: _ClassVar[ProtoPremiseType]
    STATED: _ClassVar[ProtoPremiseType]

class ProtoLanguagePreset(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    US_ENGLISH_REGULAR_NAME: _ClassVar[ProtoLanguagePreset]
    US_ENGLISH_FULLY_QUALIFIED_NAME: _ClassVar[ProtoLanguagePreset]
    GB_ENGLISH_PREFERRED_NAME: _ClassVar[ProtoLanguagePreset]
    GB_ENGLISH_FULLY_QUALIFIED_NAME: _ClassVar[ProtoLanguagePreset]
    ANY_LANGUAGE_REGULAR_NAME: _ClassVar[ProtoLanguagePreset]
    ANY_LANGUAGE_FULLY_QUALIFIED_NAME: _ClassVar[ProtoLanguagePreset]
    ANY_LANGUAGE_DEFINITION: _ClassVar[ProtoLanguagePreset]
    SPANISH_PREFERRED_NAME: _ClassVar[ProtoLanguagePreset]
    SPANISH_FULLY_QUALIFIED_NAME: _ClassVar[ProtoLanguagePreset]
ACTIVE_AND_INACTIVE: AllowedStates
ACTIVE: AllowedStates
INACTIVE: AllowedStates
INFERRED: ProtoPremiseType
STATED: ProtoPremiseType
US_ENGLISH_REGULAR_NAME: ProtoLanguagePreset
US_ENGLISH_FULLY_QUALIFIED_NAME: ProtoLanguagePreset
GB_ENGLISH_PREFERRED_NAME: ProtoLanguagePreset
GB_ENGLISH_FULLY_QUALIFIED_NAME: ProtoLanguagePreset
ANY_LANGUAGE_REGULAR_NAME: ProtoLanguagePreset
ANY_LANGUAGE_FULLY_QUALIFIED_NAME: ProtoLanguagePreset
ANY_LANGUAGE_DEFINITION: ProtoLanguagePreset
SPANISH_PREFERRED_NAME: ProtoLanguagePreset
SPANISH_FULLY_QUALIFIED_NAME: ProtoLanguagePreset

class CoordinateOverride(_message.Message):
    __slots__ = ("allowed_states", "position_time", "position_path_id", "module_ids", "excluded_module_ids", "premise_type", "module_priority_ids", "language_preset")
    ALLOWED_STATES_FIELD_NUMBER: _ClassVar[int]
    POSITION_TIME_FIELD_NUMBER: _ClassVar[int]
    POSITION_PATH_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_IDS_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_MODULE_IDS_FIELD_NUMBER: _ClassVar[int]
    PREMISE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MODULE_PRIORITY_IDS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_PRESET_FIELD_NUMBER: _ClassVar[int]
    allowed_states: AllowedStates
    position_time: int
    position_path_id: _Tinkar_pb2.PublicId
    module_ids: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    excluded_module_ids: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    premise_type: ProtoPremiseType
    module_priority_ids: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    language_preset: ProtoLanguagePreset
    def __init__(self, allowed_states: _Optional[_Union[AllowedStates, str]] = ..., position_time: _Optional[int] = ..., position_path_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., module_ids: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., excluded_module_ids: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., premise_type: _Optional[_Union[ProtoPremiseType, str]] = ..., module_priority_ids: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., language_preset: _Optional[_Union[ProtoLanguagePreset, str]] = ...) -> None: ...

class KnowledgeGraphConceptRequest(_message.Message):
    __slots__ = ("public_id", "coordinate_override")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    public_id: _Tinkar_pb2.PublicId
    coordinate_override: CoordinateOverride
    def __init__(self, public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., coordinate_override: _Optional[_Union[CoordinateOverride, _Mapping]] = ...) -> None: ...

class StampCoordinateSettings(_message.Message):
    __slots__ = ("allowed_states", "position_time", "position_path_id", "module_ids", "excluded_module_ids", "module_priority_ids")
    ALLOWED_STATES_FIELD_NUMBER: _ClassVar[int]
    POSITION_TIME_FIELD_NUMBER: _ClassVar[int]
    POSITION_PATH_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_IDS_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_MODULE_IDS_FIELD_NUMBER: _ClassVar[int]
    MODULE_PRIORITY_IDS_FIELD_NUMBER: _ClassVar[int]
    allowed_states: AllowedStates
    position_time: int
    position_path_id: _Tinkar_pb2.PublicId
    module_ids: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    excluded_module_ids: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    module_priority_ids: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    def __init__(self, allowed_states: _Optional[_Union[AllowedStates, str]] = ..., position_time: _Optional[int] = ..., position_path_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., module_ids: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., excluded_module_ids: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., module_priority_ids: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ...) -> None: ...

class NavigationCoordinateSettings(_message.Message):
    __slots__ = ("premise_type",)
    PREMISE_TYPE_FIELD_NUMBER: _ClassVar[int]
    premise_type: ProtoPremiseType
    def __init__(self, premise_type: _Optional[_Union[ProtoPremiseType, str]] = ...) -> None: ...

class LanguageCoordinateSettings(_message.Message):
    __slots__ = ("language_preset",)
    LANGUAGE_PRESET_FIELD_NUMBER: _ClassVar[int]
    language_preset: ProtoLanguagePreset
    def __init__(self, language_preset: _Optional[_Union[ProtoLanguagePreset, str]] = ...) -> None: ...

class SaveStampCoordinateRequest(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: StampCoordinateSettings
    def __init__(self, settings: _Optional[_Union[StampCoordinateSettings, _Mapping]] = ...) -> None: ...

class SavedStampCoordinateResponse(_message.Message):
    __slots__ = ("id", "settings", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: _Tinkar_pb2.PublicId
    settings: StampCoordinateSettings
    created_at: str
    def __init__(self, id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., settings: _Optional[_Union[StampCoordinateSettings, _Mapping]] = ..., created_at: _Optional[str] = ...) -> None: ...

class ListStampCoordinatesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListStampCoordinatesResponse(_message.Message):
    __slots__ = ("coordinates", "created_at")
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    coordinates: _containers.RepeatedCompositeFieldContainer[SavedStampCoordinateResponse]
    created_at: int
    def __init__(self, coordinates: _Optional[_Iterable[_Union[SavedStampCoordinateResponse, _Mapping]]] = ..., created_at: _Optional[int] = ...) -> None: ...

class SaveNavigationCoordinateRequest(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: NavigationCoordinateSettings
    def __init__(self, settings: _Optional[_Union[NavigationCoordinateSettings, _Mapping]] = ...) -> None: ...

class SavedNavigationCoordinateResponse(_message.Message):
    __slots__ = ("id", "settings", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: _Tinkar_pb2.PublicId
    settings: NavigationCoordinateSettings
    created_at: str
    def __init__(self, id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., settings: _Optional[_Union[NavigationCoordinateSettings, _Mapping]] = ..., created_at: _Optional[str] = ...) -> None: ...

class ListNavigationCoordinatesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNavigationCoordinatesResponse(_message.Message):
    __slots__ = ("coordinates", "created_at")
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    coordinates: _containers.RepeatedCompositeFieldContainer[SavedNavigationCoordinateResponse]
    created_at: int
    def __init__(self, coordinates: _Optional[_Iterable[_Union[SavedNavigationCoordinateResponse, _Mapping]]] = ..., created_at: _Optional[int] = ...) -> None: ...

class SaveLanguageCoordinateRequest(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: LanguageCoordinateSettings
    def __init__(self, settings: _Optional[_Union[LanguageCoordinateSettings, _Mapping]] = ...) -> None: ...

class SavedLanguageCoordinateResponse(_message.Message):
    __slots__ = ("id", "settings", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: _Tinkar_pb2.PublicId
    settings: LanguageCoordinateSettings
    created_at: str
    def __init__(self, id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., settings: _Optional[_Union[LanguageCoordinateSettings, _Mapping]] = ..., created_at: _Optional[str] = ...) -> None: ...

class ListLanguageCoordinatesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListLanguageCoordinatesResponse(_message.Message):
    __slots__ = ("coordinates", "created_at")
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    coordinates: _containers.RepeatedCompositeFieldContainer[SavedLanguageCoordinateResponse]
    created_at: int
    def __init__(self, coordinates: _Optional[_Iterable[_Union[SavedLanguageCoordinateResponse, _Mapping]]] = ..., created_at: _Optional[int] = ...) -> None: ...

class SemanticsWithCoordinateRequest(_message.Message):
    __slots__ = ("concept_public_id", "stamp_coordinate_id", "navigation_coordinate_id", "language_coordinate_id")
    CONCEPT_PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    STAMP_COORDINATE_ID_FIELD_NUMBER: _ClassVar[int]
    NAVIGATION_COORDINATE_ID_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_COORDINATE_ID_FIELD_NUMBER: _ClassVar[int]
    concept_public_id: _Tinkar_pb2.PublicId
    stamp_coordinate_id: _Tinkar_pb2.PublicId
    navigation_coordinate_id: _Tinkar_pb2.PublicId
    language_coordinate_id: _Tinkar_pb2.PublicId
    def __init__(self, concept_public_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., stamp_coordinate_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., navigation_coordinate_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., language_coordinate_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ...) -> None: ...

class CommitEntitiesRequest(_message.Message):
    __slots__ = ("entities", "transaction_name")
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_NAME_FIELD_NUMBER: _ClassVar[int]
    entities: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.TinkarMsg]
    transaction_name: str
    def __init__(self, entities: _Optional[_Iterable[_Union[_Tinkar_pb2.TinkarMsg, _Mapping]]] = ..., transaction_name: _Optional[str] = ...) -> None: ...

class CommitEntitiesResponse(_message.Message):
    __slots__ = ("success", "error_message", "entities_committed", "commit_time", "created_at")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_COMMITTED_FIELD_NUMBER: _ClassVar[int]
    COMMIT_TIME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    entities_committed: int
    commit_time: int
    created_at: int
    def __init__(self, success: _Optional[bool] = ..., error_message: _Optional[str] = ..., entities_committed: _Optional[int] = ..., commit_time: _Optional[int] = ..., created_at: _Optional[int] = ...) -> None: ...

class ListPatternsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListPatternsResponse(_message.Message):
    __slots__ = ("success", "error_message", "entities", "pattern_count", "created_at")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    PATTERN_COUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    entities: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.TinkarMsg]
    pattern_count: int
    created_at: int
    def __init__(self, success: _Optional[bool] = ..., error_message: _Optional[str] = ..., entities: _Optional[_Iterable[_Union[_Tinkar_pb2.TinkarMsg, _Mapping]]] = ..., pattern_count: _Optional[int] = ..., created_at: _Optional[int] = ...) -> None: ...

class ListPatternMembersRequest(_message.Message):
    __slots__ = ("pattern_id", "offset", "limit", "referenced_component_text", "referenced_component_id")
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    REFERENCED_COMPONENT_TEXT_FIELD_NUMBER: _ClassVar[int]
    REFERENCED_COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    pattern_id: _Tinkar_pb2.PublicId
    offset: int
    limit: int
    referenced_component_text: str
    referenced_component_id: _Tinkar_pb2.PublicId
    def __init__(self, pattern_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ..., offset: _Optional[int] = ..., limit: _Optional[int] = ..., referenced_component_text: _Optional[str] = ..., referenced_component_id: _Optional[_Union[_Tinkar_pb2.PublicId, _Mapping]] = ...) -> None: ...

class ListPatternMembersResponse(_message.Message):
    __slots__ = ("success", "error_message", "total_count", "entities", "member_ids", "has_more", "created_at")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    MEMBER_IDS_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    total_count: int
    entities: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.TinkarMsg]
    member_ids: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    has_more: bool
    created_at: int
    def __init__(self, success: _Optional[bool] = ..., error_message: _Optional[str] = ..., total_count: _Optional[int] = ..., entities: _Optional[_Iterable[_Union[_Tinkar_pb2.TinkarMsg, _Mapping]]] = ..., member_ids: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., has_more: _Optional[bool] = ..., created_at: _Optional[int] = ...) -> None: ...
