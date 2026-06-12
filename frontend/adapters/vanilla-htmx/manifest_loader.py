"""
manifest_loader.py — reads out/<profile>/screen-manifest.json at runtime.

Mirrors contract_loader.py style. Resolution: PROFILE_MANIFEST env var
(absolute path to a screen-manifest.json). If unset OR file missing the
loader returns "no manifest" state so the frontend falls back to the
existing generic key/value rendering (backward compat — Growth-12).

G-1 note: this loader is render-only. It does NOT re-derive classification
logic from catalog — it reads the manifest that manifest.py already produced.
Field logic lives in scripts/workflow/manifest.py (single source).

Optional field notes:
  max_length  — present only on text controls where catalog sets a length.
                Absent means no limit (do not impose one at the UI layer).
  unique      — present and true when catalog column sets unique: true.
                Absent means not unique.
"""

import json
import logging
import os
import pathlib
from typing import Any

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ManifestLoader
# ---------------------------------------------------------------------------

class ManifestLoader:
    """
    Loads screen-manifest.json from the path given by PROFILE_MANIFEST.

    If the env var is unset or the file is absent, all query methods
    return None — callers treat None as "no manifest, use fallback".
    """

    def __init__(self, manifest_path: str | None = None) -> None:
        """
        Args:
            manifest_path: explicit path (used in tests). If None, read
                           PROFILE_MANIFEST env var. If that is also unset
                           or the file is missing, operate in no-manifest mode.
        """
        path_str = manifest_path or os.environ.get("PROFILE_MANIFEST", "")

        self._entities: dict[str, Any] = {}
        self._profile: str = ""
        self._loaded: bool = False
        self._customer_display: str = ""
        self._domains: list[dict[str, Any]] = []
        self._feedback_url: str = ""

        if not path_str:
            log.info(
                "ManifestLoader: PROFILE_MANIFEST not set — fallback (generic) rendering active."
            )
            return

        p = pathlib.Path(path_str)
        if not p.is_file():
            log.warning(
                "ManifestLoader: PROFILE_MANIFEST='%s' not found — fallback rendering active.",
                path_str,
            )
            return

        try:
            with p.open("r", encoding="utf-8") as fh:
                doc: dict[str, Any] = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            log.error("ManifestLoader: failed to parse '%s': %s", path_str, exc)
            return

        self._entities = doc.get("entities", {})
        self._profile = doc.get("profile", "")
        self._customer_display = doc.get("customer_display", "")
        self._domains = doc.get("domains", [])
        self._feedback_url = doc.get("feedback_url", "")
        self._loaded = True
        log.info(
            "ManifestLoader: loaded profile='%s', %d entities from '%s'",
            self._profile,
            len(self._entities),
            path_str,
        )

    # ── public helpers ────────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        """True when a valid manifest was successfully loaded."""
        return self._loaded

    def profile(self) -> str:
        """Profile slug from the manifest (e.g. 'shop-demo')."""
        return self._profile

    def entity_keys(self) -> list[str]:
        """All entity keys present in the manifest."""
        return list(self._entities.keys())

    def customer_display(self) -> str:
        """Human-readable customer name from profile.customer.display.

        Returns an empty string when the manifest is not loaded or the field
        is absent (caller should fall back to generic heading).
        """
        return self._customer_display

    def domains(self) -> list[dict[str, Any]]:
        """Domain card list from the manifest.

        Each entry: {slug: str, display: str,
                     entities: [{key: str, label: str}, ...]}.
        The ``label`` on each entity item carries the resolved 3-tier label
        (profile entity_labels > catalog label_ko(ko) > English title-case)
        so templates can render it directly without re-deriving it.
        Returns an empty list when the manifest is not loaded or no domains
        are present (caller renders nothing).
        """
        return list(self._domains)

    def feedback_url(self) -> str:
        """Optional feedback CTA URL from profile.overlay.feedback_url.

        Returns an empty string when absent — caller must check truthiness
        before rendering the link.
        """
        return self._feedback_url

    def label(self, entity_type: str) -> str | None:
        """
        Human-readable label for an entity (e.g. 'Sales Order').
        Returns None when the entity is absent or manifest not loaded.
        """
        entry = self._entities.get(entity_type)
        if entry is None:
            return None
        return entry.get("label")

    def entity_fields(self, entity_type: str) -> list[dict[str, Any]] | None:
        """
        Return the typed field list for an entity.

        Each dict has at minimum: name, type, required, label, control.
        Optional keys (may be absent): options, fk_entity, note, max_length, unique.
        Callers must handle absent optional keys without error.

        Returns None when:
          - manifest not loaded (PROFILE_MANIFEST unset / file missing), OR
          - entity_type is not present in the manifest.
        Both cases mean "use fallback generic rendering".
        """
        if not self._loaded:
            return None
        entry = self._entities.get(entity_type)
        if entry is None:
            return None
        return entry.get("fields") or None

    def hidden_fields(self, entity_type: str) -> list[str]:
        """
        Return the list of hidden field names for an entity.
        Returns an empty list when entity absent or manifest not loaded.
        Hidden fields are NOT rendered as form inputs on create;
        on detail they may be shown read-only.
        """
        if not self._loaded:
            return []
        entry = self._entities.get(entity_type)
        if entry is None:
            return []
        return entry.get("hidden_fields", [])


# ---------------------------------------------------------------------------
# Singleton — imported by server.py at startup
# ---------------------------------------------------------------------------

_manifest_loader: ManifestLoader | None = None


def get_manifest_loader() -> ManifestLoader:
    global _manifest_loader
    if _manifest_loader is None:
        _manifest_loader = ManifestLoader()
    return _manifest_loader
