#!/usr/bin/env python3
"""Build index.html for BiRAGAS · The Three Rights — sibling to mayasss-gif.github.io/BiRAGAS-Tailored-Drug-Treatment.

Reads slides.json and emits a single static index.html with 56 hand-rendered <section>s
matching the reference HTML's exact CSS + JS architecture. Re-run after editing slides.json.
"""

import json
import re
import html
import pathlib

BASE = pathlib.Path(__file__).parent
SLIDES = json.loads((BASE / "slides.json").read_text())


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────────────────────

NUM_PATTERNS = [
    r"\$\d+\.?\d*\s*B?(?:illion)?",
    r"\d+\.?\d*\s*billion",
    r"\d+\.?\d*\s*million",
    r"\d+(?:\.\d+)?%",
    r"\d+\+?\s*(?:years?|yrs?)",
    r"\d+\+?\s*modules?",
    r"\d+\+?\s*(?:engines?|workflows?|tiers?|rights?|wrongs?|steps?)",
    r"\b(?:eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|twenty-one|twenty-two|twenty-three|twenty-four|twenty-five|twenty-six|twenty-seven|twenty-eight|fourteen|forty|seventy|ninety)\b",
    r"\b\d+(?:[,\.]\d+)?\b",
]
NUM_RE = re.compile("|".join(NUM_PATTERNS), re.IGNORECASE)

EM_KEYWORDS = [
    "wrong target", "wrong patient", "wrong analysis", "right target", "right patient", "right analysis",
    "causation", "correlation", "mechanism", "Pearl's", "Causal Confidence Score", "Causion",
    "FDA-ready", "FDA-aligned", "auditable", "defensible",
    "mechanism over correlation", "patient over average", "causation over coincidence",
    "actual story", "infrastructure", "the moat", "revenue", "lock-in",
]


def esc(s):
    return html.escape(str(s or ""))


def emphasize(text):
    """Wrap key phrases in <em> and numerals in <span class='num'>."""
    if not text:
        return ""
    out = esc(text)
    # wrap numbers first (more specific)
    out = NUM_RE.sub(lambda m: f'<span class="num">{m.group(0)}</span>', out)
    # wrap key italic phrases
    for kw in EM_KEYWORDS:
        pattern = re.compile(r"\b(" + re.escape(kw) + r")\b", re.IGNORECASE)
        out = pattern.sub(r'<em>\1</em>', out)
    return out


def split_into_sentences(text):
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def lede_pull_side(s):
    """Derive (lede, pull, side) from body + narration."""
    body = s.get("body", "")
    narration = s.get("narration", "")
    # Prefer body for visible content; narration is the audio script
    primary = body or narration
    secondary = narration if body else ""

    sents = split_into_sentences(primary)
    if not sents:
        return "", "", ""

    # one-sentence body → lede only
    if len(sents) == 1:
        # try narration second sentence as pull
        narr_sents = split_into_sentences(secondary)
        pull = narr_sents[1] if len(narr_sents) > 1 else ""
        return sents[0], pull, ""

    # 2-3 sentences: lede = 1st, side = rest, pull = pick a punchy short one
    if len(sents) <= 3:
        lede = sents[0]
        rest = sents[1:]
        pull_idx = max(range(len(rest)), key=lambda i: -abs(len(rest[i].split()) - 14))
        pull = rest[pull_idx]
        side_sentences = [s for i, s in enumerate(rest) if i != pull_idx]
        return lede, pull, " ".join(side_sentences)

    # 4+ sentences: lede = first 1-2, pull = punchy middle sentence, side = rest
    lede_n = 1 if len(sents[0].split()) >= 18 else 2
    lede = " ".join(sents[:lede_n])
    rest = sents[lede_n:]
    pull_idx = max(range(len(rest)), key=lambda i: -abs(len(rest[i].split()) - 14))
    pull = rest[pull_idx]
    side_sentences = [s for i, s in enumerate(rest) if i != pull_idx]
    return lede, pull, " ".join(side_sentences)


def splash_title(title):
    """Wrap the last word/phrase in a red splash block. Period gets absorbed."""
    if not title:
        return ""
    words = title.strip().split()
    if len(words) == 1:
        return f'<span class="splash">{esc(words[0])}</span>'
    head = " ".join(words[:-1])
    tail = words[-1]
    return f'{esc(head)} <span class="splash">{esc(tail)}</span>'


def chapter_pill(chapter):
    return {"FRONT": "FRONT MATTER", "CH I": "CHAPTER 01", "CH II": "CHAPTER 02", "CH III": "CHAPTER 03", "CLOSE": "CLOSING"}.get(chapter, chapter)


def folio(s, page_label):
    """Top folio bar: page # · CHAPTER · accent pill."""
    return f'''<div class="folio">
    <div>p. {s['n']:02d} · {esc(chapter_pill(s.get('chapter','')))} · BIRAGAS</div>
    <div><span class="pill accent">{esc(s.get('stamp',''))}</span></div>
  </div>'''


def corners():
    return '<div class="corner tl"></div><div class="corner tr"></div><div class="corner bl"></div><div class="corner br"></div>'


