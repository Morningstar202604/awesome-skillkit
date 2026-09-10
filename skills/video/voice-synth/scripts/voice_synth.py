#!/usr/bin/env python3
"""Video Voice Synthesis (TTS) — 文本转语音。

用法:
  python3 voice_synth.py --text "你好" --voice baby_f01
  python3 voice_synth.py --script script.json  (batch TTS for all scenes)
"""
import argparse
import json
import struct
import sys
import time
import wave
from pathlib import Path
from typing import Dict, Any

GATEWAY_URL = "http://127.0.0.1:30081/v1/tts"
MOCK_MODE = True

VOICES = {
    "baby_f01": {"desc": "High-pitched child", "pitch": 5, "speed": 1.3},
    "baby_f02": {"desc": "Slower baby", "pitch": 4, "speed": 1.0},
    "adult_m01": {"desc": "Male narrator", "pitch": 0, "speed": 1.0},
    "adult_f01": {"desc": "Female narrator", "pitch": 1, "speed": 1.0},
    "mascot_01": {"desc": "Enthusiastic mascot", "pitch": 2, "speed": 1.1},
    "narrator_01": {"desc": "Neutral clear", "pitch": 0, "speed": 0.9},
}


def synthesize_voice(text: str, voice: str = "baby_f01",
                     speed: float = None, pitch: int = None,
                     output: str = None) -> Dict[str, Any]:
    """Generate TTS audio (mock or gateway)."""
    voice_conf = VOICES.get(voice, {"pitch": 0, "speed": 1.0})
    speed = speed or voice_conf["speed"]
    pitch = pitch if pitch is not None else voice_conf["pitch"]

    if MOCK_MODE:
        return _mock_synth(text, voice, output)

    import urllib.request
    payload = json.dumps({
        "text": text, "voice": voice,
        "speed": speed, "pitch": pitch, "format": "wav",
    }).encode()
    req = urllib.request.Request(GATEWAY_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        audio = resp.read()
        out = Path(output or f"/tmp/tts_{int(time.time())}.wav")
        out.write_bytes(audio)
        return {
            "audio_path": str(out), "text": text,
            "voice_used": voice, "mock": False,
        }


def _mock_synth(text: str, voice: str, output: str = None) -> Dict[str, Any]:
    """Generate silent WAV as mock (duration proportional to text length)."""
    duration = max(0.5, len(text) * 0.15)
    sample_rate = 24000
    num_samples = int(duration * sample_rate)
    out = Path(output or f"/tmp/tts_mock_{int(time.time())}.wav")

    with wave.open(str(out), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_samples)

    return {
        "audio_path": str(out), "text": text,
        "voice_used": voice, "mock": True,
        "duration_sec": round(duration, 2),
        "sample_rate": sample_rate,
    }


def batch_synth(script: Dict) -> Dict[str, Any]:
    """Batch TTS for all scenes in a script."""
    results = []
    for scene in script.get("scenes", []):
        dialogue = scene.get("dialogue", "")
        if not dialogue:
            continue
        conf = script.get("tts_config", {})
        r = synthesize_voice(
            text=dialogue,
            voice=conf.get("voice_style", "baby_f01"),
            speed=conf.get("speed", 1.0),
            output=f"/tmp/scene_{scene['id']}.wav",
        )
        r["scene_id"] = scene["id"]
        r["planned_duration"] = scene.get("duration_sec", 0)
        results.append(r)

    return {
        "total_scenes": len(results),
        "results": results,
        "all_generated": all(r.get("audio_path") for r in results),
    }


def main():
    parser = argparse.ArgumentParser(description="TTS voice synthesis")
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--voice", default="baby_f01", choices=list(VOICES.keys()))
    parser.add_argument("--speed", type=float)
    parser.add_argument("--pitch", type=int)
    parser.add_argument("--script", help="Script JSON file (batch mode)")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--no-mock", action="store_true", help="Use real gateway")
    args = parser.parse_args()

    global MOCK_MODE
    MOCK_MODE = not args.no_mock

    if args.script:
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
        result = batch_synth(script)
    elif args.text:
        result = synthesize_voice(args.text, args.voice, args.speed, args.pitch, args.output)
    else:
        parser.error("Need --text or --script")
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
