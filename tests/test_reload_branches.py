import json

import asu.util
from asu.config import settings
from asu.util import reload_branches


def test_reload_branches_noop_when_url_empty():
    """reload_branches does nothing when branches_url is empty."""
    saved = settings.branches_url
    settings.branches_url = ""
    original_branches = dict(settings.branches)

    reload_branches()

    assert settings.branches == original_branches
    settings.branches_url = saved


def test_reload_branches_merges_fetched_branches():
    """reload_branches fetches and merges remote branches into settings."""
    fetched = {
        "test-branch-1": {
            "enabled": True,
            "snapshot": True,
            "path": "releases/{version}",
            "path_packages": "DEPRECATED",
            "package_changes": [],
            "targets": {"mediatek/filogic": "test-SNAPSHOT"},
        }
    }

    class FakeResponse:
        status_code = 200

        def json(self):
            return fetched

    saved_url = settings.branches_url
    saved_client = asu.util.client_get

    settings.branches_url = "http://example.com/branches.json"
    asu.util.client_get = lambda url: FakeResponse()

    try:
        assert "test-branch-1" not in settings.branches
        reload_branches()
        assert "test-branch-1" in settings.branches
        assert settings.branches["test-branch-1"]["snapshot"] is True
    finally:
        settings.branches.pop("test-branch-1", None)
        settings.branches_url = saved_url
        asu.util.client_get = saved_client


def test_reload_branches_handles_non_200():
    """reload_branches logs warning and returns on non-200 response."""

    class FakeResponse:
        status_code = 500

        def json(self):
            return {}

    saved_url = settings.branches_url
    saved_client = asu.util.client_get

    settings.branches_url = "http://example.com/branches.json"
    asu.util.client_get = lambda url: FakeResponse()

    original_branches = dict(settings.branches)

    try:
        reload_branches()
        # Branches should be unchanged
        assert settings.branches == original_branches
    finally:
        settings.branches_url = saved_url
        asu.util.client_get = saved_client


def test_reload_branches_handles_fetch_exception():
    """reload_branches handles exceptions from the HTTP client gracefully."""
    saved_url = settings.branches_url
    saved_client = asu.util.client_get

    settings.branches_url = "http://example.com/branches.json"

    def raise_error(url):
        raise ConnectionError("network down")

    asu.util.client_get = raise_error

    original_branches = dict(settings.branches)

    try:
        reload_branches()
        assert settings.branches == original_branches
    finally:
        settings.branches_url = saved_url
        asu.util.client_get = saved_client


def test_reload_branches_handles_invalid_json():
    """reload_branches handles invalid JSON responses gracefully."""

    class FakeResponse:
        status_code = 200

        def json(self):
            raise json.JSONDecodeError("bad json", "", 0)

    saved_url = settings.branches_url
    saved_client = asu.util.client_get

    settings.branches_url = "http://example.com/branches.json"
    asu.util.client_get = lambda url: FakeResponse()

    original_branches = dict(settings.branches)

    try:
        reload_branches()
        assert settings.branches == original_branches
    finally:
        settings.branches_url = saved_url
        asu.util.client_get = saved_client
