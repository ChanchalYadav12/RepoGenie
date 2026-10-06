import json, subprocess, os

data = json.load(open("storyboard.json"))
storyboard = data["storyboard"]

os.makedirs("audio", exist_ok=True)

for scene in storyboard:
    out = f"audio/scene{scene['id']}.wav"
    # -s 150 = words per minute (slower, clearer); -p 40 pitch; -g 8 gap between words (ms)
    subprocess.run(
        ["espeak-ng", "-s", "150", "-p", "42", "-g", "6", "-v", "en-us",
         scene["narration"], "-w", out],
        check=True, capture_output=True
    )
    # get duration
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", out],
        capture_output=True, text=True
    )
    dur = float(probe.stdout.strip())
    scene["duration"] = round(dur + 0.6, 2)  # pad half a second of breathing room
    print(f"scene {scene['id']}: {dur:.2f}s audio -> {scene['duration']}s with padding")

with open("storyboard.json", "w") as f:
    json.dump(data, f, indent=2)
