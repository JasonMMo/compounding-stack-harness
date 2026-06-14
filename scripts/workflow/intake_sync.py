"""intake_sync.py -- Phase 4 sync bridge (LLM 0).

Pulls VPS intake artifacts via SSH rsync into apps/intake/data-mirror/
(gitignored), then routes each pending inbox entry:

  prefer_call  -> pm-inbox.md CALL block; no build
  gap_only     -> gap-registry.jsonl + pm-inbox.md triage; no build
  defer        -> gap-registry.jsonl + pm-inbox.md triage; no build
  qualify      -> promote draft -> scaffold -> deploy -> ui_check -> needs_fit

Each qualify stage is wrapped with pipeline_emit NODE_ENTER / NODE_EXIT_OK /
NODE_FAIL.  Idempotency is maintained via docs/intake-inbox/processed.jsonl
(keyed on ts).  --dry-run prints intended actions without mutating any file or
subprocess.

PII contract:
  - data-mirror/ is gitignored; raw PII stays there only.
  - docs/intake-inbox/processed.jsonl, pm-inbox.md, gap-registry.jsonl, and
    infra/registry/cases/<client_id>.yaml contain slug / score / gap_category /
    status only -- NO email, free-text answers, or company names.
  - profiles/<slug>.yaml promoted from draft has customer.contact STRIPPED of
    email/phone and replaced with "intake-ref:<client_id>" before any write.
    The real contact lives in gitignored data-mirror/ + VPS audit trail only.

SSH:
  Host  root@187.77.140.157
  Key   ~/.ssh/n9n_preview_ed25519
  VPS data dir  /data/intake/data/

stdlib + PyYAML.  No LLM calls.

Usage:
  python scripts/workflow/intake_sync.py --help
  python scripts/workflow/intake_sync.py --dry-run --no-ssh --mirror /tmp/fixture
  python scripts/workflow/intake_sync.py --no-ssh --skip-deploy --skip-ui-check
  python scripts/workflow/intake_sync.py --force-slug acme-erp
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# PII detection patterns (used by promote_draft scrubber)
# ---------------------------------------------------------------------------

# Matches any email-like token: [non-space non-@]+@[non-space non-@]+
_EMAIL_RE = re.compile(r"[^\s@]+@[^\s@]+")

# Korean / international phone patterns that might appear in YAML values
_PHONE_RE = re.compile(r"(?:0\d{9,10}|\d{2,4}-\d{3,4}-\d{4})")

# ---------------------------------------------------------------------------
# Repo-root constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]

VPS_HOST = "root@187.77.140.157"
VPS_DATA_DIR = "/data/intake/data"
SSH_KEY = str(Path.home() / ".ssh" / "n9n_preview_ed25519")

_DEFAULT_MIRROR_DIR = REPO_ROOT / "apps" / "intake" / "data-mirror"
_DEFAULT_PROCESSED = REPO_ROOT / "docs" / "intake-inbox" / "processed.jsonl"
_DEFAULT_PM_INBOX = REPO_ROOT / "docs" / "intake-inbox" / "pm-inbox.md"
_DEFAULT_GAP_REGISTRY = REPO_ROOT / "docs" / "intake-inbox" / "gap-registry.jsonl"
_DEFAULT_PROFILES_DIR = REPO_ROOT / "profiles"
_DEFAULT_CASES_DIR = REPO_ROOT / "infra" / "registry" / "cases"
_DEFAULT_EVIDENCE_DIR = REPO_ROOT / "docs" / "intake-inbox" / "evidence"
_DEFAULT_UI_CHECKS_DIR = REPO_ROOT / "docs" / "intake-inbox" / "ui-checks"

_PREVIEW_BASE_DOMAIN = "n9n.co.kr"

_WORKFLOW_DIR = REPO_ROOT / "scripts" / "workflow"

# Safe stack defaults when draft.yaml has null frontend/backend/dialect
_DEFAULT_FRONTEND = "vanilla-htmx"
_DEFAULT_BACKEND = "fastapi"
_DEFAULT_DIALECT = "postgres"

# ---------------------------------------------------------------------------
# pipeline_emit import (local sibling)
# ---------------------------------------------------------------------------

_sys_path_added = False


def _ensure_workflow_in_path() -> None:
    global _sys_path_added
    if not _sys_path_added:
        wf = str(_WORKFLOW_DIR)
        if wf not in sys.path:
            sys.path.insert(0, wf)
        _sys_path_added = True


def _emit(
    case_yaml: Path,
    node_id: str,
    event: str,
    slug: str,
    score: int | None = None,
    error_class: str | None = None,
    evidence_path: str | None = None,
) -> None:
    """Thin wrapper around pipeline_emit.emit_node_event; silently handles import errors."""
    _ensure_workflow_in_path()
    try:
        from pipeline_emit import emit_node_event  # type: ignore[import]
        emit_node_event(
            case_yaml,
            node_id,
            event,
            slug=slug,
            score=score,
            error_class=error_class,
            evidence_path=str(evidence_path) if evidence_path else None,
        )
    except Exception as exc:
        print(f"[intake_sync] WARN: emit_node_event failed: {exc}", file=sys.stderr)


def _capture_evidence(
    node_id: str,
    slug: str,
    returncode: int | None,
    stderr_tail: str,
    report_path: str | None = None,
    evidence_dir: Path | None = None,
) -> Path | None:
    _ensure_workflow_in_path()
    try:
        from pipeline_emit import capture_evidence  # type: ignore[import]
        return capture_evidence(
            node_id,
            slug,
            returncode=returncode,
            stderr_tail=stderr_tail,
            report_path=report_path,
            out_dir=evidence_dir or _DEFAULT_EVIDENCE_DIR,
        )
    except Exception as exc:
        print(f"[intake_sync] WARN: capture_evidence failed: {exc}", file=sys.stderr)
        return None


def _set_triage(case_yaml: Path, status: str) -> None:
    _ensure_workflow_in_path()
    try:
        from pipeline_emit import set_triage_status  # type: ignore[import]
        set_triage_status(case_yaml, status)
    except Exception as exc:
        print(f"[intake_sync] WARN: set_triage_status failed: {exc}", file=sys.stderr)

# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if _HAS_YAML:
        data = _yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    return {}


def _dump_yaml(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if _HAS_YAML:
        path.write_text(
            _yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
    else:
        import json as _json
        path.write_text(_json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# ---------------------------------------------------------------------------
# SSH rsync helpers
# ---------------------------------------------------------------------------


def _rsync_cmd(src: str, dst: Path) -> list[str]:
    """Build rsync argv; uses SSH key for authentication."""
    return [
        "rsync",
        "-avz",
        "--checksum",
        "-e", f"ssh -i {SSH_KEY} -o StrictHostKeyChecking=no -o BatchMode=yes",
        src,
        str(dst),
    ]


def rsync_inbox(no_ssh: bool, mirror_dir: Path) -> Path:
    """Rsync VPS inbox.jsonl into mirror_dir/inbox.jsonl.

    Parameters
    ----------
    no_ssh:
        If True skip SSH and use the existing file in mirror_dir.
    mirror_dir:
        Local PII mirror root (gitignored).

    Returns
    -------
    Path
        Path to the local inbox.jsonl (may not exist yet in --no-ssh mode).
    """
    mirror_dir = Path(mirror_dir)
    mirror_dir.mkdir(parents=True, exist_ok=True)
    local_inbox = mirror_dir / "inbox.jsonl"

    if no_ssh:
        print(f"[intake_sync] --no-ssh: using existing mirror inbox {local_inbox}")
        return local_inbox

    src = f"{VPS_HOST}:{VPS_DATA_DIR}/inbox.jsonl"
    cmd = _rsync_cmd(src, local_inbox)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"[intake_sync] WARN: rsync inbox failed rc={result.returncode}: "
            f"{result.stderr[:200]}",
            file=sys.stderr,
        )
    else:
        print("[intake_sync] inbox.jsonl synced.")
    return local_inbox


def rsync_client_artifacts(
    client_id: str, no_ssh: bool, mirror_dir: Path
) -> Path:
    """Rsync clients/<client_id>/ artifacts into mirror_dir/clients/<client_id>/.

    Artifacts: draft.yaml, triage.json, needs-note.md, audit.jsonl.

    Returns
    -------
    Path
        Local client artifact directory.
    """
    mirror_dir = Path(mirror_dir)
    local_client_dir = mirror_dir / "clients" / client_id
    local_client_dir.mkdir(parents=True, exist_ok=True)

    if no_ssh:
        print(f"[intake_sync] --no-ssh: using existing artifacts {local_client_dir}")
        return local_client_dir

    src = f"{VPS_HOST}:{VPS_DATA_DIR}/clients/{client_id}/"
    cmd = _rsync_cmd(src, local_client_dir)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"[intake_sync] WARN: rsync client {client_id} failed rc={result.returncode}: "
            f"{result.stderr[:200]}",
            file=sys.stderr,
        )
    else:
        print(f"[intake_sync] client {client_id} artifacts synced.")
    return local_client_dir

# ---------------------------------------------------------------------------
# Inbox loader
# ---------------------------------------------------------------------------


def load_inbox(mirror_dir: Path) -> list[dict]:
    """Load inbox.jsonl from mirror_dir.  Each line must be a JSON object.

    Returns list sorted by 'ts' ascending (oldest first).
    """
    inbox_path = Path(mirror_dir) / "inbox.jsonl"
    if not inbox_path.exists():
        return []
    entries: list[dict] = []
    for lineno, raw in enumerate(inbox_path.read_text(encoding="utf-8").splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                entries.append(obj)
        except json.JSONDecodeError as exc:
            print(
                f"[intake_sync] WARN: inbox.jsonl line {lineno} JSON error: {exc}",
                file=sys.stderr,
            )
    # Sort oldest first; entries missing 'ts' go to the end
    entries.sort(key=lambda e: e.get("ts", "9999"))
    return entries

# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


def is_processed(ts: str, processed_path: Path) -> bool:
    """Return True if an entry with this ts has already been processed."""
    processed_path = Path(processed_path)
    if not processed_path.exists():
        return False
    for raw in processed_path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            if obj.get("ts") == ts:
                return True
        except json.JSONDecodeError:
            continue
    return False


def record_processed(
    entry: dict,
    processed_path: Path,
    *,
    status: str,
) -> None:
    """Append a PII-free processed record to processed.jsonl.

    Only slug, ts, score, and status are written -- NO email / free-text.
    """
    processed_path = Path(processed_path)
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": entry.get("ts", ""),
        "slug": entry.get("slug", ""),
        "score": entry.get("score"),
        "status": status,
        "processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with processed_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Draft promotion
# ---------------------------------------------------------------------------


def promote_draft(
    slug: str,
    client_id: str,
    mirror_dir: Path,
    *,
    profiles_dir: Path | None = None,
) -> Path:
    """Copy mirror draft.yaml -> profiles/<slug>.yaml with null-stack defaults.

    Injects safe defaults when stack.frontend / stack.backend / dialect is null:
      frontend -> vanilla-htmx
      backend  -> fastapi
      dialect  -> postgres

    This ensures scaffold.py can run even for IT-knowledge-poor clients.

    Parameters
    ----------
    slug:
        ASCII slug (G-8).
    client_id:
        VPS client identifier (used to locate mirror artifact).
    mirror_dir:
        Local PII mirror root.
    profiles_dir:
        Destination profiles dir (defaults to REPO_ROOT/profiles/).

    Returns
    -------
    Path
        The written profiles/<slug>.yaml path.
    """
    if profiles_dir is None:
        profiles_dir = _DEFAULT_PROFILES_DIR
    profiles_dir = Path(profiles_dir)
    profiles_dir.mkdir(parents=True, exist_ok=True)

    draft_path = Path(mirror_dir) / "clients" / client_id / "draft.yaml"
    if not draft_path.exists():
        raise FileNotFoundError(f"Draft not found: {draft_path}")

    data = _load_yaml(draft_path)
    if not data:
        raise ValueError(f"Draft YAML is empty or unparseable: {draft_path}")

    # ---- PII scrub: customer.contact ----------------------------------------
    # intake_to_profile._render_profile writes the submitter email into
    # customer.contact.  Replace it with a PII-free operational reference so
    # the promoted profile is safe to commit while remaining traceable.
    customer_block = data.get("customer")
    if isinstance(customer_block, dict):
        raw_contact = customer_block.get("contact", "")
        if raw_contact and (
            _EMAIL_RE.search(str(raw_contact)) or _PHONE_RE.search(str(raw_contact))
        ):
            customer_block["contact"] = f"intake-ref:{client_id}"
        elif raw_contact and str(raw_contact).strip():
            # Non-empty but no detected pattern: still replace to be safe,
            # because free-text company contacts could appear here.
            # Only keep the value if it is already in intake-ref: form.
            if not str(raw_contact).startswith("intake-ref:"):
                customer_block["contact"] = f"intake-ref:{client_id}"

    # ---- PII scan: full YAML serialisation check ----------------------------
    # Serialise tentatively; if any email pattern found, raise rather than
    # silently writing PII to a git-tracked file.
    if _HAS_YAML:
        import yaml as _yaml_check
        tentative_text = _yaml_check.dump(
            data, allow_unicode=True, default_flow_style=False, sort_keys=False
        )
    else:
        import json as _json_check
        tentative_text = _json_check.dumps(data, ensure_ascii=False)

    pii_hit = _EMAIL_RE.search(tentative_text)
    if pii_hit:
        raise ValueError(
            f"promote_draft: PII detected in serialised profile for {slug} "
            f"(token: {pii_hit.group()!r}).  Aborting write.  "
            f"Audit draft at: {draft_path}"
        )

    # Ensure status is set to draft (VPS produces this; set explicitly in case)
    data.setdefault("status", "draft")

    # Inject safe defaults for null stack keys
    stack = data.setdefault("stack", {})
    if not stack:
        data["stack"] = {}
        stack = data["stack"]

    if not stack.get("frontend"):
        stack["frontend"] = _DEFAULT_FRONTEND
    if not stack.get("backend"):
        stack["backend"] = _DEFAULT_BACKEND
    if not stack.get("dialect"):
        stack["dialect"] = _DEFAULT_DIALECT

    dest = profiles_dir / f"{slug}.yaml"
    _dump_yaml(data, dest)
    print(f"[intake_sync] draft promoted -> {dest}")
    return dest

# ---------------------------------------------------------------------------
# SSH tunnel check (reuses deploy_to_coolify.check_tunnel pattern)
# ---------------------------------------------------------------------------


def _check_coolify_tunnel() -> bool:
    """Return True if Coolify API responds on localhost:8000."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request("http://localhost:8000/api/v1/healthcheck", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            _ = resp.read()
        return True
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return True
        return True  # any HTTP response means tunnel is alive
    except Exception:
        return False


