"""Shared wire conversion. Unknown or malformed identifiers must never look empty."""
from uuid import UUID

from ._generated import Tinkar_pb2
from .exceptions import TinkarError
from .models import Stamp


def public_ids(value, *, required=True):
    bits = list(value.uuid_bits)
    if len(bits) % 2:
        raise TinkarError("PublicId contains an odd number of UUID words", "protocol_error")
    try:
        packed = [str(UUID(int=(bits[i] << 64) | bits[i + 1]))
                  for i in range(0, len(bits), 2)]
        strings = [str(UUID(item)) for item in value.uuids]
    except (ValueError, TypeError, AttributeError) as error:
        raise TinkarError(f"Invalid PublicId: {error}", "protocol_error") from error
    if packed and strings and set(packed) != set(strings):
        raise TinkarError("Conflicting PublicId UUID representations", "protocol_error")
    result = list(dict.fromkeys(packed or strings))
    if not result and (required or value.HasField("sequence")):
        raise TinkarError(
            "PublicId has no UUIDs; sequence-only references require a component table",
            "protocol_error",
        )
    return result


def public_id(value):
    """Encode a single UUID using the current PublicId message, not old string fields."""
    try:
        identifier = UUID(value)
    except (ValueError, TypeError, AttributeError) as error:
        raise TinkarError(f"Invalid UUID: {value!r}", "invalid_argument") from error
    return Tinkar_pb2.PublicId(uuid_bits=[
        identifier.int >> 64, identifier.int & ((1 << 64) - 1),
    ])


def stamp_from_proto(value):
    return Stamp(
        status=",".join(public_ids(value.status_public_id)),
        author=",".join(public_ids(value.author_public_id)),
        module=",".join(public_ids(value.module_public_id)),
        path=",".join(public_ids(value.path_public_id)),
        time=value.time,
    )
