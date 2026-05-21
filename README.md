# BiRAGAS · The Three Rights

**Edition:** MMXXVI · 56 slides · ~14 minutes narrated · Ayass BioScience
**Reference:** https://mayasss-gif.github.io/BiRAGAS-Tailored-Drug-Treatment

## How to open

**Easiest** — double-click **`Launch BiRAGAS.app`** in Finder. It silently starts a local server on port 8765 and opens the deck in your default browser. Nothing else to manage.

**Alternative** — double-click `launch.command` (opens Terminal; close it to stop the server). If macOS flags the `.command` file, right-click → Open → confirm.

**Manual** — from this folder:
```bash
python3 -m http.server 8765
```
then visit http://localhost:8765/

> Opening `index.html` directly via `file://` will fail to load audio + slides.json on most modern browsers (CORS). Always serve over http (the launchers do this for you).

## Keyboard controls

| Key | Action |
|---|---|
| `→` or `Space` | Next slide |
| `←` | Previous slide |
| `P` | Play / pause narration |
| `R` | Replay narration |
| `A` | Toggle auto-advance |
| `F` | Fullscreen |
| `Home` / `End` | Jump to first / last slide |
| Click headline | Replay narration |

## Structure

- **Front matter (5)** — Cover, Manifesto, Executive Summary, The Three Wrongs framework, Thesis
- **Chapter I · Wrong Target (15)** — Diagnosis → Correction → 8 modules → Consequence
- **Chapter II · Wrong Patient (14)** — Diagnosis → Correction → 9 modules → Consequence
- **Chapter III · Wrong Analysis (16)** — Diagnosis → Correction → 11 modules → Consequence
- **Close (6)** — Three Rights, Causion agent, Pipeline, Ask, Thesis, Sign-off

All 28 BiRAGAS modules from `Shahbaz/Zip Data (2)/` are mapped to one of the three Wrongs.

## Files

```
Presentation/
├── index.html        # the deck
├── styles.css        # cream-paper + mulberry/chartreuse/cyan/hot-pink editorial theme
├── slides.json       # 56 slide definitions + narration scripts
├── audio/            # 56 TTS MP3s (Ava Multilingual Neural)
├── launch.command    # double-click to serve & open
└── README.md         # this file
```

## Editing

- **Slide content / order** — edit `slides.json`, refresh browser.
- **Narration** — edit each slide's `narration` field, then re-generate MP3s. Quick one-liner from this folder:
  ```bash
  /Users/mohamadammarayass/Desktop/Ayass\ _\ Strategic\ Planning/BiRAGAS_SKILLS/venv/bin/python3 -c "
  import json, asyncio, edge_tts, pathlib
  slides = json.loads(pathlib.Path('slides.json').read_text())['slides']
  async def gen(s):
      out = pathlib.Path('audio') / f\"slide_{s['n']:02d}.mp3\"
      await edge_tts.Communicate(s['narration'], 'en-US-AvaMultilingualNeural').save(str(out))
  asyncio.run(asyncio.gather(*(gen(s) for s in slides)))
  "
  ```
- **Theme tokens** — `styles.css` `:root` block holds the palette.
