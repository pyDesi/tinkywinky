"""Guard the legacy unary admin API against the server's streaming job protocol."""
from ..exceptions import TinkarError
from ..models import ExportType


class AdminNamespace:
    def __init__(self, stub, timeout):
        self._stub = stub
        self._timeout = timeout

    @staticmethod
    def _streaming_required(operation):
        raise TinkarError(
            f"{operation} now uses streamed job events. The legacy unary admin "
            "wrapper is unsupported; use the current IkeAdmin generated stub "
            "and validate its terminal job result. No request was sent.",
            "unsupported_operation",
        )

    def import_changeset(self, changeset_data, *, use_multi_pass=True, timeout=None):
        self._streaming_required("ImportChangeset")

    def export_entities(self, *, export_type=ExportType.FULL, from_epoch_millis=0,
                        to_epoch_millis=0, membership_tag_ids=None, timeout=None):
        self._streaming_required("ExportEntities")

    def run_reasoner(self, *, timeout=None):
        self._streaming_required("RunReasoner")
