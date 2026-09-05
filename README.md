# Mesh & More — Local Holding Page

A real, working, **local-only** holding page for Mesh & More (luxury small-group
travel for solo travellers over 40). Reuses the dark-editorial design system
from `site-redesign-v1.html`, upgraded to the ui-ux-pro-max *luxury dark
editorial* system: deep ink `#0B1B1E`, bone `#EFE9DD`, refined gold accent
`#C8A35B`, Cormorant (display serif) + Montserrat (UI sans). No third-party
ESP, no cloud DB — lead data never leaves this machine.

## What it does

- Serves `index.html` (hero, how-it-works, journeys, **pricing band**, honesty,
  and a **lead-capture form**).
- The form POSTs to a tiny local handler (`/api/lead`) which appends each lead
  as one JSON line to `leads/leads.jsonl`.
- Pre-launch mechanic: register-interest / hold-a-spot — **no full payment**,
  **optional refundable £50–£100 hold**, "expected 2026/27", no supplier
  contracted yet.
- Responsive, no iOS/phone frame on desktop, no glassmorphism, no AI purple.

## Run it (one command)

```bash
cd /Users/nicholaschristensen/Projects/05-mesh-and-more/site
python3 app.py
```

Then open <http://127.0.0.1:8000> in your browser.

Optional custom port:

```bash
python3 app.py 8080
```

To stop: `Ctrl+C`.

## Test the form end-to-end (no browser needed)

In a second terminal, while the server is running:

```bash
curl -s -X POST http://127.0.0.1:8000/api/lead \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test Traveller","email":"test@example.com","journey":"Puglia","window":"2026-spring"}'
```

Confirm the lead landed:

```bash
cat leads/leads.jsonl
```

You should see one JSON object per submission.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The holding page markup + lead form + client-side POST |
| `css/style.css` | Dark-editorial design system (extracted/extended from v1) |
| `app.py` | Stdlib `http.server` + `POST /api/lead` → `leads/leads.jsonl` |
| `leads/` | Created at runtime; `leads.jsonl` stores submissions |
| `README.md` | This file |

## Notes

- Pure Python standard library — no `pip install` required.
- Lead data is stored on this machine only. To reset, delete `leads/leads.jsonl`.
- Copy is currently drawn from `site-redesign-v1.html`; swap in final
  humanized copy when `copy-holding-page-humanized.md` lands — markup has clear
  section anchors (`#join`, `#pricing`, etc.) for easy replacement.
