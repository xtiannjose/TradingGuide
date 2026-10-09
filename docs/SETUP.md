# Setup

One-time setup on a Windows machine. Run `.\scripts\setup.ps1` first: it checks everything below and prints the fix for anything missing. `.\scripts\setup.ps1 -Install` installs what it can.

## Tools

| Tool | Why | Install |
|---|---|---|
| Python 3.12 | all scripts | `winget install --id Python.Python.3.12 --exact` |
| yt-dlp | download videos and captions | `winget install --id yt-dlp.yt-dlp --exact` |
| Deno | lets yt-dlp handle YouTube's player | `winget install --id DenoLand.Deno --exact` |
| FFmpeg | frame extraction | `winget install --id Gyan.FFmpeg --exact` |
| git, GitHub CLI | publish to GitHub | `winget install --id Git.Git --exact`, `winget install --id GitHub.cli --exact` |
| Microsoft Edge | prints the guide to PDF (headless) | ships with Windows 11 |
| `pymupdf` (Python) | reads and renders PDFs for checks | `python -m pip install --user -r requirements.txt` |

If `winget` says "No available upgrade found", the tool is already installed and current.

## The `watch` plugin (video to captions and frames)

In Claude Code:

```
/plugin marketplace add bradautomates/claude-video
/plugin install watch@claude-video
/reload-plugins
```

Then set the local engine, which needs no API key and sends nothing to Google:

```powershell
python "$env:USERPROFILE\.claude\plugins\cache\claude-video\watch\<version>\skills\watch\scripts\setup.py" --engine local
```

`setup.ps1` finds that path for you. The config lives in `%USERPROFILE%\.config\watch\.env`.

Notes:

- The skill lets you pick `gemini` (needs a free key from Google AI Studio) or `local`. This project uses `local`. A `GEMINI_API_KEY` environment variable that is wrong makes the Gemini engine fail with `HTTP 400: API key not valid`; it does not affect `--engine local`.
- Captions come first. If a video has no captions, the local engine can use WhisperX (a large one-time download) or a cloud key; this project has not needed it.
- Reports above about 2 MB (very long videos) are fine to write to a file, but too large to read in one go. Split them with `scripts/segment.py`.

## GitHub

```powershell
gh auth login      # once
gh auth status
```

## Windows notes that bit us

- PowerShell 5.1 `>` can write UTF-16. `study-video.ps1` sets UTF-8 and writes the report with `Set-Content -Encoding UTF8`.
- Python's stdout in a pipe can fail on emoji (cp1252). Scripts set `PYTHONUTF8=1`.
- Edge headless prints to PDF: `msedge --headless=new --no-pdf-header-footer --print-to-pdf=out.pdf file:///path/guide.html`. `guide-src/make.py` does this and fills the contents page numbers in two passes.
