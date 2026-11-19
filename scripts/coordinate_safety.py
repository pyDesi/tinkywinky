"""Collection audit only, not permission to run upstream tests on the current store.

Use as a pytest plugin on disposable stores. The smoke RPC allowlist is the
current-store boundary and is intentionally not changed here.
"""
import ast
import inspect
import textwrap

import pytest

SAVE_METHODS = {
    "save_stamp_coordinate", "save_navigation_coordinate", "save_language_coordinate",
}


def has_coordinate_write(source):
    return any(
        isinstance(node, ast.Attribute) and node.attr in SAVE_METHODS
        for node in ast.walk(ast.parse(textwrap.dedent(source)))
    )


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    for item in items:
        if has_coordinate_write(inspect.getsource(item.obj)):
            if item.get_closest_marker("integration_destructive") is None:
                raise pytest.UsageError(
                    f"Unmarked coordinate write: {item.nodeid}; "
                    "add integration_destructive before running this suite"
                )
