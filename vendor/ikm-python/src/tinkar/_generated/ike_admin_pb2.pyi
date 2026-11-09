import Tinkar_pb2 as _Tinkar_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FULL: _ClassVar[ExportType]
    TEMPORAL: _ClassVar[ExportType]
    MEMBERSHIP: _ClassVar[ExportType]

class JobKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_KIND_UNSPECIFIED: _ClassVar[JobKind]
    REASONER: _ClassVar[JobKind]
    IMPORT: _ClassVar[JobKind]
    EXPORT: _ClassVar[JobKind]

class JobState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_STATE_UNSPECIFIED: _ClassVar[JobState]
    QUEUED: _ClassVar[JobState]
    RUNNING: _ClassVar[JobState]
    SUCCEEDED: _ClassVar[JobState]
    FAILED: _ClassVar[JobState]
    CANCELLED: _ClassVar[JobState]
FULL: ExportType
TEMPORAL: ExportType
MEMBERSHIP: ExportType
JOB_KIND_UNSPECIFIED: JobKind
REASONER: JobKind
IMPORT: JobKind
EXPORT: JobKind
JOB_STATE_UNSPECIFIED: JobState
QUEUED: JobState
RUNNING: JobState
SUCCEEDED: JobState
FAILED: JobState
CANCELLED: JobState

class ImportChangesetChunk(_message.Message):
    __slots__ = ("start", "data")
    START_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    start: ImportChangesetStart
    data: bytes
    def __init__(self, start: _Optional[_Union[ImportChangesetStart, _Mapping]] = ..., data: _Optional[bytes] = ...) -> None: ...

class ImportChangesetStart(_message.Message):
    __slots__ = ("file_name", "single_pass")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    SINGLE_PASS_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    single_pass: bool
    def __init__(self, file_name: _Optional[str] = ..., single_pass: _Optional[bool] = ...) -> None: ...

class EntityCountSummaryProto(_message.Message):
    __slots__ = ("concepts_count", "semantics_count", "patterns_count", "stamps_count", "total_count")
    CONCEPTS_COUNT_FIELD_NUMBER: _ClassVar[int]
    SEMANTICS_COUNT_FIELD_NUMBER: _ClassVar[int]
    PATTERNS_COUNT_FIELD_NUMBER: _ClassVar[int]
    STAMPS_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    concepts_count: int
    semantics_count: int
    patterns_count: int
    stamps_count: int
    total_count: int
    def __init__(self, concepts_count: _Optional[int] = ..., semantics_count: _Optional[int] = ..., patterns_count: _Optional[int] = ..., stamps_count: _Optional[int] = ..., total_count: _Optional[int] = ...) -> None: ...

class ExportEntitiesRequest(_message.Message):
    __slots__ = ("export_type", "from_epoch_millis", "to_epoch_millis", "membership_tags")
    EXPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FROM_EPOCH_MILLIS_FIELD_NUMBER: _ClassVar[int]
    TO_EPOCH_MILLIS_FIELD_NUMBER: _ClassVar[int]
    MEMBERSHIP_TAGS_FIELD_NUMBER: _ClassVar[int]
    export_type: ExportType
    from_epoch_millis: int
    to_epoch_millis: int
    membership_tags: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    def __init__(self, export_type: _Optional[_Union[ExportType, str]] = ..., from_epoch_millis: _Optional[int] = ..., to_epoch_millis: _Optional[int] = ..., membership_tags: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ...) -> None: ...

class JobInfo(_message.Message):
    __slots__ = ("job_id", "kind", "label", "state", "queued_at", "started_at")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    QUEUED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    kind: JobKind
    label: str
    state: JobState
    queued_at: int
    started_at: int
    def __init__(self, job_id: _Optional[str] = ..., kind: _Optional[_Union[JobKind, str]] = ..., label: _Optional[str] = ..., state: _Optional[_Union[JobState, str]] = ..., queued_at: _Optional[int] = ..., started_at: _Optional[int] = ...) -> None: ...

