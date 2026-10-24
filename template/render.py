#!/usr/bin/env python3
"""Render Sylaris-branded social images from a JSON spec.

Usage: python3 render.py spec.json [out_dir]

A spec is one object or a list of objects:
{
  "id": "content-20261024-2",          # output file name stem
  "size": "feed" | "x" | "story",      # feed 1080x1350, x 1600x900, story 1080x1920
  "theme": "dark" | "light",
  "label": "Sylaris One",              # pill, top left (optional)
  "eyebrow": "U.S. TELEMEDICINE MARKET",  # small caps line above headline (optional)
  "headline": "Launch your site *and your platform together.*",  # *...* = accent color
  "stat": "$88.2B",                    # big number instead of / above headline (optional)
  "sub": "Supporting line.",           # optional
  "items": [{"title": "...", "text": "..."}],  # optional cards (max 3)
  "cta": "Book a Launch Call →",       # optional button
  "note": "Small disclaimer line.",    # optional, above the footer
  "counter": "01 / 05"                 # optional carousel counter, footer right
}
"""
import html, json, os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
SIZES = {"feed": (1080, 1350), "x": (1600, 900), "story": (1080, 1920)}


def esc_accent(text):
    t = html.escape(text)
    t = re.sub(r"\*(.+?)\*", r'<span class="accent">\1</span>', t)
    return t.replace("\n", "<br>")


def body_for(s):
    theme = s.get("theme", "dark")
    parts = []
    if s.get("label"):
        parts.append(f'<div class="pill">{html.escape(s["label"])}</div>')
    main = []
    if s.get("eyebrow"):
        main.append(f'<div class="eyebrow">{html.escape(s["eyebrow"])}</div>')
    if s.get("stat"):
        main.append(f'<div class="stat">{esc_accent(s["stat"])}</div>')
    if s.get("headline"):
        main.append(f'<h1 id="h">{esc_accent(s["headline"])}</h1>')
    if s.get("sub"):
        main.append(f'<p class="sub">{esc_accent(s["sub"])}</p>')
    if s.get("items"):
        cards = "".join(
            f'<div class="card"><b>{html.escape(i.get("title", ""))}</b><span>{html.escape(i.get("text", ""))}</span></div>'
            for i in s["items"][:3])
        main.append(f'<div class="list">{cards}</div>')
    if s.get("cta"):
        main.append(f'<div class="cta">{html.escape(s["cta"])}</div>')
    parts.append(f'<div class="main" id="main">{"".join(main)}</div>')
    if s.get("note"):
        parts.append(f'<p class="note">{html.escape(s["note"])}</p>')
    mark = "wordmark-white.png" if theme == "dark" else "wordmark-dark.png"
    right = html.escape(s.get("counter") or s.get("url") or "sylarisos.com/launch")
    parts.append(f'<div class="foot"><img src="{ROOT / mark}"><span class="url">{right}</span></div>')
    return "\n".join(parts)


def page_for(s):
    w, h = SIZES[s.get("size", "feed")]
    style = []
    if s.get("size") == "x":
        style += ["--pad:72px", "--hs:84px", "--ss:150px", "--subs:28px"]
    if s.get("size") == "story":
        style += ["--pad:84px"]
    tpl = (ROOT / "template.html").read_text()
    out = (tpl.replace("FONTS/", f"{ROOT}/node_modules/@fontsource/sora/files/")
              .replace("IFONTS/", f"{ROOT}/node_modules/@fontsource/inter/files/")
              .replace("THEME", s.get("theme", "dark"))
              .replace("WIDTH", str(w)).replace("HEIGHT", str(h))
              .replace("STYLE", ";".join(style))
              .replace("BODY", body_for(s)))
    if s.get("size") == "story":
        out = out.replace('<div class="frame">', '<div class="frame" style="padding-top:230px;padding-bottom:220px">')
    return out, w, h


FIT_JS = """
() => {
  const main = document.getElementById('main'), h = document.getElementById('h');
  if (!h) return;
  let size = parseFloat(getComputedStyle(h).fontSize);
  while (main.scrollHeight > main.clientHeight + 2 && size > 44) {
    size -= 3; h.style.fontSize = size + 'px';
  }
}
"""


def render(specs, out_dir):
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for s in specs:
            page_html, w, h = page_for(s)
            tmp = out_dir / f".{s['id']}.html"
            tmp.write_text(page_html)
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.evaluate(FIT_JS)
            dest = out_dir / f"{s['id']}_{s.get('size', 'feed')}.png"
            pg.screenshot(path=str(dest))
            pg.close()
            tmp.unlink()
            results.append(str(dest))
        b.close()
    return results


if __name__ == "__main__":
    data = json.loads(Path(sys.argv[1]).read_text())
    specs = data if isinstance(data, list) else [data]
    for r in render(specs, sys.argv[2] if len(sys.argv) > 2 else ROOT / "out"):
        print(r)
