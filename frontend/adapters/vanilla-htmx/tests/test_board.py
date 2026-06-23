"""
tests/test_board.py — L1 unit tests for kanban board view (Phase 2).

Covers:
1. manifest_loader.board_descriptor() — board-enabled detection (generic, task, milestone)
2. _validate_status_transition() — state machine guard (task entity)
3. GET /board/<entity_type> — 200 + column rendering + fallback when not board-enabled
4. POST /board/<entity_type>/<id>/move — valid transition, invalid transition (422)
"""

import importlib
import json
import pathlib
import sys
import unittest.mock as mock

import pytest

# ---------------------------------------------------------------------------
# Path setup — adapter root must be importable
# ---------------------------------------------------------------------------

_ADAPTER_ROOT = pathlib.Path(__file__).parent.parent  # …/vanilla-htmx/
_REPO_ROOT = _ADAPTER_ROOT.parent.parent.parent        # …/compounding-stack-harness/
_TASKFLOW_MANIFEST = _REPO_ROOT / "out" / "taskflow-demo" / "screen-manifest.json"

sys.path.insert(0, str(_ADAPTER_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_manifest_loader(path: str | None = None):
    import manifest_loader as ml_mod
    importlib.reload(ml_mod)
    return ml_mod.ManifestLoader(manifest_path=path)


# ---------------------------------------------------------------------------
# 1. board_descriptor() — unit tests (no HTTP, no backend)
# ---------------------------------------------------------------------------

class TestBoardDescriptor:
    def test_no_manifest_returns_none(self, monkeypatch):
        monkeypatch.delenv("PROFILE_MANIFEST", raising=False)
        loader = _make_manifest_loader(path=None)
        assert loader.board_descriptor("task") is None

    def test_task_board_descriptor_present(self):
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found — run scaffold first")
        loader = _make_manifest_loader(str(_TASKFLOW_MANIFEST))
        desc = loader.board_descriptor("task")
        assert desc is not None
        assert desc["group_by"] == "status"
        assert isinstance(desc["columns"], list)
        assert len(desc["columns"]) >= 1
        assert isinstance(desc["card_fields"], list)

    def test_task_columns_order(self):
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found")
        loader = _make_manifest_loader(str(_TASKFLOW_MANIFEST))
        desc = loader.board_descriptor("task")
        # Expect the 5 statuses from the seed in order
        expected = ["todo", "in-progress", "blocked", "done", "cancelled"]
        assert desc["columns"] == expected

    def test_task_card_fields_non_empty(self):
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found")
        loader = _make_manifest_loader(str(_TASKFLOW_MANIFEST))
        desc = loader.board_descriptor("task")
        assert len(desc["card_fields"]) > 0
        # status itself must NOT appear in card_fields
        assert "status" not in desc["card_fields"]

    def test_task_card_fields_max_4(self):
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found")
        loader = _make_manifest_loader(str(_TASKFLOW_MANIFEST))
        desc = loader.board_descriptor("task")
        assert len(desc["card_fields"]) <= 4

    def test_milestone_board_descriptor_present(self):
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found")
        loader = _make_manifest_loader(str(_TASKFLOW_MANIFEST))
        desc = loader.board_descriptor("milestone")
        # milestone also has a status enum field → should be board-enabled
        assert desc is not None
        assert desc["group_by"] == "status"

    def test_department_not_board_enabled(self):
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found")
        loader = _make_manifest_loader(str(_TASKFLOW_MANIFEST))
        # department has no status field
        desc = loader.board_descriptor("department")
        assert desc is None

    def test_absent_entity_returns_none(self):
        if not _TASKFLOW_MANIFEST.is_file():
            pytest.skip("taskflow-demo manifest not found")
        loader = _make_manifest_loader(str(_TASKFLOW_MANIFEST))
        assert loader.board_descriptor("nonexistent-xyz") is None


# ---------------------------------------------------------------------------
# 2. _validate_status_transition() — state machine guard
# ---------------------------------------------------------------------------

class TestStatusMachine:
    @pytest.fixture(autouse=True)
    def _import_fn(self):
        """Import the guard function from server module (reload to avoid singleton)."""
        import server
        importlib.reload(server)
        self._validate = server._validate_status_transition

    def test_todo_to_inprogress_valid(self):
        assert self._validate("task", "todo", "in-progress") is None

    def test_inprogress_to_blocked_valid(self):
        assert self._validate("task", "in-progress", "blocked") is None

    def test_inprogress_to_done_valid(self):
        assert self._validate("task", "in-progress", "done") is None

    def test_blocked_to_inprogress_valid(self):
        assert self._validate("task", "blocked", "in-progress") is None

    def test_todo_to_done_invalid(self):
        """Direct skip: todo → done is forbidden."""
        result = self._validate("task", "todo", "done")
        assert result is not None
        assert "허용" in result or "전이" in result

    def test_todo_to_blocked_invalid(self):
        result = self._validate("task", "todo", "blocked")
        assert result is not None

    def test_done_to_anything_invalid(self):
        """done is a terminal state."""
        result = self._validate("task", "done", "todo")
        assert result is not None
        assert "종료" in result or "불가" in result

    def test_cancelled_terminal(self):
        result = self._validate("task", "cancelled", "todo")
        assert result is not None

    def test_unknown_from_status_returns_error(self):
        result = self._validate("task", "nonexistent", "todo")
        assert result is not None

    def test_no_machine_for_other_entity_allows_any(self):
        """Entities without a registered machine are not guarded."""
        assert self._validate("milestone", "pending", "achieved") is None
        assert self._validate("project", "planning", "completed") is None


# ---------------------------------------------------------------------------
# 3. Flask route tests — GET /board/<entity_type>
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def flask_client():
    """Flask test client with mock backend and taskflow-demo manifest."""
    if not _TASKFLOW_MANIFEST.is_file():
        pytest.skip("taskflow-demo manifest not found — run scaffold first")

    import os
    os.environ["PROFILE_MANIFEST"] = str(_TASKFLOW_MANIFEST)
    os.environ["BACKEND_BASE_URL"] = "http://localhost:19999"  # no real backend needed

    import importlib
    # Reset manifest_loader singleton FIRST, then reload server so module-level
    # `manifest` variable picks up the freshly set PROFILE_MANIFEST env var.
    import manifest_loader as ml_mod
    ml_mod._manifest_loader = None
    importlib.reload(ml_mod)

    import server as srv_mod
    importlib.reload(srv_mod)

    srv_mod.app.config["TESTING"] = True
    srv_mod.app.config["SECRET_KEY"] = "test-secret"

    with srv_mod.app.test_client() as client:
        with client.session_transaction() as sess:
            sess["token"] = "test-token"
            sess["user_id"] = "testuser"
        yield client


def _mock_list_response(items: list[dict]) -> bytes:
    return json.dumps({"items": items, "total": len(items)}).encode()


class TestBoardRoute:
    def test_board_task_200_when_backend_returns_items(self, flask_client, monkeypatch):
        """GET /board/task returns 200 with mock backend returning 3 task items."""
        sample_items = [
            {"id": "t1", "name": "Buy milk", "status": "todo", "priority": "normal"},
            {"id": "t2", "name": "Write tests", "status": "in-progress", "priority": "high"},
            {"id": "t3", "name": "Deploy", "status": "done", "priority": "urgent"},
        ]

        def fake_urlopen(req, timeout=None):
            resp = mock.MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = mock.MagicMock(return_value=False)
            resp.read.return_value = _mock_list_response(sample_items)
            resp.status = 200
            return resp

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        response = flask_client.get("/board/task")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        # Five kanban columns must appear (todo / in-progress / blocked / done / cancelled)
        assert "todo" in html.lower()
        assert "in-progress" in html.lower() or "in progress" in html.lower()
        assert "done" in html.lower()
        assert "칸반 보드" in html

    def test_board_task_renders_card_names(self, flask_client, monkeypatch):
        """Card content (name field) appears in board HTML."""
        sample_items = [
            {"id": "t1", "name": "Fix login bug", "status": "todo", "priority": "high"},
        ]

        def fake_urlopen(req, timeout=None):
            resp = mock.MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = mock.MagicMock(return_value=False)
            resp.read.return_value = _mock_list_response(sample_items)
            resp.status = 200
            return resp

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        response = flask_client.get("/board/task")
        assert response.status_code == 200
        assert b"Fix login bug" in response.data

    def test_board_non_board_entity_404(self, flask_client, monkeypatch):
        """GET /board/department returns 404 (department has no status field)."""
        response = flask_client.get("/board/department")
        assert response.status_code == 404

    def test_list_page_has_board_link_for_task(self, flask_client, monkeypatch):
        """Entity list for task includes '보드 보기' link."""
        sample_items = [
            {"id": "t1", "name": "Task A", "status": "todo", "priority": "normal"},
        ]

        def fake_urlopen(req, timeout=None):
            resp = mock.MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = mock.MagicMock(return_value=False)
            resp.read.return_value = _mock_list_response(sample_items)
            resp.status = 200
            return resp

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        response = flask_client.get("/entities/task")
        assert response.status_code == 200
        assert "보드 보기" in response.data.decode("utf-8")

    def test_list_page_no_board_link_for_department(self, flask_client, monkeypatch):
        """Entity list for department does NOT include '보드 보기' link."""
        sample_items = [{"id": "d1", "name": "Engineering"}]

        def fake_urlopen(req, timeout=None):
            resp = mock.MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = mock.MagicMock(return_value=False)
            resp.read.return_value = _mock_list_response(sample_items)
            resp.status = 200
            return resp

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        response = flask_client.get("/entities/department")
        assert response.status_code == 200
        assert "보드 보기" not in response.data.decode("utf-8")


# ---------------------------------------------------------------------------
# 4. Move endpoint — valid / invalid transitions
# ---------------------------------------------------------------------------

class TestBoardMoveRoute:
    def test_valid_move_redirects(self, flask_client, monkeypatch):
        """POST /board/task/t1/move with valid transition (todo→in-progress) → redirect."""
        def fake_urlopen(req, timeout=None):
            resp = mock.MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = mock.MagicMock(return_value=False)
            resp.read.return_value = json.dumps({"success": True, "data": {}}).encode()
            resp.status = 200
            return resp

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        response = flask_client.post(
            "/board/task/t1/move",
            data={"from_status": "todo", "to_status": "in-progress"},
        )
        # Should redirect to /board/task
        assert response.status_code in (302, 303)
        assert "/board/task" in response.headers.get("Location", "")

    def test_invalid_move_returns_422(self, flask_client, monkeypatch):
        """POST /board/task/t1/move with skip transition (todo→done) → 422."""
        response = flask_client.post(
            "/board/task/t1/move",
            data={"from_status": "todo", "to_status": "done"},
        )
        assert response.status_code == 422
        assert "전이" in response.data.decode("utf-8") or "허용" in response.data.decode("utf-8")

    def test_terminal_state_move_returns_422(self, flask_client, monkeypatch):
        """POST /board/task/t1/move from terminal 'done' → 422."""
        response = flask_client.post(
            "/board/task/t1/move",
            data={"from_status": "done", "to_status": "todo"},
        )
        assert response.status_code == 422