# ──────────────────────────────────────────────────────────────────────────────
#  Per-kind templates
# ──────────────────────────────────────────────────────────────────────────────

def render_cover(s):
    audio = f"audio/slide_{s['n']:02d}.mp3"
    return f'''<section class="slide active" data-audio="{audio}" data-label="{esc(s['title'])}">
  <div class="spread cover">
    {corners()}
    <div class="eyebrow">Ayass BioScience · BiRAGAS Platform · MMXXVI</div>
    <h1>BiRAGAS<br>The Three <span class="splash">Rights.</span></h1>
    <div class="sub">Every <span class="acc">wrong target</span>. Every <span class="acc">wrong patient</span>. Every <span class="acc">wrong analysis</span>. We fix all three.</div>
    <div class="meta-row">
      <span class="pill red">EVIDENCE PLATFORM</span>
      <span>The right target · The right patient · The right analysis</span>
      <span class="pill">28 MODULES</span>
    </div>
  </div>
</section>'''


def render_close(s):
    """Final slide — dark close-slide layout, like the reference."""
    audio = f"audio/slide_{s['n']:02d}.mp3"
    title = s.get("title", "Ayass BioScience")
    sub = s.get("subtitle", "MMXXVI")
    return f'''<section class="slide" data-audio="{audio}" data-label="{esc(title)}">
  <div class="spread close-slide">
    {corners()}
    <div class="eyebrow">— THE EDITORS' NOTE · BIRAGAS · MMXXVI —</div>
    <div class="manifesto">We are not building another AI.</div>
    <div class="manifesto next">We are building the <span class="acc">infrastructure</span><span class="period"></span></div>
    <div class="tag">{esc(title)} · {esc(sub)} · BIRAGAS</div>
  </div>
</section>'''


def render_chapter(s):
    """Chapter title cards — body-slide style but bigger headline."""
    audio = f"audio/slide_{s['n']:02d}.mp3"
    return f'''<section class="slide" data-audio="{audio}" data-label="{esc(s['title'] + ' · ' + s.get('subtitle',''))}">
  <div class="spread body-slide" style="--accent:var(--red)">
    {corners()}
    {folio(s, 'CHAPTER')}
    <div class="eyebrow">— Chapter {{ romans(s.n) }} —</div>
    <h2>{esc(s.get('subtitle','').rstrip('.'))} <span class="splash">every time.</span></h2>
    <div class="body-grid single">
      <div class="lede">A complete causal chapter of the BiRAGAS platform — diagnosis of the failure, correction of the mechanism, consequence for the field.</div>
    </div>
    <div class="audio-hint">click headline to replay narration</div>
  </div>
</section>'''


def render_framework(s):
    """The Three Wrongs grid — 3 cards inside a body-slide."""
    audio = f"audio/slide_{s['n']:02d}.mp3"
    cards = ""
    for w in s.get("wrongs", []):
        cards += f'''<div class="card">
        <div class="num">{esc(w['n'])}</div>
        <div class="card-label">{esc(w['label'])}</div>
        <div class="card-desc">{esc(w['desc'])}</div>
      </div>'''
    return f'''<section class="slide" data-audio="{audio}" data-label="{esc(s['title'])}">
  <div class="spread body-slide" style="--accent:var(--red)">
    {corners()}
    {folio(s, 'FRAMEWORK')}
    <div class="eyebrow">— Three failures, one platform —</div>
    <h2>The <em>Three</em> <span class="splash">Wrongs.</span></h2>
    <div class="cards-3">{cards}</div>
    <div class="audio-hint">click headline to replay narration</div>
  </div>
</section>'''


def render_rights(s):
    """The Three Rights grid (mirror of framework, accent green/mustard for the corrected side)."""
    audio = f"audio/slide_{s['n']:02d}.mp3"
    cards = ""
    accent_classes = ["red", "mustard", "cobalt"]
    for i, r in enumerate(s.get("rights", [])):
        cls = accent_classes[i % 3]
        cards += f'''<div class="card right-card {cls}">
        <div class="num">{esc(r['n'])}</div>
        <div class="card-label">{esc(r['label'])}</div>
        <div class="card-desc">{esc(r['desc'])}</div>
      </div>'''
    return f'''<section class="slide" data-audio="{audio}" data-label="{esc(s['title'])}">
  <div class="spread body-slide" style="--accent:var(--mustard)">
    {corners()}
    {folio(s, 'CLOSING')}
    <div class="eyebrow">— Three corrections, one platform —</div>
    <h2>The <em>Three</em> <span class="splash">Rights.</span></h2>
    <div class="cards-3">{cards}</div>
    <div class="audio-hint">click headline to replay narration</div>
  </div>
</section>'''


