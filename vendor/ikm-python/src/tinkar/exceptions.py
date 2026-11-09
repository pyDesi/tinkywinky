"""Tinkar client exceptions."""

from __future__ import annotations

import grpc


class TinkarError(Exception):
    """Single exception type for all Tinkar client errors.

    Attributes:
        message: Human-readable error description.
        code: String code identifying the error type (e.g., "unavailable", "timeout").
    """

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def __repr__(self) -> str:
        return f"TinkarError(code={self.code!r}, message={self.message!r})"

    @classmethod
    def from_grpc_error(cls, err: grpc.RpcError) -> TinkarError:
        """Wrap a gRPC error with a readable code."""
        status = err.code()
        code_map = {
            grpc.StatusCode.UNAVAILABLE: "unavailable",
            grpc.StatusCode.DEADLINE_EXCEEDED: "timeout",
            grpc.StatusCode.NOT_FOUND: "not_found",
            grpc.StatusCode.PERMISSION_DENIED: "permission_denied",
            grpc.StatusCode.UNAUTHENTICATED: "unauthenticated",
            grpc.StatusCode.INTERNAL: "server_error",
            grpc.StatusCode.UNIMPLEMENTED: "unimplemented",
        }
        return cls(
            message=err.details() or str(err),
            code=code_map.get(status, status.name.lower()),
        )

    @classmethod
    def from_response(cls, error_message: str) -> TinkarError:
        """Wrap a server-side success=False response."""
        return cls(message=error_message, code="server_error")
