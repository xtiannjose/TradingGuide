# Workflow: study a new video

Goal: turn a video into notes, merge the rules into `strategy/strategy.md`, rebuild the guide, publish. Work in a folder outside the repo (called `<work>` here, for example `D:\trading-work\<video-id>`). Downloads, frames and detailed notes stay there.

## 1. Check the machine

```powershell
.\scripts\setup.ps1
```

## 2. Get the report (captions + frames)

```powershell
.\scripts\study-video.ps1 -Url https://www.youtube.com/watch?v=VIDEOID -OutDir <work>\VIDEOID
```

This writes `report.md` (header, frame list, full transcript) and keeps the downloaded video and frames under `<work>\VIDEOID\watch-*`. A 10-hour video takes a long time to download and scan; run it in the background.

Short video (under about 15 minutes): read `report.md`, view the frames it lists, and skip to step 5.

## 3. Split a long transcript

YouTube auto-captions repeat every line. `segment.py` removes the repeats and cuts the transcript into parts.

```powershell
python scripts\segment.py --chapters <work>\VIDEOID\watch-*\download\run-*\video.info.json   # optional: print chapter times
python scripts\segment.py <work>\VIDEOID\report.md <work>\VIDEOID\segments --minutes 50
# or cut at chapter times:  --cuts 0:56:08,1:29:13,2:15:14
```

Output: `seg_A.txt`, `seg_B.txt`, and so on, each line `[H:MM:SS] text`. Aim for parts of 6,000 to 16,000 words.

Chapter titles can be wrong about content (video 1's "Confluence Trading" was market-structure basics), so cut by time, not by title, unless the titles prove right.

## 4. Study each part (agents, in waves)

Use the template in `docs/AGENT-PROMPT.md`, one agent per part. Rules learned the hard way:

- **At most 4 agents at a time.** Twelve at once hit the account session limit (HTTP 429) and all died. Start the next one as each finishes.
- Each agent must **write its notes file first**, then view **at most 12** frames to confirm key chart moments (extract with `ffmpeg -ss H:MM:SS -i video.mp4 -frames:v 1 -vf scale=1280:-2 out.jpg`).
- If agents die on a limit, resume them one at a time with a message such as "write the notes now, then view at most 12 frames". They keep their context.
- Notes go in `<work>\VIDEOID\notes\seg_X.md` with the 8 sections in the template. Notes stay local.

## 5. Merge into the strategy

Read the notes (sections 3, 4, 6 and 8 matter most). Then edit `strategy/strategy.md`:

- Add or change rules with citations `[PART mm:ss]`. Mark anything you filled in yourself "(app default)".
- Where the new video agrees, say so. Where it differs, keep both and add a row to the conflicts table. Add a "changed by video N" line.
- Move newly answered items out of section 7 (gaps); add new gaps.
- Add the video to `docs/VIDEOS.md` with its part table.

## 6. Update and rebuild the guide

The guide text lives in `guide-src/build.py` (part bodies are HTML strings) and the diagrams in `guide-src/diagrams.py`.

```powershell
python guide-src\make.py Confluence-Trading-Guide.pdf
```

Then check the result: render the pages to images (`pymupdf`), look at every diagram and at the first page of each part, and fix overlapping labels, clipped text and near-empty pages. Keep the guide simple: one idea per paragraph, a picture for each rule, an example where one exists.

## 7. Publish

```powershell
git add -A
git commit -m "Add video N to strategy and guide"
git push
```

Update `README.md` status and the memory notes if you keep any. Never commit videos, transcripts, keys or `.env` files (`.gitignore` blocks the common ones).
