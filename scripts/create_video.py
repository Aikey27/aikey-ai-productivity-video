#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "assets" / "template"


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("[执行]", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, check=True)


def require_tool(name: str, hint: str) -> None:
    if not shutil.which(name):
        raise SystemExit(f"缺少 {name}。{hint}")


def audio_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return max(1.0, float(result.stdout.strip()))


def split_text(text: str, maximum: int = 7) -> list[str]:
    parts = [p.strip() for p in re.split(r"(?<=[。！？!?；;])\s*|\n+", text) if p.strip()]
    if not parts:
        return [text.strip()]
    while len(parts) > maximum:
        index = min(range(len(parts) - 1), key=lambda i: len(parts[i]) + len(parts[i + 1]))
        parts[index:index + 2] = [parts[index] + parts[index + 1]]
    return parts


def make_scenes(text: str, duration: float) -> dict[str, object]:
    parts = split_text(text)
    weights = [max(1, len(re.sub(r"\s+", "", part))) for part in parts]
    total_weight = sum(weights)
    kickers = ["核心问题", "关键变化", "操作方法", "实际价值", "使用场景", "能力边界", "行动建议"]
    scenes: list[dict[str, object]] = []
    cursor = 0.0
    for index, (part, weight) in enumerate(zip(parts, weights)):
        end = duration if index == len(parts) - 1 else cursor + duration * weight / total_weight
        headline = re.sub(r"[，。！？!?；;：:]", " ", part).strip()
        if len(headline) > 18:
            headline = headline[:18].rstrip() + "…"
        scenes.append({
            "kicker": kickers[min(index, len(kickers) - 1)],
            "headline": headline,
            "body": part,
            "start": round(cursor, 3),
            "end": round(max(cursor + 0.5, end), 3),
            "kind": "hook" if index == 0 else "content",
        })
        cursor = end
    return {"title": "AI 生产力", "accent": "#33E6D4", "scenes": scenes}


def ensure_dependencies(project: Path) -> None:
    if (project / "node_modules" / ".bin" / "remotion").exists():
        return
    require_tool("npm", "请安装 Node.js 18 或更高版本。")
    run(["npm", "install", "--no-audit", "--no-fund"], project)


def main() -> None:
    parser = argparse.ArgumentParser(description="AIKEY 公开版：文案自动配音并生成竖屏科技视频")
    parser.add_argument("--text-file", type=Path, required=True, help="UTF-8 中文文案")
    parser.add_argument("--audio", type=Path, help="可选：已有 MP3/WAV；提供后跳过在线配音")
    parser.add_argument("--output", type=Path, default=Path("AIKEY-VIDEO/output.mp4"))
    args = parser.parse_args()

    require_tool("ffmpeg", "请先安装 FFmpeg。")
    require_tool("ffprobe", "请先安装 FFmpeg。")

    text_file = args.text_file.expanduser().resolve()
    if not text_file.exists():
        raise SystemExit(f"找不到文案文件：{text_file}")
    text = text_file.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("文案文件为空。")

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    work = output.parent / f"aikey-video-workspace-{int(time.time())}"
    shutil.copytree(TEMPLATE / "remotion", work)
    public = work / "public"
    public.mkdir(parents=True, exist_ok=True)

    if args.audio:
        source_audio = args.audio.expanduser().resolve()
        if not source_audio.exists():
            raise SystemExit(f"找不到配音文件：{source_audio}")
        voice_source = "user-audio"
    else:
        source_audio = work / "volcengine-narration.mp3"
        run([sys.executable, str(SKILL_ROOT / "scripts" / "volcengine_tts.py"), "--text-file", str(text_file), "--output", str(source_audio)])
        voice_source = "volcengine"

    narration = public / "narration.wav"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source_audio), "-ar", "48000", "-ac", "1", str(narration)])
    duration = audio_duration(narration)
    scenes = make_scenes(text, duration)
    (work / "src" / "scenes.json").write_text(json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(text_file, work / "script.txt")

    ensure_dependencies(work)
    env = os.environ.copy()
    temp_dir = work / "tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(temp_dir)
    run([
        "npx", "remotion", "render", "src/index.ts", "Video", str(output),
        "--codec=h264", "--audio-codec=aac", "--pixel-format=yuv420p",
    ], work, env)

    if not output.exists() or output.stat().st_size < 100_000:
        raise SystemExit("渲染没有生成有效视频。")
    print(json.dumps({
        "status": "ok",
        "output": str(output),
        "bytes": output.stat().st_size,
        "duration_seconds": round(duration, 3),
        "voice_source": voice_source,
        "workspace": str(work),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

