import json, subprocess, textwrap, os

data = json.load(open("storyboard.json"))
storyboard = data["storyboard"]

def srt_time(t):
    h = int(t // 3600); t -= h*3600
    m = int(t // 60); t -= m*60
    s = int(t)
    ms = int(round((t - s) * 1000))
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# ---------- captions.srt ----------
cursor = 0.0
srt_lines = []
for i, scene in enumerate(storyboard, start=1):
    start = cursor
    end = cursor + scene["duration"]
    srt_lines.append(str(i))
    srt_lines.append(f"{srt_time(start)} --> {srt_time(end)}")
    srt_lines.append(scene["narration"])
    srt_lines.append("")
    cursor = end

with open("captions/captions.srt", "w") as f:
    f.write("\n".join(srt_lines))

print(f"Total reel duration: {cursor:.1f}s")

# ---------- per-scene clip: image + audio, burned caption via drawtext ----------
clips = []
for scene in storyboard:
    sid = scene["id"]
    img = f"scenes/scene{sid}.png"
    wav = f"audio/scene{sid}.wav"
    out = f"scenes/clip{sid}.mp4"

    wrapped = textwrap.fill(scene["narration"], width=48)
    # escape for ffmpeg drawtext
    wrapped_escaped = wrapped.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019")
    draw = (
        f"drawtext=text='{wrapped_escaped}':fontcolor=white:fontsize=26:"
        f"x=(w-text_w)/2:y=h-180:line_spacing=8:"
        f"box=1:boxcolor=black@0.55:boxborderw=14"
    )

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", img, "-i", wav,
        "-vf", f"{draw},format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(scene["duration"]),
        "-shortest",
        out
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    clips.append(out)
    print(f"clip {sid} built ({scene['duration']}s)")

# ---------- concat ----------
list_path = "scenes/concat_list.txt"
with open(list_path, "w") as f:
    for c in clips:
        f.write(f"file '{os.path.abspath(c)}'\n")

final_out = "RepoGenie_FoodOrderingWebApp_Reel.mp4"
cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
       "-c", "copy", final_out]
subprocess.run(cmd, check=True, capture_output=True)
print("Final reel saved:", final_out)