def render_pipeline(s):
    audio = f"audio/slide_{s['n']:02d}.mp3"
    steps = s.get("steps", [])
    nodes = []
    for i, step in enumerate(steps):
        last = (i == len(steps) - 1)
        cls = "pipe-node dossier" if last else "pipe-node"
        nodes.append(f'<div class="{cls}">{esc(step)}</div>')
        if not last:
            nodes.append('<span class="pipe-arrow">→</span>')
    flow = "".join(nodes)
    lede, pull, side = lede_pull_side(s)
    return f'''<section class="slide" data-audio="{audio}" data-label="{esc(s['title'])}">
  <div class="spread body-slide" style="--accent:var(--mustard)">
    {corners()}
    {folio(s, 'PIPELINE')}
    <div class="eyebrow">— FASTQ to FDA-ready dossier —</div>
    <h2>The <em>Six-Step</em> <span class="splash">Pipeline.</span></h2>
    <div class="pipeline-flow">{flow}</div>
    <div class="body-grid single">
      <div class="lede">{emphasize(lede)}</div>
    </div>
    <div class="audio-hint">click headline to replay narration</div>
  </div>
</section>'''


def render_ask(s):
    audio = f"audio/slide_{s['n']:02d}.mp3"
    rows = ""
    for item in s.get("items", []):
        rows += f'''<div class="ask-row">
          <div class="k">{esc(item['k'])}</div>
          <div class="v">{emphasize(item['v'])}</div>
        </div>'''
    return f'''<section class="slide" data-audio="{audio}" data-label="{esc(s['title'])}">
  <div class="spread body-slide" style="--accent:var(--cobalt)">
    {corners()}
    {folio(s, 'THE ASK')}
    <div class="eyebrow">— Three doors. One platform. —</div>
    <h2>The <span class="splash">Ask.</span></h2>
    <div class="ask-grid">{rows}</div>
    <div class="audio-hint">click headline to replay narration</div>
  </div>
</section>'''


def render_body(s, accent="red"):
    """The default body-slide: folio · eyebrow · h2 · lede + pull + side."""
    audio = f"audio/slide_{s['n']:02d}.mp3"
    lede, pull, side = lede_pull_side(s)
    title = s.get("title", "")
    eyebrow_text = {
        "diagnosis": "— The diagnosis —",
        "problem": "— The problem —",
        "cost": "— The cost —",
        "correction": "— The correction —",
        "consequence": "— The consequence —",
        "math": "— The mathematics —",
        "manifesto": "— The manifesto —",
        "thesis": "— The thesis —",
        "summary": "— Executive summary —",
        "agent": "— The natural-language layer —",
    }.get(s.get("kind"), f"— {esc(s.get('chapter',''))} —")

    pull_html = f'<div class="pull">{emphasize(pull)}</div>' if pull else ""
    side_html = f'<div>{emphasize(side)}</div>' if side else ""
    side_block = f'<div class="side">{pull_html}{side_html}</div>' if (pull_html or side_html) else ""
    grid_cls = "body-grid" if side_block else "body-grid single"

    return f'''<section class="slide" data-audio="{audio}" data-label="{esc(title)}">
  <div class="spread body-slide" style="--accent:var(--{accent})">
    {corners()}
    {folio(s, '')}
    <div class="eyebrow">{eyebrow_text}</div>
    <h2>{splash_title(title)}</h2>
    <div class="{grid_cls}">
      <div class="lede">{emphasize(lede)}</div>
      {side_block}
    </div>
    <div class="audio-hint">click headline to replay narration</div>
  </div>
</section>'''


def render_module(s):
    """Module slides — same body-slide but with cobalt accent + module tag."""
    audio = f"audio/slide_{s['n']:02d}.mp3"
    lede, pull, side = lede_pull_side(s)
    pull_html = f'<div class="pull">{emphasize(pull)}</div>' if pull else ""
    side_html = f'<div>{emphasize(side)}</div>' if side else ""
    side_block = f'<div class="side">{pull_html}{side_html}</div>' if (pull_html or side_html) else ""
    grid_cls = "body-grid" if side_block else "body-grid single"
    return f'''<section class="slide" data-audio="{audio}" data-label="{esc(s['title'])}">
  <div class="spread body-slide" style="--accent:var(--cobalt)">
    {corners()}
    {folio(s, 'MODULE')}
    <div class="eyebrow">— Production module —</div>
    <h2>{splash_title(s['title'])}</h2>
    <div class="{grid_cls}">
      <div class="lede">{emphasize(lede)}</div>
      {side_block}
    </div>
    <div class="audio-hint">click headline to replay narration</div>
  </div>
</section>'''


# ──────────────────────────────────────────────────────────────────────────────
#  Dispatch
# ──────────────────────────────────────────────────────────────────────────────

def render(s):
    k = s.get("kind", "")
    if k == "cover":
        return render_cover(s)
    if k == "close":
        return render_close(s)
    if k == "chapter":
        return render_chapter(s)
    if k == "framework":
        return render_framework(s)
    if k == "rights":
        return render_rights(s)
    if k == "pipeline":
        return render_pipeline(s)
    if k == "ask":
        return render_ask(s)
    if k == "module":
        return render_module(s)
    # diagnosis/correction/consequence/problem/cost/math/manifesto/thesis/summary/agent → body-slide
    accent = "red"
    if k in {"correction", "consequence"}:
        accent = "red"
    elif k in {"summary", "thesis", "manifesto", "agent"}:
        accent = "mustard"
    return render_body(s, accent=accent)


