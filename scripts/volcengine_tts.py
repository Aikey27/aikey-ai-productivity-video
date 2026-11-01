#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import uuid
import urllib.error
import urllib.request
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TTS_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse"
DEFAULT_SPEAKER = "zh_female_vv_uranus_bigtts"
DEFAULT_RESOURCE = "seed-tts-2.0"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def configuration() -> tuple[str, str, str]:
    load_dotenv(SKILL_ROOT / ".env")
    api_key = os.environ.get("VOLCENGINE_API_KEY", "").strip()
    if not api_key or api_key == "请填写你的_API_Key":
        raise SystemExit("缺少 VOLCENGINE_API_KEY。请复制 .env.example 为 .env 并填写 API Key。")
    speaker = os.environ.get("VOLCENGINE_SPEAKER_ID", DEFAULT_SPEAKER).strip() or DEFAULT_SPEAKER
    resource = os.environ.get("VOLCENGINE_RESOURCE_ID", DEFAULT_RESOURCE).strip() or DEFAULT_RESOURCE
    if resource not in {"seed-tts-2.0", "seed-icl-2.0"}:
        raise SystemExit("VOLCENGINE_RESOURCE_ID 仅支持 seed-tts-2.0 或 seed-icl-2.0。")
    return api_key, speaker, resource


def synthesize(text: str) -> tuple[bytes, str, str, str]:
    api_key, speaker, resource = configuration()
    request_id = str(uuid.uuid4())
    payload = {
        "user": {"uid": "workbuddy-skill-user"},
        "req_params": {
            "text": text,
            "speaker": speaker,
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000,
                "speech_rate": 0,
                "loudness_rate": 0,
            },
            "additions": json.dumps({"disable_markdown_filter": False}),
        },
    }
    request = urllib.request.Request(
        TTS_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "X-Api-Key": api_key,
            "X-Api-Resource-Id": resource,
            "X-Api-Request-Id": request_id,
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )

    chunks: list[bytes] = []
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            for raw in response:
                line = raw.decode("utf-8", errors="replace").strip()
                if line.startswith("data:"):
                    line = line[5:].strip()
                if not line or line == "[DONE]":
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("data"):
                    chunks.append(base64.b64decode(event["data"]))
                code = event.get("code")
                if code not in (None, 0, 1000, 20000000):
                    message = event.get("message") or "未知错误"
                    raise SystemExit(f"火山引擎配音失败（{code}）：{message}；请求 ID：{request_id}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise SystemExit(f"火山引擎配音请求失败（HTTP {exc.code}）：{detail}；请求 ID：{request_id}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"无法连接火山引擎：{exc.reason}；请求 ID：{request_id}") from exc

    if not chunks:
        raise SystemExit(f"火山引擎没有返回音频。请检查额度和 API Key；请求 ID：{request_id}")
    return b"".join(chunks), speaker, resource, request_id


def main() -> None:
    parser = argparse.ArgumentParser(description="使用火山引擎豆包语音生成连续配音")
    parser.add_argument("--text-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    text = args.text_file.expanduser().read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("配音文本为空。")
    audio, speaker, resource, request_id = synthesize(text)
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(audio)
    print(json.dumps({
        "status": "ok",
        "output": str(output),
        "bytes": len(audio),
        "voice_source": "volcengine",
        "speaker": speaker,
        "resource_id": resource,
        "request_id": request_id,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

