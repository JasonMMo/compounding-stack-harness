"""
tests/test_home.py — L1 unit tests for the /home CTA board buttons.

Covers:
1. /home renders board CTA links for board-enabled entities (generic, via
   board_descriptor) — confirmed with taskflow manifest (task + milestone).
2. /home renders NO cta block when no entity is board-enabled.
3. Hardcoding guard: the string "task" must NOT appear in server.py or
   home.html inside the board_entities computation / CTA template block.
"""

import importlib
import json
import pathlib
import sys
import unittest.mock as mock

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent
_REPO_ROOT = _ADAPTER_ROOT.parent.parent.parent
_TASKFLOW_MANIFEST = _REPO_ROOT / "out" / "taskflow-demo" / "screen-manifest.json"

sys.path.insert(0, str(_ADAPTER_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flask_client_with_manifest(manifest_path: str | None):
    """Return a logged-in Flask test client pointing at the given manifest."""
    import os
    if manifest_path:
        os.environ["PROFILE_MANIFEST"] = manifest_path
    else:
        os.environ.pop("PROFILE_MANIFEST", None)

    os.environ.setdefault("BACKEND_BASE_URL", "http://localhost:19999")

    import manifest_loader as ml_mod
    ml_mod._manifest_loader = None
    importlib.reload(ml_mod)

    import server as srv_mod
    importlib.reload(srv_mod)

    srv_mod.app.config["TESTING"] = True
    srv_mod.app.config["SECRET_KEY"] = "test-secret"

    client = srv_mod.app.test_client()
    with client.session_transaction() as sess:
        sess["token"] = "test-token"
        sess["user_id"] = "testuser"
    return client


# ---------------------------------------------------------------------------
# 1. board CTA links present when manifest has board-enabled entities
# ---------------------------------------------------------------------------

class TestHomeBoardCTA:
    def test_board_link_present_for_board_enabled_entity(self):
        """
        /home must include an <a href="/board/<key>"> for every board-enabled
        entity.  Uses the taskflow-demo manifest which has 'task' and
        'milestone' as board-enabled entities.
        """
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found — run scaffold first")

        client = _flask_client_with_manifest(str(_TASKFLOW_MANIFEST))
        resp = client.get("/home")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")

        # Both board-enabled entities must have a board href
        assert "/board/task" in html
        assert "/board/milestone" in html

    def test_board_button_label_suffix(self):
        """Button label ends with ' 보드' for each board-enabled entity."""
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found — run scaffold first")

        client = _flask_client_with_manifest(str(_TASKFLOW_MANIFEST))
        resp = client.get("/home")
        html = resp.data.decode("utf-8")

        # The template appends ' 보드' to entity.label
        assert "보드" in html

    def test_board_link_uses_btn_primary_class(self):
        """CTA buttons must carry btn-primary styling."""
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found — run scaffold first")

        client = _flask_client_with_manifest(str(_TASKFLOW_MANIFEST))
        resp = client.get("/home")
        html = resp.data.decode("utf-8")

        assert "btn-primary" in html


# ---------------------------------------------------------------------------
# 2. No CTA block when manifest has no board-enabled entities
# ---------------------------------------------------------------------------

class TestHomeBoardCTAEmpty:
    def test_no_cta_when_no_board_entities(self):
        """
        When no entity is board-enabled (board_descriptor returns None for all),
        home-hero__cta div must NOT appear in the rendered HTML.
        """
        import os
        os.environ.pop("PROFILE_MANIFEST", None)

        import manifest_loader as ml_mod
        ml_mod._manifest_loader = None
        importlib.reload(ml_mod)

        import server as srv_mod
        importlib.reload(srv_mod)
        srv_mod.app.config["TESTING"] = True
        srv_mod.app.config["SECRET_KEY"] = "test-secret"

        # Patch the module-level manifest singleton AFTER reload
        empty_loader = ml_mod.ManifestLoader(manifest_path=None)
        srv_mod.manifest = empty_loader

        client = srv_mod.app.test_client()
        with client.session_transaction() as sess:
            sess["token"] = "test-token"
            sess["user_id"] = "testuser"

        resp = client.get("/home")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")

        assert "home-hero__cta" not in html
        assert "/board/" not in html


# ---------------------------------------------------------------------------
# 3. Generic mechanism guard — no hardcoded entity key in server.py / home.html
# ---------------------------------------------------------------------------

class TestNoBoardHardcode:
    def _board_entities_block(self, path: pathlib.Path) -> str:
        """Return only the lines relevant to board_entities in the file."""
        text = path.read_text(encoding="utf-8")
        # Collect lines that contain board_entities or board_ href/route context
        lines = [ln for ln in text.splitlines()
                 if "board_entities" in ln or "entity_board" in ln
                 or "home-hero__cta" in ln]
        return "\n".join(lines)

    def test_server_py_board_entities_no_hardcoded_task(self):
        server_path = _ADAPTER_ROOT / "server.py"
        block = self._board_entities_block(server_path)
        # The block must not contain the literal string 'task' (case-sensitive)
        assert '"task"' not in block
        assert "'task'" not in block

    def test_home_html_cta_no_hardcoded_task(self):
        template_path = _ADAPTER_ROOT / "templates" / "home.html"
        block = self._board_entities_block(template_path)
        assert '"task"' not in block
        assert "'task'" not in block
