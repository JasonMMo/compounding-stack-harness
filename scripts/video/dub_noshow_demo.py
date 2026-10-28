"""
dub_noshow_demo.py — 녹화본(record_noshow_demo.py)에 나레이션 음성을 장면별로 더빙.

나레이션 음성은 founder 가 VoiceStudio 로 만든 단일 wav(narration_voice.wav,
6문장 연속 낭독). 문장 경계는 무음 구간과 음절 수를 대조해 정했고(VOICE_CUTS),
각 문장은 녹화 시 실측된 장면 시작(timeline*.json)에 상대 오프셋으로 놓인다.
→ 재녹화해도 같은 음성으로 다시 더빙 가능. 음성을 새로 만들면 VOICE_CUTS 재측정.

    python scripts/video/dub_noshow_demo.py              # 가로판
    python scripts/video/dub_noshow_demo.py --vertical   # 9:16 세로판
    # 산출: out/noshow-video/noshow-demo[-vertical]-dubbed.{mp4,srt}

비용: API 호출 0. ffmpeg 로컬만 사용.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

# (장면 key, 장면 시작 대비 오프셋 s, 원본 wav 구간들, 구간 사이 간격 s)
# reminder 는 문장(6.9s)이 장면(6.5s)보다 길어 내부 쉼을 압축하고 0.3s 먼저 시작.
VOICE_CUTS = [
    ("intro", 0.35, [(0.00, 2.90)], 0.0),
    ("booking", 0.31, [(3.79, 8.77)], 0.0),
    ("confirm", 0.31, [(9.42, 12.73)], 0.0),
    ("reminder", -0.30, [(13.59, 13.88), (14.14, 15.59), (15.88, 18.14), (18.49, 20.98)], 0.15),
    ("cancel", 0.70, [(21.87, 27.55)], 0.0),
    ("outro", 0.27, [(28.43, 31.09), (31.98, 34.48)], 0.45),
]
# 마지막 문장이 아웃트로보다 길어 끝 프레임을 늘린다.
TAIL_PAD = 2.0


def fmt_srt(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main() -> None:
    ap = argparse.ArgumentParser(description="노쇼가드 시연 영상 장면별 더빙")
    ap.add_argument("--out-dir", default="out/noshow-video")
    ap.add_argument("--voice", default=None, help="기본: <out-dir>/narration_voice.wav")
    ap.add_argument("--vertical", action="store_true")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    suffix = "-vertical" if args.vertical else ""
    voice = Path(args.voice) if args.voice else out_dir / "narration_voice.wav"
    video = out_dir / f"noshow-demo{suffix}.mp4"
    marks = json.loads((out_dir / f"timeline{suffix}.json").read_text(encoding="utf-8"))
    starts = {m["key"]: m["start"] for m in marks}

    narr = [line.split("] ", 1)[1] for line in
            (out_dir / f"narration{suffix}.txt").read_text(encoding="utf-8").splitlines() if line]

    chains, labels, srt = [], [], []
    for i, (key, offset, cuts, gap) in enumerate(VOICE_CUTS):
        at = starts[key] + offset
        parts = []
        for j, (s, e) in enumerate(cuts):
            chains.append(f"[1:a]atrim={s}:{e},asetpts=PTS-STARTPTS[c{i}_{j}]")
            parts.append(f"[c{i}_{j}]")
            if gap and j < len(cuts) - 1:
                chains.append(f"anullsrc=r=24000:cl=mono,atrim=0:{gap}[g{i}_{j}]")
                parts.append(f"[g{i}_{j}]")
        dur = sum(e - s for s, e in cuts) + gap * (len(cuts) - 1)
        chains.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1,adelay={int(at * 1000)}[l{i}]")
        labels.append(f"[l{i}]")
        srt += [str(i + 1), f"{fmt_srt(at)} --> {fmt_srt(at + dur)}", narr[i], ""]

    chains.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,"
                  "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,pan=stereo|c0=c0|c1=c0,apad[a]")
    chains.append(f"[0:v]tpad=stop_mode=clone:stop_duration={TAIL_PAD}[v]")
    mp4 = out_dir / f"noshow-demo{suffix}-dubbed.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(voice),
         "-filter_complex", ";".join(chains), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(mp4)],
        check=True,
    )
    (out_dir / f"noshow-demo{suffix}-dubbed.srt").write_text("\n".join(srt), encoding="utf-8")
    print(json.dumps({"mp4": str(mp4)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