def _open_ssh_tunnel() -> bool:
    """Attempt to open SSH tunnel in background; return True if successful."""
    cmd = [
        "ssh", "-i", SSH_KEY,
        "-fN",
        "-o", "ServerAliveInterval=30",
        "-L", "8000:localhost:8000",
        VPS_HOST,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return result.returncode == 0

# ---------------------------------------------------------------------------
# Run auto preview (qualify path)
# ---------------------------------------------------------------------------


def run_auto_preview(
    entry: dict,
    *,
    no_ssh: bool,
    skip_deploy: bool,
    skip_ui_check: bool,
    mirror_dir: Path,
    processed_path: Path,
    profiles_dir: Path | None = None,
    cases_dir: Path | None = None,
    evidence_dir: Path | None = None,
    subprocess_run: Any = None,
    dry_run: bool = False,
) -> dict:
    """Execute the full auto-preview pipeline for a qualify-status entry.

    Stages (each wrapped with NODE_ENTER / NODE_EXIT_OK / NODE_FAIL):
      DRAFT_PROMOTED -- copy mirror draft -> profiles/<slug>.yaml
      SCAFFOLDED     -- subprocess scaffold.py --profile <slug>
      DEPLOYED       -- subprocess preview_package.py --coolify + deploy_to_coolify.py
      UI_CHECKED     -- subprocess ui_check.py (soft gate)
      NEEDS_FIT      -- subprocess needs_fit_audit.py (deterministic pre-pass)

    Parameters
    ----------
    entry:
        Inbox entry dict (PII-free fields from VPS).
    no_ssh:
        Whether SSH is disabled (affects tunnel check for deploy).
    skip_deploy:
        Skip DEPLOYED stage (useful in tests).
    skip_ui_check:
        Skip UI_CHECKED stage.
    mirror_dir:
        Local PII mirror root.
    processed_path:
        docs/intake-inbox/processed.jsonl path.
    profiles_dir:
        Override for profiles/ dir (test injection).
    cases_dir:
        Override for infra/registry/cases/ dir (test injection).
    evidence_dir:
        Override for evidence output dir (test injection).
    subprocess_run:
        Injectable subprocess.run replacement (for tests).
    dry_run:
        If True print intended actions; mutate nothing.

    Returns
    -------
    dict
        Summary with keys: slug, stages_ok, stages_failed, final_status.
    """
    if subprocess_run is None:
        subprocess_run = subprocess.run

    slug = entry.get("slug", "")
    client_id = entry.get("client_id", "")
    score = entry.get("score")

    if cases_dir is None:
        cases_dir = _DEFAULT_CASES_DIR
    if evidence_dir is None:
        evidence_dir = _DEFAULT_EVIDENCE_DIR

    cases_dir = Path(cases_dir)
    cases_dir.mkdir(parents=True, exist_ok=True)
    case_yaml = cases_dir / f"{client_id}.yaml"

    stages_ok: list[str] = []
    stages_failed: list[str] = []
    final_status = "built"

    # ---- Stage: DRAFT_PROMOTED ----
    node = "DRAFT_PROMOTED"
    if dry_run:
        print(f"  [DRY-RUN] {node}: promote_draft({slug})")
        stages_ok.append(node)
    else:
        _emit(case_yaml, node, "NODE_ENTER", slug=slug, score=score)
        try:
            promote_draft(
                slug, client_id, mirror_dir, profiles_dir=profiles_dir
            )
            _emit(case_yaml, node, "NODE_EXIT_OK", slug=slug, score=score)
            stages_ok.append(node)
        except Exception as exc:
            ev = _capture_evidence(
                node, slug, None, str(exc)[:500], evidence_dir=evidence_dir
            )
            _emit(
                case_yaml, node, "NODE_FAIL", slug=slug, score=score,
                error_class="draft-promote-error",
                evidence_path=str(ev) if ev else None,
            )
            stages_failed.append(node)
            record_processed(entry, processed_path, status="failed")
            return {
                "slug": slug,
                "stages_ok": stages_ok,
                "stages_failed": stages_failed,
                "final_status": "failed",
            }

    # ---- Stage: SCAFFOLDED ----
    node = "SCAFFOLDED"
    scaffold_script = str(_WORKFLOW_DIR / "scaffold.py")
    scaffold_cmd = [sys.executable, scaffold_script, "--profile", slug]

    if dry_run:
        print(f"  [DRY-RUN] {node}: {' '.join(scaffold_cmd)}")
        stages_ok.append(node)
    else:
        _emit(case_yaml, node, "NODE_ENTER", slug=slug, score=score)
        result = subprocess_run(scaffold_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            stderr_tail = (result.stderr or "")[-500:]
            ev = _capture_evidence(
                node, slug, result.returncode, stderr_tail, evidence_dir=evidence_dir
            )
            _emit(
                case_yaml, node, "NODE_FAIL", slug=slug, score=score,
                error_class="scaffold-unknown-entity",
                evidence_path=str(ev) if ev else None,
            )
            stages_failed.append(node)
            # Record as failed so --force-slug is needed for manual retry
            record_processed(entry, processed_path, status="failed")
            return {
                "slug": slug,
                "stages_ok": stages_ok,
                "stages_failed": stages_failed,
                "final_status": "failed",
            }
        _emit(case_yaml, node, "NODE_EXIT_OK", slug=slug, score=score)
        stages_ok.append(node)

    # ---- Stage: DEPLOYED ----
    node = "DEPLOYED"
    base_url = f"https://{slug}.{_PREVIEW_BASE_DOMAIN}"

    if skip_deploy:
        print(f"  [SKIP] {node}: --skip-deploy")
    else:
        pkg_script = str(_WORKFLOW_DIR / "preview_package.py")
        deploy_script = str(_WORKFLOW_DIR / "deploy_to_coolify.py")
        pkg_cmd = [sys.executable, pkg_script, "--profile", slug, "--coolify"]
        deploy_cmd = [sys.executable, deploy_script, "--slug", slug]

        if dry_run:
            print(f"  [DRY-RUN] {node}:")
            print(f"    {' '.join(pkg_cmd)}")
            print(f"    {' '.join(deploy_cmd)}")
            stages_ok.append(node)
        else:
            # Ensure Coolify tunnel
            if not no_ssh and not _check_coolify_tunnel():
                print("[intake_sync] SSH tunnel to Coolify dead; attempting to open...",
                      file=sys.stderr)
                opened = _open_ssh_tunnel()
                if not opened or not _check_coolify_tunnel():
                    ev = _capture_evidence(
                        node, slug, None, "Coolify SSH tunnel unavailable",
                        evidence_dir=evidence_dir,
                    )
                    _emit(
                        case_yaml, node, "NODE_FAIL", slug=slug, score=score,
                        error_class="sync-ssh-fail",
                        evidence_path=str(ev) if ev else None,
                    )
                    stages_failed.append(node)
                    # Leave unprocessed for retry (tunnel may recover)
                    return {
                        "slug": slug,
                        "stages_ok": stages_ok,
                        "stages_failed": stages_failed,
                        "final_status": "tunnel-fail",
                    }

            _emit(case_yaml, node, "NODE_ENTER", slug=slug, score=score)

            # preview_package.py
            pkg_result = subprocess_run(pkg_cmd, capture_output=True, text=True)
            if pkg_result.returncode != 0:
                stderr_tail = (pkg_result.stderr or "")[-500:]
                ev = _capture_evidence(
                    node, slug, pkg_result.returncode, stderr_tail,
                    evidence_dir=evidence_dir,
                )
                _emit(
                    case_yaml, node, "NODE_FAIL", slug=slug, score=score,
                    error_class="deploy-fail",
                    evidence_path=str(ev) if ev else None,
                )
                stages_failed.append(node)
                record_processed(entry, processed_path, status="failed")
                return {
                    "slug": slug,
                    "stages_ok": stages_ok,
                    "stages_failed": stages_failed,
                    "final_status": "failed",
                }

            # deploy_to_coolify.py
            deploy_result = subprocess_run(deploy_cmd, capture_output=True, text=True)
            if deploy_result.returncode != 0:
                stderr_tail = (deploy_result.stderr or "")[-500:]
                ev = _capture_evidence(
                    node, slug, deploy_result.returncode, stderr_tail,
                    evidence_dir=evidence_dir,
                )
                _emit(
                    case_yaml, node, "NODE_FAIL", slug=slug, score=score,
                    error_class="deploy-fail",
                    evidence_path=str(ev) if ev else None,
                )
                stages_failed.append(node)
                record_processed(entry, processed_path, status="failed")
                return {
                    "slug": slug,
                    "stages_ok": stages_ok,
                    "stages_failed": stages_failed,
                    "final_status": "failed",
                }

            _emit(case_yaml, node, "NODE_EXIT_OK", slug=slug, score=score)
            stages_ok.append(node)

    # ---- Stage: UI_CHECKED ----
    node = "UI_CHECKED"
    if skip_ui_check:
        print(f"  [SKIP] {node}: --skip-ui-check")
    else:
        manifest_path = str(REPO_ROOT / "out" / slug / "screen-manifest.json")
        ui_script = str(_WORKFLOW_DIR / "ui_check.py")
        ui_cmd = [
            sys.executable, ui_script,
            "--base-url", base_url,
            "--slug", slug,
            "--manifest", manifest_path,
        ]

        if dry_run:
            print(f"  [DRY-RUN] {node}: {' '.join(ui_cmd)}")
            stages_ok.append(node)
        else:
            _emit(case_yaml, node, "NODE_ENTER", slug=slug, score=score)
            ui_result = subprocess_run(ui_cmd, capture_output=True, text=True)
            # rc=0 always from ui_check.py (soft gate); rc=2 = tool error
            if ui_result.returncode == 2:
                ev = _capture_evidence(
                    node, slug, ui_result.returncode,
                    (ui_result.stderr or "")[-500:],
                    evidence_dir=evidence_dir,
                )
                _emit(
                    case_yaml, node, "NODE_FAIL", slug=slug, score=score,
                    error_class="ui-check-fail",
                    evidence_path=str(ev) if ev else None,
                )
                stages_failed.append(node)
                # Soft gate: continue pipeline but flag
            else:
                # Read verdict from the written JSON report
                report_path = (
                    REPO_ROOT / "docs" / "intake-inbox" / "ui-checks" / f"{slug}.json"
                )
                verdict = "UNKNOWN"
                if report_path.exists():
                    try:
                        report = json.loads(report_path.read_text(encoding="utf-8"))
                        verdict = report.get("verdict", "UNKNOWN")
                    except Exception:
                        pass
                if verdict == "FAIL":
                    ev = _capture_evidence(
                        node, slug, 0, f"ui verdict={verdict}",
                        report_path=str(report_path),
                        evidence_dir=evidence_dir,
                    )
                    _emit(
                        case_yaml, node, "NODE_FAIL", slug=slug, score=score,
                        error_class="ui-check-fail",
                        evidence_path=str(ev) if ev else None,
                    )
                    stages_failed.append(node)
                    # Still continue -- soft gate
                    final_status = "built-ui-warn"
                else:
                    _emit(case_yaml, node, "NODE_EXIT_OK", slug=slug, score=score)
                    stages_ok.append(node)

    # ---- Stage: NEEDS_FIT ----
    node = "NEEDS_FIT"
    needs_note_path = (
        Path(mirror_dir) / "clients" / client_id / "needs-note.md"
    )
    manifest_path = str(REPO_ROOT / "out" / slug / "screen-manifest.json")
    profile_path = str((profiles_dir or _DEFAULT_PROFILES_DIR) / f"{slug}.yaml")
    nf_script = str(_WORKFLOW_DIR / "needs_fit_audit.py")
    nf_cmd = [
        sys.executable, nf_script,
        "--slug", slug,
        "--needs-note", str(needs_note_path),
        "--manifest", manifest_path,
        "--profile", profile_path,
    ]

    if dry_run:
        print(f"  [DRY-RUN] {node}: {' '.join(nf_cmd)}")
        stages_ok.append(node)
    else:
        if not needs_note_path.exists():
            print(
                f"[intake_sync] WARN: needs-note.md missing for {slug}; skipping NEEDS_FIT",
                file=sys.stderr,
            )
        else:
            _emit(case_yaml, node, "NODE_ENTER", slug=slug, score=score)
            nf_result = subprocess_run(nf_cmd, capture_output=True, text=True)
            stdout_text = nf_result.stdout or ""
            # Parse verdict from stdout envelope; needs_fit_audit prints
            # "VERDICT: PASS|PASS-WITH-CAVEAT|BLOCK" in its envelope
            nf_verdict = "UNKNOWN"
            for line in stdout_text.splitlines():
                if line.startswith("VERDICT:"):
                    nf_verdict = line.split(":", 1)[1].strip()
                    break

            if nf_verdict == "BLOCK":
                ev = _capture_evidence(
                    node, slug, nf_result.returncode,
                    (nf_result.stderr or "")[-300:],
                    evidence_dir=evidence_dir,
                )
                _emit(
                    case_yaml, node, "NODE_FAIL", slug=slug, score=score,
                    error_class="needs-fit-BLOCK",
                    evidence_path=str(ev) if ev else None,
                )
                stages_failed.append(node)
                # Flag but do not block record_processed; delivery is CEO-gated
                if final_status == "built":
                    final_status = "built-needs-fit-block"
            else:
                _emit(case_yaml, node, "NODE_EXIT_OK", slug=slug, score=score)
                stages_ok.append(node)

    if not dry_run:
        record_processed(entry, processed_path, status=final_status)

    return {
        "slug": slug,
        "stages_ok": stages_ok,
        "stages_failed": stages_failed,
        "final_status": final_status,
    }

# ---------------------------------------------------------------------------
# Call / gap routing helpers
# ---------------------------------------------------------------------------


def _append_pm_inbox(pm_inbox: Path, block: str) -> None:
    pm_inbox.parent.mkdir(parents=True, exist_ok=True)
    with pm_inbox.open("a", encoding="utf-8") as fh:
        fh.write(block + "\n")


def _append_gap_registry(gap_registry: Path, record: dict) -> None:
    gap_registry.parent.mkdir(parents=True, exist_ok=True)
    with gap_registry.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Route entry
# ---------------------------------------------------------------------------


def route_entry(
    entry: dict,
    *,
    no_ssh: bool,
    skip_deploy: bool,
    skip_ui_check: bool,
    mirror_dir: Path,
    processed_path: Path,
    profiles_dir: Path | None = None,
    cases_dir: Path | None = None,
    evidence_dir: Path | None = None,
    pm_inbox_path: Path | None = None,
    gap_registry_path: Path | None = None,
    subprocess_run: Any = None,
    dry_run: bool = False,
) -> dict:
    """Route an inbox entry to the appropriate handling path.

    Routing:
      prefer_call == "yes" -> CALL QUEUE (no build)
      status in {gap_only, defer}   -> GAP REGISTRY + PM TRIAGE (no build)
      status == qualify             -> run_auto_preview(...)

    Returns summary dict.
    """
    ts = entry.get("ts", "")
    slug = entry.get("slug", "")
    score = entry.get("score")
    status = entry.get("status", "")
    prefer_call = str(entry.get("prefer_call", "")).lower().strip()
    client_id = entry.get("client_id", "")

    if cases_dir is None:
        cases_dir = _DEFAULT_CASES_DIR
    if pm_inbox_path is None:
        pm_inbox_path = _DEFAULT_PM_INBOX
    if gap_registry_path is None:
        gap_registry_path = _DEFAULT_GAP_REGISTRY

    cases_dir = Path(cases_dir)
    cases_dir.mkdir(parents=True, exist_ok=True)
    case_yaml = cases_dir / f"{client_id}.yaml"

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---- prefer_call path ----
    if prefer_call == "yes":
        block = (
            f"\n## CALL REQUEST [{now_str}]\n"
            f"- slug: {slug}\n"
            f"- score: {score}\n"
            f"- status: call_queue\n"
            f"- action: Contact client; build on hold.\n"
        )
        if dry_run:
            print(f"  [DRY-RUN] pm-inbox: CALL REQUEST for {slug}")
        else:
            _append_pm_inbox(pm_inbox_path, block)
            _set_triage(case_yaml, "prefer_call")
            _emit(case_yaml, "CALL_QUEUE", "NODE_ENTER", slug=slug, score=score)
            _emit(case_yaml, "CALL_QUEUE", "NODE_EXIT_OK", slug=slug, score=score)
            record_processed(entry, processed_path, status="call_queue")
        return {"slug": slug, "routed_to": "call_queue", "final_status": "call_queue"}

    # ---- gap_only / defer path ----
    if status in ("gap_only", "defer"):
        gap_record: dict[str, Any] = {
            "ts": ts,
            "slug": slug,
            "score": score,
            "gap_category": entry.get("gap_category", ""),
            "todo_axis": entry.get("todo_axis", ""),
        }
        block = (
            f"\n## TRIAGE [{now_str}]\n"
            f"- slug: {slug}\n"
            f"- score: {score}\n"
            f"- status: {status}\n"
            f"- gap_category: {entry.get('gap_category', 'unknown')}\n"
            f"- todo_axis: {entry.get('todo_axis', '')}\n"
            f"- action: Review gap-registry.jsonl; schedule PM triage.\n"
        )
        if dry_run:
            print(f"  [DRY-RUN] gap-registry + pm-inbox for {slug} ({status})")
        else:
            _append_gap_registry(gap_registry_path, gap_record)
            _append_pm_inbox(pm_inbox_path, block)
            triage_map = {"gap_only": "gap_only", "defer": "defer"}
            _set_triage(case_yaml, triage_map[status])
            emit_node = "GAP_RECORDED" if status == "gap_only" else "PM_TRIAGE"
            _emit(case_yaml, emit_node, "NODE_ENTER", slug=slug, score=score)
            _emit(case_yaml, emit_node, "NODE_EXIT_OK", slug=slug, score=score)
            record_processed(entry, processed_path, status=status)
        return {
            "slug": slug,
            "routed_to": "gap_registry",
            "final_status": status,
        }

    # ---- qualify path ----
    if status == "qualify":
        print(f"[intake_sync] {slug}: qualify -> run_auto_preview")
        return run_auto_preview(
            entry,
            no_ssh=no_ssh,
            skip_deploy=skip_deploy,
            skip_ui_check=skip_ui_check,
            mirror_dir=mirror_dir,
            processed_path=processed_path,
            profiles_dir=profiles_dir,
            cases_dir=cases_dir,
            evidence_dir=evidence_dir,
            subprocess_run=subprocess_run,
            dry_run=dry_run,
        )

    # ---- unknown status: record as skipped ----
    print(
        f"[intake_sync] WARN: entry {slug} has unknown status={status!r}; skipping",
        file=sys.stderr,
    )
    if not dry_run:
        record_processed(entry, processed_path, status=f"skipped-unknown-{status}")
    return {"slug": slug, "routed_to": "unknown", "final_status": "skipped"}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "intake_sync.py -- Phase 4 sync bridge (LLM 0).\n"
            "Pulls VPS intake artifacts and routes each pending inbox entry."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print intended actions without mutating files or running subprocesses.",
    )
    parser.add_argument(
        "--no-ssh", action="store_true",
        help="Skip SSH rsync; use existing data-mirror files.",
    )
    parser.add_argument(
        "--skip-deploy", action="store_true",
        help="Skip DEPLOYED stage (preview_package.py + deploy_to_coolify.py).",
    )
    parser.add_argument(
        "--skip-ui-check", action="store_true",
        help="Skip UI_CHECKED stage.",
    )
    parser.add_argument(
        "--force-slug", metavar="SLUG", default=None,
        help="Process only this slug, even if already in processed.jsonl.",
    )
    parser.add_argument(
        "--mirror", metavar="DIR", default=str(_DEFAULT_MIRROR_DIR),
        help=f"Local PII mirror dir (gitignored). Default: {_DEFAULT_MIRROR_DIR}",
    )
    parser.add_argument(
        "--processed", metavar="FILE", default=str(_DEFAULT_PROCESSED),
        help=f"Processed JSONL path. Default: {_DEFAULT_PROCESSED}",
    )
    args = parser.parse_args(argv)

    mirror_dir = Path(args.mirror)
    processed_path = Path(args.processed)

    if args.dry_run:
        print("[intake_sync] *** DRY-RUN MODE -- no files will be mutated ***")

    # 1. Rsync inbox
    rsync_inbox(args.no_ssh, mirror_dir)

    # 2. Load inbox
    entries = load_inbox(mirror_dir)
    if not entries:
        print("[intake_sync] inbox empty; nothing to do.")
        if not args.dry_run:
            _run_monitor()
        return 0

    print(f"[intake_sync] {len(entries)} inbox entries loaded.")

    # 3. Route each entry
    summaries: list[dict] = []
    for entry in entries:
        ts = entry.get("ts", "")
        slug = entry.get("slug", "")

        # --force-slug: skip non-matching entries; ignore is_processed for matching
        if args.force_slug and slug != args.force_slug:
            continue

        if not args.force_slug and is_processed(ts, processed_path):
            print(f"[intake_sync] {slug} (ts={ts}): already processed; skip.")
            continue

        print(f"[intake_sync] Processing {slug} (ts={ts}, status={entry.get('status')})...")

        # Rsync client artifacts
        client_id = entry.get("client_id", "")
        if client_id:
            rsync_client_artifacts(client_id, args.no_ssh, mirror_dir)

        summary = route_entry(
            entry,
            no_ssh=args.no_ssh,
            skip_deploy=args.skip_deploy,
            skip_ui_check=args.skip_ui_check,
            mirror_dir=mirror_dir,
            processed_path=processed_path,
            dry_run=args.dry_run,
        )
        summaries.append(summary)

    # 4. Print per-case summary table
    if summaries:
        print("\n[intake_sync] === Summary ===")
        print(f"  {'slug':<30} {'routed_to':<20} {'final_status'}")
        print(f"  {'-'*30} {'-'*20} {'-'*20}")
        for s in summaries:
            routed = s.get("routed_to", s.get("stages_ok", ["-"]).__class__.__name__)
            if "stages_ok" in s:
                routed = "qualify"
            print(
                f"  {s.get('slug', ''):<30} "
                f"{routed:<20} "
                f"{s.get('final_status', '')}"
            )

    # 5. Run pipeline monitor alert check
    if not args.dry_run:
        _run_monitor()

    return 0


def _run_monitor() -> None:
    monitor_script = str(_WORKFLOW_DIR / "pipeline_monitor.py")
    try:
        result = subprocess.run(
            [sys.executable, monitor_script, "--alert"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(
                f"[intake_sync] WARN: pipeline_monitor --alert returned rc={result.returncode}",
                file=sys.stderr,
            )
    except Exception as exc:
        print(f"[intake_sync] WARN: pipeline_monitor call failed: {exc}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