def build():
    sections = []
    for s in SLIDES["slides"]:
        sections.append(render(s))
    sections_html = "\n".join(sections)
    out = TEMPLATE.replace("{{SECTIONS}}", sections_html).replace("{{TOTAL}}", str(len(SLIDES["slides"])))
    (BASE / "index.html").write_text(out)
    print(f"Wrote index.html with {len(SLIDES['slides'])} sections")


# ──────────────────────────────────────────────────────────────────────────────
#  HTML template (CSS + JS verbatim from the reference, content-injected)
# ──────────────────────────────────────────────────────────────────────────────

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0F0F0F">
<title>BiRAGAS · The Three Rights · Ayass BioScience · MMXXVI</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,300..900,0..100,0..1;1,9..144,300..900,0..100,0..1&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#F4EFE7; --paper-deep:#E8E0CF; --paper-soft:#FAF6EE;
  --ink:#0F0F0F; --ink-soft:#2A2A2A; --rule:#11111122;
  --red:#E63946; --red-deep:#B82C36; --mustard:#D4A017; --cobalt:#1E40AF;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--paper);color:var(--ink);font-family:"Newsreader",Georgia,serif;font-size:18px;line-height:1.55;overflow:hidden}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:200;opacity:0.42;mix-blend-mode:multiply;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.78' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.08 0 0 0 0 0.07 0 0 0 0 0.06 0 0 0 0.55 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");background-size:300px 300px}

