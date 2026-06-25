#!/usr/bin/env python3
"""Design-Cloud Bridge — 고객 복제본(replica) 빌더 (WP-3).

고객 profile + theme 로 **빌드타임 물리격리된 정적 번들**을 만든다. 런타임 멀티테넌트
라우팅(논리격리)의 반대 — 고객마다 자기 데이터·브랜딩만 담은 별도 디렉터리를 산출하고,
클라우드(claude.ai/design) 결합·타 테넌트 식별자·raw PII 가 0 임을 누출 가드로 강제한다.

설계: docs/architecture/design-cloud-bridge.md §1 C(복제본), §3,
       docs/architecture/design-cloud-bridge-execution-plan.md (WP-3).

흐름 (deliverable_kind=marketing-site):
  1. scaffold   — scripts/workflow/scaffold.py --profile <slug> → out/<slug>/site-manifest.json
  2. astro build — PUBLIC_SITE_MANIFEST 설정 후 landing-astro 어댑터에서 `npm run build` → dist/
                   (--skip-astro-build 시 기존 dist 재사용 — node_modules 없는 환경/재격리용)
  3. isolate    — dist/ → <replica-root>/<slug>/ 로 복제 (격리 디렉터리, 정리 후 복사)
  4. leak gate  — 번들에 누출 3종 검사(cloud 결합·타 테넌트 slug·raw PII). 위반 시 비0 종료.

토큰 파이프라인 메모 (Style Dictionary v5+ 평가, WP-3 §6):
  landing-astro 의 build-tokens.mjs 가 raw.json→semantic.json→theme.yaml override→
  CSS custom props + Tailwind theme 를 자체 해소한다(자체 구현, 의존성 0). 이는 Style
  Dictionary 가 하는 일과 동치이며 신규 Node 의존을 더하지 않는다. 따라서 **현행 유지**가
  cost-aware 결론 — Style Dictionary v5+ 도입은 (a) iOS/Android 네이티브 멀티플랫폼 출력,
  또는 (b) 외부 도구와의 DTCG 라운드트립이 필요해질 때 재검토. 본 빌더는 그 파이프라인을
  그대로 호출(재구현 금지, open-closed)한다.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# build_replica.py 는 <repo>/scripts/design/build_replica.py
REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_ADAPTER = REPO_ROOT / "frontend" / "adapters" / "landing-astro"
_DEFAULT_OUT_ROOT = REPO_ROOT / "out"
_DEFAULT_REPLICA_ROOT = REPO_ROOT / "out" / "replicas"

# 누출 가드(diagnose.py)를 직접 호출하기 위해 scripts/ 를 path 에 추가.
_SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


class ReplicaError(RuntimeError):
    """복제본 빌드 실패 (누출 게이트 포함)."""


def _utf8_stdout() -> None:
    # Windows 콘솔(cp949)에서 한글/em-dash 출력 깨짐 방지.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


def load_profile(slug: str, profiles_dir: Path | None = None) -> dict:
    """profiles/<slug>.yaml 로드 (없으면 ReplicaError)."""
    pdir = profiles_dir if profiles_dir is not None else REPO_ROOT / "profiles"
    path = pdir / f"{slug}.yaml"
    if not path.is_file():
        raise ReplicaError(f"profile not found: {path}")
    try:
        import yaml  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover
        raise ReplicaError(f"pyyaml required to read profile: {exc}") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _deliverable_kind(profile: dict) -> str:
    stack = profile.get("stack")
    if isinstance(stack, dict) and stack.get("deliverable_kind"):
        return str(stack["deliverable_kind"])
    return str(profile.get("deliverable_kind") or "")


def run_scaffold(slug: str, out_root: Path) -> Path:
    """scaffold.py 를 호출해 out/<slug>/site-manifest.json 을 산출, 그 경로 반환."""
    scaffold = REPO_ROOT / "scripts" / "workflow" / "scaffold.py"
    if not scaffold.is_file():
        raise ReplicaError(f"scaffold.py not found: {scaffold}")
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    cmd = [sys.executable, str(scaffold), "--profile", slug, "--out", str(out_root)]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ReplicaError(f"scaffold failed (rc={proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    manifest = out_root / slug / "site-manifest.json"
    if not manifest.is_file():
        raise ReplicaError(f"scaffold produced no manifest: {manifest}")
    return manifest


def run_astro_build(adapter_dir: Path, manifest: Path) -> Path:
    """landing-astro 어댑터에서 npm run build 실행, dist/ 경로 반환."""
    if not (adapter_dir / "package.json").is_file():
        raise ReplicaError(f"landing-astro adapter not found: {adapter_dir}")
    if not (adapter_dir / "node_modules").is_dir():
        raise ReplicaError(
            f"node_modules absent in {adapter_dir} — run `npm install` there, "
            "or use --skip-astro-build with an existing dist."
        )
    npm = shutil.which("npm")
    if not npm:
        raise ReplicaError("npm not found on PATH.")
    env = {**os.environ, "PUBLIC_SITE_MANIFEST": str(manifest.resolve())}
    proc = subprocess.run([npm, "run", "build"], cwd=str(adapter_dir), env=env,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-25:])
        raise ReplicaError(f"astro build failed (rc={proc.returncode}):\n{tail}")
    dist = adapter_dir / "dist"
    if not dist.is_dir():
        raise ReplicaError(f"build produced no dist: {dist}")
    return dist


def isolate_bundle(source_dist: Path, slug: str, replica_root: Path) -> Path:
    """source_dist 를 <replica_root>/<slug>/ 로 격리 복제 (기존 내용 정리 후)."""
    if not source_dist.is_dir():
        raise ReplicaError(f"source dist not found: {source_dist}")
    dest = replica_root / slug
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dist, dest)
    return dest


# ── 누출 게이트 (복제본 인도 전 비협상 검사) ─────────────────────────────────
def verify_no_leak(replica_root: Path, slug: str,
                   profiles_dir: Path | None = None,
                   cases_dir: Path | None = None) -> list[str]:
    """번들에 누출 3종(cloud 결합·타 테넌트 slug·raw PII)이 없는지 검사. 위반 리스트 반환.

    diagnose.py 의 단일 진실 가드를 재사용한다(재구현 금지):
      G-17 cloud-coupling-leak, G-18 cross-tenant-leak, 그리고 _PII_PATTERNS 로 raw PII.

    한계 (QA WP-3 게이트 기록):
      · 텍스트 파일만 스캔 — 바이너리 에셋(.png/.woff2) 속 누출은 대상 외.
      · G-18 은 profiles/cases 에 등록된 known slug + 빌드된 번들 이름만 foreign 으로 본다.
        미등록 테넌트 slug 는 탐지 불가. 단일 번들만 빌드된 초기 상태에선 foreign set 이
        비어 G-18 이 사실상 비활성(거짓음성) — 복수 고객 빌드 시 활성. M2+ 재검토 대상.
    """
    import diagnose  # noqa: E402  (scripts/ on path)

    bundle = replica_root / slug
    violations: list[str] = []

    # 1) 클라우드 결합 (G-17) — 이 번들만 스캔.
    r17 = diagnose.g17_cloud_coupling_leak(scan_roots=(bundle,))
    if r17.status == "FAIL":
        violations += [f"[G-17] {v}" for v in r17.violations]

    # 2) 교차 테넌트 slug (G-18) — replica_root 전체(이 번들 포함).
    r18 = diagnose.g18_cross_tenant_leak(
        replica_root=replica_root, profiles_dir=profiles_dir, cases_dir=cases_dir,
    )
    if r18.status == "FAIL":
        violations += [f"[G-18] {v}" for v in r18.violations]

    # 3) raw PII / 시크릿 경로 참조 (G-16 패턴 재사용) — 이 번들만.
    for p in diagnose._iter_files(bundle, diagnose._TEXTY_SUFFIXES):
        text = p.read_text(encoding="utf-8", errors="replace")
        for pat, label in diagnose._PII_PATTERNS:
            if pat.search(text):
                violations.append(f"[PII] {diagnose._rel(p)}: contains {label}")
        for ref in diagnose._FORBIDDEN_PATH_REFS:
            if ref in text:
                violations.append(f"[PII] {diagnose._rel(p)}: references secret/PII path '{ref}'")
    return violations


def build_replica(
    slug: str,
    *,
    out_root: Path | None = None,
    adapter_dir: Path | None = None,
    replica_root: Path | None = None,
    skip_astro_build: bool = False,
    dist_dir: Path | None = None,
) -> dict:
    """end-to-end 복제본 빌드. 결과 dict(bundle 경로·파일수·게이트) 반환."""
    out_root = out_root or _DEFAULT_OUT_ROOT
    adapter_dir = adapter_dir or _DEFAULT_ADAPTER
    replica_root = replica_root or _DEFAULT_REPLICA_ROOT

    profile = load_profile(slug)
    kind = _deliverable_kind(profile)
    if kind != "marketing-site":
        # business-system 등은 본 빌더 범위 밖 — 명시적 실패가 침묵보다 안전.
        raise ReplicaError(
            f"profile '{slug}' deliverable_kind={kind!r} — build_replica only handles 'marketing-site'."
        )

    manifest = run_scaffold(slug, out_root)

    if skip_astro_build:
        source_dist = dist_dir if dist_dir is not None else adapter_dir / "dist"
        if not source_dist.is_dir():
            raise ReplicaError(
                f"--skip-astro-build but no dist at {source_dist} — build once or pass --dist-dir."
            )
    else:
        source_dist = run_astro_build(adapter_dir, manifest)

    bundle = isolate_bundle(source_dist, slug, replica_root)
    file_count = sum(1 for _ in bundle.rglob("*") if _.is_file())

    violations = verify_no_leak(replica_root, slug)
    return {
        "slug": slug,
        "theme": (profile.get("site") or {}).get("theme"),
        "manifest": str(manifest),
        "bundle": str(bundle),
        "files": file_count,
        "leak_violations": violations,
        "ok": not violations,
    }


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="customer profile slug (profiles/<slug>.yaml)")
    parser.add_argument("--out-root", type=Path, default=None, help="scaffold out root (default: out/)")
    parser.add_argument("--adapter-dir", type=Path, default=None, help="landing-astro adapter dir")
    parser.add_argument("--replica-root", type=Path, default=None, help="replica output root (default: out/replicas/)")
    parser.add_argument("--skip-astro-build", action="store_true", help="reuse existing dist instead of npm build")
    parser.add_argument("--dist-dir", type=Path, default=None, help="explicit dist to isolate (with --skip-astro-build)")
    args = parser.parse_args(argv)

    try:
        result = build_replica(
            args.slug,
            out_root=args.out_root,
            adapter_dir=args.adapter_dir,
            replica_root=args.replica_root,
            skip_astro_build=args.skip_astro_build,
            dist_dir=args.dist_dir,
        )
    except ReplicaError as exc:
        print(f"build_replica: {exc}", file=sys.stderr)
        return 2

    print(f"# 복제본 빌드 — {result['slug']} (theme={result['theme']})")
    print(f"  manifest : {result['manifest']}")
    print(f"  bundle   : {result['bundle']}  ({result['files']} files)")
    if result["ok"]:
        print("  leak gate: PASS (cloud 결합 0 · 타 테넌트 slug 0 · raw PII 0)")
        return 0
    print(f"  leak gate: FAIL ({len(result['leak_violations'])} violation(s)) — 인도 차단")
    for v in result["leak_violations"]:
        print(f"    ✗ {v}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