class JobProgress(_message.Message):
    __slots__ = ("done", "total", "message")
    DONE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    done: int
    total: int
    message: str
    def __init__(self, done: _Optional[int] = ..., total: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class JobResult(_message.Message):
    __slots__ = ("job_id", "success", "cancelled", "error_message", "entity_counts", "duration_ms", "file_name", "file_size_bytes")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_COUNTS_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    success: bool
    cancelled: bool
    error_message: str
    entity_counts: EntityCountSummaryProto
    duration_ms: int
    file_name: str
    file_size_bytes: int
    def __init__(self, job_id: _Optional[str] = ..., success: _Optional[bool] = ..., cancelled: _Optional[bool] = ..., error_message: _Optional[str] = ..., entity_counts: _Optional[_Union[EntityCountSummaryProto, _Mapping]] = ..., duration_ms: _Optional[int] = ..., file_name: _Optional[str] = ..., file_size_bytes: _Optional[int] = ...) -> None: ...

class JobQueuePosition(_message.Message):
    __slots__ = ("ahead",)
    AHEAD_FIELD_NUMBER: _ClassVar[int]
    ahead: _containers.RepeatedCompositeFieldContainer[JobInfo]
    def __init__(self, ahead: _Optional[_Iterable[_Union[JobInfo, _Mapping]]] = ...) -> None: ...

class JobEvent(_message.Message):
    __slots__ = ("job", "queued", "started_at", "progress", "result", "file_chunk")
    JOB_FIELD_NUMBER: _ClassVar[int]
    QUEUED_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    FILE_CHUNK_FIELD_NUMBER: _ClassVar[int]
    job: JobInfo
    queued: JobQueuePosition
    started_at: int
    progress: JobProgress
    result: JobResult
    file_chunk: bytes
    def __init__(self, job: _Optional[_Union[JobInfo, _Mapping]] = ..., queued: _Optional[_Union[JobQueuePosition, _Mapping]] = ..., started_at: _Optional[int] = ..., progress: _Optional[_Union[JobProgress, _Mapping]] = ..., result: _Optional[_Union[JobResult, _Mapping]] = ..., file_chunk: _Optional[bytes] = ...) -> None: ...

class WatchJobRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class CancelJobRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class CancelJobResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RunReasonerRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReasonerResultsProto(_message.Message):
    __slots__ = ("classified_concept_count", "inferred_changes_count", "navigation_changes_count", "equivalent_sets_count", "cycles_count", "orphans_count")
    CLASSIFIED_CONCEPT_COUNT_FIELD_NUMBER: _ClassVar[int]
    INFERRED_CHANGES_COUNT_FIELD_NUMBER: _ClassVar[int]
    NAVIGATION_CHANGES_COUNT_FIELD_NUMBER: _ClassVar[int]
    EQUIVALENT_SETS_COUNT_FIELD_NUMBER: _ClassVar[int]
    CYCLES_COUNT_FIELD_NUMBER: _ClassVar[int]
    ORPHANS_COUNT_FIELD_NUMBER: _ClassVar[int]
    classified_concept_count: int
    inferred_changes_count: int
    navigation_changes_count: int
    equivalent_sets_count: int
    cycles_count: int
    orphans_count: int
    def __init__(self, classified_concept_count: _Optional[int] = ..., inferred_changes_count: _Optional[int] = ..., navigation_changes_count: _Optional[int] = ..., equivalent_sets_count: _Optional[int] = ..., cycles_count: _Optional[int] = ..., orphans_count: _Optional[int] = ...) -> None: ...

class EquivalentSet(_message.Message):
    __slots__ = ("concept",)
    CONCEPT_FIELD_NUMBER: _ClassVar[int]
    concept: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    def __init__(self, concept: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ...) -> None: ...

class ReasonerPhase(_message.Message):
    __slots__ = ("step", "total_steps", "message")
    STEP_FIELD_NUMBER: _ClassVar[int]
    TOTAL_STEPS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    step: int
    total_steps: int
    message: str
    def __init__(self, step: _Optional[int] = ..., total_steps: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class RunReasonerResult(_message.Message):
    __slots__ = ("success", "error_message", "counts", "duration_ms", "created_at", "concepts_with_inferred_changes", "concepts_with_navigation_changes", "orphans", "equivalent_sets", "commit_time", "stamp_coordinate_text", "logic_coordinate_text", "edit_coordinate_text", "cancelled")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COUNTS_FIELD_NUMBER: _ClassVar[int]
    DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CONCEPTS_WITH_INFERRED_CHANGES_FIELD_NUMBER: _ClassVar[int]
    CONCEPTS_WITH_NAVIGATION_CHANGES_FIELD_NUMBER: _ClassVar[int]
    ORPHANS_FIELD_NUMBER: _ClassVar[int]
    EQUIVALENT_SETS_FIELD_NUMBER: _ClassVar[int]
    COMMIT_TIME_FIELD_NUMBER: _ClassVar[int]
    STAMP_COORDINATE_TEXT_FIELD_NUMBER: _ClassVar[int]
    LOGIC_COORDINATE_TEXT_FIELD_NUMBER: _ClassVar[int]
    EDIT_COORDINATE_TEXT_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    counts: ReasonerResultsProto
    duration_ms: int
    created_at: int
    concepts_with_inferred_changes: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    concepts_with_navigation_changes: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    orphans: _containers.RepeatedCompositeFieldContainer[_Tinkar_pb2.PublicId]
    equivalent_sets: _containers.RepeatedCompositeFieldContainer[EquivalentSet]
    commit_time: int
    stamp_coordinate_text: str
    logic_coordinate_text: str
    edit_coordinate_text: str
    cancelled: bool
    def __init__(self, success: _Optional[bool] = ..., error_message: _Optional[str] = ..., counts: _Optional[_Union[ReasonerResultsProto, _Mapping]] = ..., duration_ms: _Optional[int] = ..., created_at: _Optional[int] = ..., concepts_with_inferred_changes: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., concepts_with_navigation_changes: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., orphans: _Optional[_Iterable[_Union[_Tinkar_pb2.PublicId, _Mapping]]] = ..., equivalent_sets: _Optional[_Iterable[_Union[EquivalentSet, _Mapping]]] = ..., commit_time: _Optional[int] = ..., stamp_coordinate_text: _Optional[str] = ..., logic_coordinate_text: _Optional[str] = ..., edit_coordinate_text: _Optional[str] = ..., cancelled: _Optional[bool] = ...) -> None: ...

class ReasonerRunInfo(_message.Message):
    __slots__ = ("started_at", "started")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    started_at: int
    started: bool
    def __init__(self, started_at: _Optional[int] = ..., started: _Optional[bool] = ...) -> None: ...

class RunReasonerEvent(_message.Message):
    __slots__ = ("phase", "result", "run")
    PHASE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    RUN_FIELD_NUMBER: _ClassVar[int]
    phase: ReasonerPhase
    result: RunReasonerResult
    run: ReasonerRunInfo
    def __init__(self, phase: _Optional[_Union[ReasonerPhase, _Mapping]] = ..., result: _Optional[_Union[RunReasonerResult, _Mapping]] = ..., run: _Optional[_Union[ReasonerRunInfo, _Mapping]] = ...) -> None: ...

class WatchReasonerRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CancelReasonerRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CancelReasonerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