.deck{position:fixed;inset:0;display:flex;flex-direction:column}
.masthead{flex-shrink:0;background:var(--ink);color:var(--paper);padding:10px 36px;display:flex;justify-content:space-between;align-items:center;gap:24px;font-family:"DM Mono",ui-monospace,monospace;font-size:12px;letter-spacing:0.22em;text-transform:uppercase;z-index:50}
.masthead .brand{display:flex;gap:18px;align-items:center}
.masthead .brand .b{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 96,"wght" 700,"SOFT" 50,"WONK" 1;font-size:22px;text-transform:none;letter-spacing:-0.02em;color:var(--paper)}
.masthead .brand .b .dot{color:var(--red)}
.masthead .meta{color:#e8e0cfaa}
.masthead .controls{display:flex;gap:10px}
.btn{background:transparent;color:var(--paper);border:1px solid #ffffff55;padding:5px 12px;font-family:"DM Mono";font-size:11px;letter-spacing:0.18em;text-transform:uppercase;cursor:pointer;transition:all 0.18s}
.btn:hover{background:var(--paper);color:var(--ink);border-color:var(--paper)}
.btn.on{background:var(--red);color:var(--paper);border-color:var(--red)}
.btn .dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:currentColor;margin-right:6px;vertical-align:middle}
.btn.on .dot{background:var(--paper);animation:blink 1.2s steps(2) infinite}
@keyframes blink{50%{opacity:0.2}}

.stage{flex:1;position:relative;overflow:hidden}
.slide{position:absolute;inset:0;opacity:0;visibility:hidden;transition:opacity 0.5s ease;overflow-y:auto}
.slide.active{opacity:1;visibility:visible}

.footer{flex-shrink:0;background:var(--paper-deep);border-top:1px solid var(--ink);padding:10px 36px;display:flex;align-items:center;gap:24px;font-family:"DM Mono";font-size:12px;letter-spacing:0.18em;text-transform:uppercase;z-index:50}
.footer .nav-btn{background:var(--ink);color:var(--paper);border:none;padding:6px 16px;font-family:"DM Mono";font-size:14px;letter-spacing:0.18em;cursor:pointer;transition:background 0.18s}
.footer .nav-btn:disabled{background:#888;cursor:not-allowed}
.footer .nav-btn:hover:not(:disabled){background:var(--red)}
.footer .counter{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 36,"wght" 600;font-size:24px;letter-spacing:-0.01em;min-width:90px;text-align:center}
.footer .counter .of{color:var(--red);margin:0 6px}
.footer .progress{flex:1;height:4px;background:#0001;position:relative;overflow:hidden}
.footer .bar{position:absolute;left:0;top:0;height:100%;background:var(--red);transition:width 0.35s ease}
.footer .scrubber{display:flex;gap:4px;max-width:42%;overflow:hidden}
.footer .pip{width:8px;height:8px;background:#0002;cursor:pointer;transition:all 0.18s;border-radius:50%;flex-shrink:0}
.footer .pip.done{background:var(--ink)}
.footer .pip.active{background:var(--red);transform:scale(1.6)}

.spread{position:relative;width:100%;height:100%;padding:42px 80px 60px}
.folio{display:flex;justify-content:space-between;align-items:center;font-family:"DM Mono";font-size:12px;letter-spacing:0.2em;text-transform:uppercase;color:var(--ink-soft);padding-bottom:16px;border-bottom:1px solid var(--rule)}
.folio .pill{background:var(--ink);color:var(--paper);padding:3px 10px}
.folio .pill.accent{background:var(--accent,var(--red))}

.corner{position:absolute;width:30px;height:30px;border:2px solid var(--ink);pointer-events:none}
.corner.tl{top:30px;left:30px;border-right:none;border-bottom:none}
.corner.tr{top:30px;right:30px;border-left:none;border-bottom:none}
.corner.bl{bottom:48px;left:30px;border-right:none;border-top:none}
.corner.br{bottom:48px;right:30px;border-left:none;border-top:none}

/* COVER */
.cover{display:flex;flex-direction:column;justify-content:center;align-items:flex-start;text-align:left}
.cover .eyebrow{font-family:"DM Mono";font-size:14px;letter-spacing:0.32em;text-transform:uppercase;color:var(--red);margin-bottom:28px;display:flex;align-items:center;gap:14px}
.cover .eyebrow::before{content:"";width:50px;height:1px;background:var(--ink-soft)}
.cover h1{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 144,"wght" 380,"SOFT" 100,"WONK" 1;font-size:clamp(80px,10vw,168px);line-height:0.94;letter-spacing:-0.035em;color:var(--ink);margin-bottom:26px}
.cover h1 .splash{background:var(--red);color:var(--paper);padding:0 0.1em;display:inline-block;transform:rotate(-1.5deg)}
.cover .sub{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 96,"wght" 400;font-size:clamp(22px,2.4vw,42px);line-height:1.22;color:var(--ink-soft);max-width:1400px}
.cover .sub .acc{color:var(--red);font-weight:600}
.cover .meta-row{margin-top:48px;font-family:"DM Mono";font-size:13px;letter-spacing:0.28em;text-transform:uppercase;color:var(--ink-soft);display:flex;gap:18px;flex-wrap:wrap;align-items:center}
.cover .meta-row .pill{background:var(--ink);color:var(--paper);padding:3px 10px}
.cover .meta-row .pill.red{background:var(--red)}

/* BODY */
.body-slide{display:flex;flex-direction:column;padding:42px 80px 60px;height:100%}
.body-slide .eyebrow{font-family:"DM Mono";font-size:13px;letter-spacing:0.28em;text-transform:uppercase;color:var(--accent,var(--red));margin-top:14px;margin-bottom:16px;display:flex;align-items:center;gap:14px}
.body-slide h2{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 144,"wght" 480,"SOFT" 100,"WONK" 1;font-size:clamp(46px,6.4vw,108px);line-height:0.98;letter-spacing:-0.028em;color:var(--ink);margin-bottom:26px;max-width:1500px;cursor:pointer}
.body-slide h2 em{font-style:italic;color:var(--accent,var(--red))}
.body-slide h2 .splash{background:var(--accent,var(--red));color:var(--paper);padding:0 0.1em;display:inline-block;transform:rotate(-1deg)}
.body-slide .body-grid{display:grid;grid-template-columns:1.4fr 1fr;gap:48px;flex:1;align-items:start}
.body-slide .body-grid.single{grid-template-columns:1fr;max-width:1500px}
.body-slide .lede{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 96,"wght" 400;font-size:clamp(20px,2.1vw,34px);line-height:1.36;color:var(--ink);padding-left:22px;border-left:4px solid var(--accent,var(--red));max-width:1100px}
.body-slide .lede strong,.body-slide .lede em{font-style:italic;font-weight:500;color:var(--accent,var(--red))}
.body-slide .lede .num{font-family:"Fraunces";font-weight:800;font-variation-settings:"opsz" 96,"wght" 800;color:var(--accent,var(--red));font-style:normal}
.body-slide .side{font-family:"Newsreader";font-size:17px;line-height:1.58;color:var(--ink-soft)}
.body-slide .side .pull{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 96,"wght" 500;font-size:26px;line-height:1.24;color:var(--ink);margin-bottom:18px;padding-bottom:18px;border-bottom:2px solid var(--accent,var(--red))}
.body-slide .side .pull::before{content:"❡ ";color:var(--accent,var(--red));font-style:normal}
.body-slide .side em{font-style:italic;color:var(--accent,var(--red))}
.body-slide .side .num{font-family:"Fraunces";font-weight:700;color:var(--accent,var(--red));font-style:normal}
.body-slide .footnote{margin-top:24px;font-family:"DM Mono";font-size:12px;letter-spacing:0.18em;text-transform:uppercase;color:var(--ink-soft);max-width:1500px}
.body-slide .audio-hint{position:absolute;bottom:74px;right:60px;font-family:"DM Mono";font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:var(--ink-soft);opacity:0.65}
.body-slide .audio-hint::before{content:"▷ ";color:var(--accent,var(--red))}

/* CARDS — 3-up grid for framework + rights */
.cards-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px;flex:1;align-content:start}
.card{background:var(--paper-soft);border:1px solid var(--rule);padding:26px 24px;position:relative}
.card .num{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 96,"wght" 800;font-size:64px;line-height:1;color:var(--accent,var(--red));margin-bottom:12px}
.card .card-label{font-family:"DM Mono";font-size:12px;letter-spacing:0.22em;text-transform:uppercase;color:var(--ink);margin-bottom:10px}
.card .card-desc{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 36,"wght" 400;font-size:18px;line-height:1.4;color:var(--ink-soft)}
.card.right-card{border-top:6px solid var(--accent,var(--red))}
.card.right-card.red{border-top-color:var(--red)} .card.right-card.red .num{color:var(--red)}
.card.right-card.mustard{border-top-color:var(--mustard)} .card.right-card.mustard .num{color:var(--mustard)}
.card.right-card.cobalt{border-top-color:var(--cobalt)} .card.right-card.cobalt .num{color:var(--cobalt)}

/* PIPELINE */
.pipeline-flow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:8px 0 28px;padding:6px 0}
.pipe-node{font-family:"DM Mono";font-size:13px;letter-spacing:0.16em;padding:12px 20px;border:1.5px solid var(--ink);background:var(--paper-soft);color:var(--ink);text-transform:uppercase}
.pipe-node.dossier{background:var(--mustard);color:var(--ink);font-weight:700}
.pipe-arrow{font-size:22px;color:var(--accent,var(--red))}

/* ASK */
.ask-grid{display:grid;grid-template-columns:1fr;gap:0;max-width:1100px;margin-top:6px}
.ask-row{display:grid;grid-template-columns:260px 1fr;align-items:baseline;padding:18px 0;border-bottom:1px solid var(--rule)}
.ask-row .k{font-family:"DM Mono";font-size:13px;letter-spacing:0.22em;text-transform:uppercase;color:var(--accent,var(--cobalt))}
.ask-row .v{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 36,"wght" 400;font-size:22px;color:var(--ink)}

/* CLOSE */
.close-slide{background:var(--ink);color:var(--paper);display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:60px 100px}
.close-slide .corner{border-color:var(--paper)}
.close-slide .eyebrow{font-family:"DM Mono";font-size:13px;letter-spacing:0.32em;text-transform:uppercase;color:var(--red);margin-bottom:46px;display:inline-flex;gap:14px;align-items:center}
.close-slide .eyebrow::before,.close-slide .eyebrow::after{content:"";width:50px;height:1px;background:var(--red)}
.close-slide .manifesto{font-family:"Fraunces";font-style:italic;font-variation-settings:"opsz" 144,"wght" 400,"SOFT" 100,"WONK" 1;font-size:clamp(48px,6.5vw,96px);line-height:1.08;letter-spacing:-0.025em;color:var(--paper);max-width:1500px;cursor:pointer}
.close-slide .manifesto .next{margin-top:24px}
.close-slide .manifesto .acc{color:var(--red);font-weight:600}
.close-slide .manifesto .period{display:inline-block;width:0.22em;height:0.22em;background:var(--red);border-radius:50%;margin-left:0.05em;transform:translateY(0.06em)}
.close-slide .tag{margin-top:64px;font-family:"DM Mono";font-size:13px;letter-spacing:0.3em;text-transform:uppercase;color:#ffffff80}

/* NOW PLAYING */
.now-playing{position:fixed;bottom:88px;left:36px;background:var(--ink);color:var(--paper);padding:10px 16px;font-family:"DM Mono";font-size:11px;letter-spacing:0.18em;text-transform:uppercase;border-left:3px solid var(--red);display:flex;align-items:center;gap:10px;opacity:0;transform:translateY(20px);transition:all 0.3s ease;z-index:80;pointer-events:none;max-width:50%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.now-playing.on{opacity:1;transform:translateY(0)}
.now-playing .eq{display:inline-flex;gap:2px;height:14px;align-items:end;flex-shrink:0}
.now-playing .eq span{width:3px;background:var(--red);transform-origin:bottom;animation:eq 0.9s ease-in-out infinite}
.now-playing .eq span:nth-child(1){height:60%;animation-delay:0s}
.now-playing .eq span:nth-child(2){height:100%;animation-delay:0.2s}
.now-playing .eq span:nth-child(3){height:70%;animation-delay:0.4s}
.now-playing .eq span:nth-child(4){height:90%;animation-delay:0.1s}
@keyframes eq{0%,100%{transform:scaleY(0.4)}50%{transform:scaleY(1)}}

/* SIDE NAV */
.side-nav{position:fixed;top:50%;transform:translateY(-50%);z-index:70;display:flex;align-items:center;justify-content:center;width:64px;height:64px;border-radius:50%;background:rgba(15,15,15,0.72);color:var(--paper);border:2px solid rgba(244,239,231,0.45);cursor:pointer;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:background 0.22s ease,border-color 0.22s ease,box-shadow 0.22s ease,transform 0.18s ease,opacity 0.22s ease;font-family:"DM Mono",ui-monospace,monospace;font-size:34px;font-weight:300;line-height:1;padding:0;user-select:none}
.side-nav .chev{display:block;transform:translateY(-2px)}
.side-nav:hover:not(:disabled){background:var(--red);border-color:var(--red);box-shadow:0 10px 28px rgba(230,57,70,0.4);transform:translateY(-50%) scale(1.06)}
.side-nav:active:not(:disabled){transform:translateY(-50%) scale(0.94)}
.side-nav:disabled{opacity:0.22;cursor:not-allowed;pointer-events:none}
.side-nav.prev{left:24px}
.side-nav.next{right:24px}
.side-nav:focus-visible{outline:3px solid var(--red);outline-offset:4px}

.footer .nav-btn{min-width:54px;min-height:44px;font-size:20px;padding:10px 22px;display:inline-flex;align-items:center;justify-content:center}
.btn:focus-visible,.nav-btn:focus-visible{outline:3px solid var(--red);outline-offset:3px}

@media (max-width: 900px){
  html,body{font-size:17px}
  .side-nav{width:56px;height:56px;font-size:28px}
  .side-nav.prev{left:14px} .side-nav.next{right:14px}
  .spread,.body-slide{padding:30px 38px 56px}
  .cover h1{font-size:clamp(52px,9vw,120px);line-height:0.96}
  .body-slide h2{font-size:clamp(34px,6vw,84px);line-height:1.02}
  .cover .sub{font-size:clamp(20px,2.8vw,36px)}
  .body-slide .body-grid{grid-template-columns:1fr;gap:24px}
  .body-slide .lede{font-size:clamp(18px,2.6vw,28px);max-width:100%}
  .body-slide .side .pull{font-size:22px}
  .close-slide .manifesto{font-size:clamp(36px,5.6vw,72px)}
  .masthead{padding:8px 22px;font-size:11px} .masthead .brand .b{font-size:18px} .masthead .meta{display:none}
  .footer{padding:8px 22px;gap:14px} .footer .counter{font-size:18px;min-width:64px}
  .cards-3{grid-template-columns:1fr 1fr}
}
@media (max-width: 600px){
  html,body{font-size:16px;line-height:1.45}
  .side-nav{width:46px;height:46px;font-size:24px;background:rgba(15,15,15,0.78);border-width:1.5px}
  .side-nav.prev{left:8px} .side-nav.next{right:8px}
  .spread,.body-slide{padding:20px 18px 24px}
  .corner{width:22px;height:22px;border-width:1.5px}
  .corner.tl,.corner.tr{top:18px} .corner.tl{left:16px} .corner.tr{right:16px}
  .corner.bl,.corner.br{bottom:32px} .corner.bl{left:16px} .corner.br{right:16px}
  .cover{justify-content:flex-start;padding-top:6vh}
  .cover h1{font-size:clamp(40px,12vw,72px);line-height:0.98;margin-bottom:14px}
  .cover .sub{font-size:clamp(18px,5vw,28px)}
  .cover .meta-row{margin-top:24px;gap:10px;font-size:10px;letter-spacing:0.18em}
  .body-slide h2{font-size:clamp(26px,7.2vw,50px);line-height:1.04;margin-bottom:14px}
  .body-slide .eyebrow{font-size:10px}
  .body-slide .body-grid{gap:18px}
  .body-slide .lede{font-size:clamp(16px,4.2vw,22px);padding-left:14px;border-left-width:3px}
  .body-slide .side{font-size:15px}
  .body-slide .side .pull{font-size:18px;margin-bottom:12px;padding-bottom:12px}
  .body-slide .audio-hint{display:none}
  .folio{font-size:10px;flex-wrap:wrap;gap:8px}
  .close-slide{padding:30px 22px}
  .close-slide .manifesto{font-size:clamp(28px,7.6vw,46px);line-height:1.12}
  .close-slide .tag{margin-top:28px;font-size:10px}
  .masthead{padding:8px 14px;font-size:10px} .masthead .brand .b{font-size:16px} .masthead .brand span:not(.b){display:none}
  .footer{padding:8px 12px;gap:8px;font-size:11px} .footer .nav-btn{min-width:46px;min-height:42px;font-size:18px;padding:8px 14px}
  .footer .counter{font-size:15px;min-width:50px} .footer .scrubber{display:none}
  .now-playing{bottom:74px;left:10px;font-size:10px;padding:6px 10px;max-width:70%}
  .cards-3{grid-template-columns:1fr}
  .ask-row{grid-template-columns:1fr;gap:4px}
}
</style>
</head>
<body>
<div class="deck">
  <header class="masthead">
    <div class="brand">
      <span class="b">BiRAGAS<span class="dot">.</span></span>
      <span>EDITORIAL · THE THREE RIGHTS</span>
    </div>
    <div class="meta">MMXXVI · 56 SLIDES · AYASS BIOSCIENCE</div>
    <div class="controls">
      <button class="btn" id="audio-btn" aria-pressed="false"><span class="dot"></span>AUDIO · OFF</button>
      <button class="btn" id="auto-btn" aria-pressed="false"><span class="dot"></span>AUTO · OFF</button>
      <button class="btn" id="fs-btn">⛶ FULLSCREEN</button>
    </div>
  </header>

  <div class="stage">
{{SECTIONS}}
  </div>

  <footer class="footer">
    <button class="nav-btn" id="prev" aria-label="Previous slide">←</button>
    <div class="counter" id="counter" aria-live="polite">01<span class="of">/</span>{{TOTAL}}</div>
    <div class="progress"><div class="bar" id="bar"></div></div>
    <div class="scrubber" id="scrubber"></div>
    <button class="nav-btn" id="next" aria-label="Next slide">→</button>
  </footer>

  <button class="side-nav prev" id="side-prev" aria-label="Previous slide" type="button"><span class="chev">‹</span></button>
  <button class="side-nav next" id="side-next" aria-label="Next slide" type="button"><span class="chev">›</span></button>
</div>

<audio id="player" preload="auto"></audio>

<div class="now-playing" id="now-playing">
  <span class="eq"><span></span><span></span><span></span><span></span></span>
  <span id="np-label">narration</span>
</div>

<script>
const slides = [...document.querySelectorAll('.slide')];
const player = document.getElementById('player');
const audioBtn = document.getElementById('audio-btn');
const autoBtn = document.getElementById('auto-btn');
const fsBtn = document.getElementById('fs-btn');
const prevBtn = document.getElementById('prev');
const nextBtn = document.getElementById('next');
const sidePrev = document.getElementById('side-prev');
const sideNext = document.getElementById('side-next');
const counter = document.getElementById('counter');
const bar = document.getElementById('bar');
const scrubber = document.getElementById('scrubber');
const npLabel = document.getElementById('np-label');
const nowPlay = document.getElementById('now-playing');

let cur = 0;
let audioOn = false;
let autoOn = false;
const N = slides.length;

slides.forEach((s, i) => {
  const pip = document.createElement('div');
  pip.className = 'pip';
  pip.title = s.dataset.label || ('slide ' + (i+1));
  pip.addEventListener('click', () => goTo(i));
  scrubber.appendChild(pip);
});
const pips = [...scrubber.children];

function pad(n){ return String(n).padStart(2,'0'); }
function updateUI() {
  counter.innerHTML = `${pad(cur+1)}<span class="of">/</span>${pad(N)}`;
  bar.style.width = `${100*(cur+1)/N}%`;
  pips.forEach((p, i) => {
    p.classList.toggle('done', i < cur);
    p.classList.toggle('active', i === cur);
  });
  prevBtn.disabled = cur === 0;
  nextBtn.disabled = cur === N - 1;
  sidePrev.disabled = cur === 0;
  sideNext.disabled = cur === N - 1;
  // auto-scroll the scrubber to keep current pip visible
  const activePip = pips[cur];
  if (activePip && activePip.scrollIntoView) {
    activePip.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  }
}
function goTo(i) {
  if (i < 0 || i >= N) return;
  slides[cur].classList.remove('active');
  cur = i;
  slides[cur].classList.add('active');
  updateUI();
  if (audioOn) playSlideAudio();
}
function playSlideAudio() {
  const p = slides[cur].dataset.audio;
  if (!p) { player.pause(); nowPlay.classList.remove('on'); return; }
  player.src = p;
  player.play().then(() => {
    npLabel.textContent = slides[cur].dataset.label || 'narration';
    nowPlay.classList.add('on');
  }).catch(()=>nowPlay.classList.remove('on'));
}
audioBtn.addEventListener('click', () => {
  audioOn = !audioOn;
  audioBtn.classList.toggle('on', audioOn);
  audioBtn.innerHTML = `<span class="dot"></span>${audioOn ? 'AUDIO · ON' : 'AUDIO · OFF'}`;
  if (audioOn) playSlideAudio();
  else { player.pause(); nowPlay.classList.remove('on'); }
});
autoBtn.addEventListener('click', () => {
  autoOn = !autoOn;
  autoBtn.classList.toggle('on', autoOn);
  autoBtn.innerHTML = `<span class="dot"></span>${autoOn ? 'AUTO · ON' : 'AUTO · OFF'}`;
});
fsBtn.addEventListener('click', () => {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen();
  else document.exitFullscreen();
});
player.addEventListener('ended', () => {
  nowPlay.classList.remove('on');
  if (autoOn) goTo(cur + 1);
});
prevBtn.addEventListener('click', () => goTo(cur - 1));
nextBtn.addEventListener('click', () => goTo(cur + 1));
sidePrev.addEventListener('click', () => goTo(cur - 1));
sideNext.addEventListener('click', () => goTo(cur + 1));

let _tx = null, _ty = null;
document.addEventListener('touchstart', e => { const t = e.changedTouches[0]; _tx = t.clientX; _ty = t.clientY; }, {passive:true});
document.addEventListener('touchend', e => {
  if (_tx === null) return;
  const t = e.changedTouches[0];
  const dx = t.clientX - _tx, dy = t.clientY - _ty;
  if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.5) {
    if (dx < 0) goTo(cur + 1); else goTo(cur - 1);
  }
  _tx = _ty = null;
}, {passive:true});

document.addEventListener('keydown', e => {
  if (e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();goTo(cur+1);}
  else if (e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();goTo(cur-1);}
  else if (e.key==='Home') goTo(0);
  else if (e.key==='End') goTo(N-1);
  else if (e.key==='a'||e.key==='A') audioBtn.click();
  else if (e.key==='f'||e.key==='F') fsBtn.click();
});
document.addEventListener('click', e => {
  const t = e.target.closest('.cover h1, .body-slide h2, .close-slide .manifesto');
  if (!t) return;
  if (!audioOn) { audioOn = true; audioBtn.classList.add('on'); audioBtn.innerHTML = '<span class="dot"></span>AUDIO · ON'; }
  playSlideAudio();
});
updateUI();
</script>
</body></html>
"""


if __name__ == "__main__":
    build()
