# Sylaris social assets

Post graphics for Sylaris OS social channels, plus the template that renders them. Images here are public so GoHighLevel's Social Planner can fetch them.

- `template/`: the renderer (`render.py`), the HTML template, and the SYLARIS wordmark.
- `posts/YYYY-MM/`: rendered images, named `<post id>_<size>.png`.
- `BRAND.md`: the visual and copy rules every post follows.

## Render an image

```
cd template
npm install                      # Sora and Inter fonts
pip install playwright --break-system-packages && python3 -m playwright install chromium
python3 render.py spec.json ../posts/2026-10
```

`spec.json` is one object or a list:

```json
{
  "id": "content-20261026-1",
  "size": "feed",
  "theme": "dark",
  "label": "The system",
  "eyebrow": "AI Recovery Agent",
  "headline": "Patients who drop off *don't stay lost.*",
  "stat": "~40%",
  "sub": "Supporting line in plain words.",
  "items": [{"title": "Pick a template", "text": "Built for telehealth"}],
  "cta": "Book a Launch Call →",
  "note": "Small disclaimer line.",
  "counter": "01 / 05",
  "url": "sylarisos.com/launch"
}
```

Only `id` and `headline` (or `stat`) are required. Text inside `*...*` takes the accent color: teal on dark, gray on light. Sizes: `feed` 1080×1350 (Instagram and Facebook), `x` 1600×900, `story` 1080×1920. Long headlines shrink to fit.

## Public link for an image

`https://raw.githubusercontent.com/joecore44/sylaris-social-assets/main/posts/<YYYY-MM>/<file>.png`
