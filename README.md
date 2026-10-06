# RepoGenie — Pipeline Proof of Concept

This is a runnable prototype of the RepoGenie pipeline, built to check whether the
design actually works against real repositories before building the full product.
It is **not** the final product — it proves the mechanics of each pipeline stage.

Everything here ran for real, on two real GitHub repositories. No step is faked or
pre-recorded. Run the commands below yourself and you'll get the same output.

---

## What's real vs. what's stubbed (say this out loud to your prof)

| Stage | What this prototype does | What production would use instead |
|---|---|---|
| Fetch, Analyze, Parse, Chunk | **Real.** Actual `git clone`, Python `ast` module, regex parsing, real file classification | Same, possibly + Tree-sitter for more languages |
| Embeddings + FAISS | **Stubbed.** Uses TF-IDF (`scikit-learn`) because this environment has no API key and can't download embedding models | OpenAI/Sentence-Transformers embeddings + FAISS |
| Script generation | **Stubbed.** Rule-based template filled in with real analysis results, not an LLM | GPT-4 class model writing the script |
| Voice | **Real, but low quality.** `espeak-ng`, a fully offline, free TTS engine | ElevenLabs / OpenAI TTS / Google Cloud TTS |
| Visuals, captions, video assembly | **Fully real.** `matplotlib`, `pygments`, `ffmpeg` — exactly as the pipeline design specifies | Same tools, same approach |

Be upfront about this table if asked — it's the honest, defensible version of "we
tested it," and it's a stronger answer than pretending every stage used a paid AI
service you don't have keys for yet.

---

## 1. Install dependencies (one-time setup)

```bash
# System tools
sudo apt-get update
sudo apt-get install -y ffmpeg espeak-ng git

# Python packages
pip install scikit-learn matplotlib pygments
```

## 2. Clone a repository to test

```bash
git clone https://github.com/ritchi-e/Food_ordering_WebAPP.git repo_food
```

## 3. Run each pipeline stage, in order

```bash
# Stage 1: Repository Checker -> Fetch -> Analyzer -> Code Parser -> Chunking -> (TF-IDF) Retrieval
python3 1_analyze_repo.py repo_food Food_ordering_WebAPP \
    "where is user authentication handled" \
    "how are orders placed and tracked" \
    "where is the shopping cart logic"
```
This clones nothing itself (you already cloned in step 2) — it walks the repo,
classifies every file as source/doc/config/asset, parses functions and classes
out of the source files, builds a TF-IDF index over the resulting chunks, and
runs your example questions against it, printing the best-matching file and
function for each. This is the step that proves retrieval actually finds the
right code.

```bash
# Stage 2: Reel Generation - Script + Storyboard
python3 2_generate_script.py
```
Builds `storyboard.json` — seven scenes, each with narration text and a named
visual requirement. The narration text here is template-filled from the real
module list and file counts found in step 1, not written by an LLM.

```bash
# Stage 3: Reel Generation - Visuals
python3 3_generate_visuals.py
```
Renders one PNG per scene into `scenes/`: a title card, an architecture diagram,
a module grid, a data-flow diagram, and a real syntax-highlighted snippet pulled
directly from the cloned repo's `backend/middleware/auth.py`.

```bash
# Stage 4: Reel Generation - Voice
python3 4_generate_voice.py
```
Synthesizes narration audio for every scene with `espeak-ng` (fully offline — no
API, no internet needed) and measures each clip's real duration so later scenes
can be timed to match.

```bash
# Stage 5: Video Assembly
python3 5_assemble_video.py
```
Builds an `.srt` caption file, burns captions onto each scene image with
`ffmpeg`'s `drawtext` filter, pairs each image with its narration audio, and
concatenates all seven scenes into one MP4.

Your final reel appears as `RepoGenie_FoodOrderingWebApp_Reel.mp4` in this folder.

---

## 4. What to actually show your professor

Don't just press play on the finished video. Open a terminal, `cd` into this
folder, and run the five commands above live (or screen-record yourself doing
it once beforehand). Watching `ffmpeg` actually synthesize a video from a repo
you just cloned in front of him is a far stronger demo than any finished file —
it proves the pipeline, not just that a video exists.

A good script for the walkthrough:

1. `git clone` a repo of his choosing, live
2. Run stage 1 and point out the retrieval results matching real files
3. Run stages 2–5 back to back (~20 seconds total)
4. Play the resulting `.mp4`

If he asks "why does the narration sound robotic" or "why isn't this GPT-4", the
table at the top of this file is your honest answer: this is a structural proof
of concept, not the final polished product, because the final product needs paid
API keys this environment doesn't have.

---

## Files in this folder

| File | Pipeline stage |
|---|---|
| `1_analyze_repo.py` | Repository Checker, Fetch, Analyzer, Parser, Chunking, Retrieval |
| `2_generate_script.py` | Script + Storyboard generation |
| `3_generate_visuals.py` | Visual generation (architecture diagrams, code snippets) |
| `4_generate_voice.py` | Voice / narration generation |
| `5_assemble_video.py` | Captions + Video Assembly |
