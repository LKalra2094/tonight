# Session Status

**Last updated**: 2026-03-29

---

## Where We Left Off

- Sprint 1 complete and merged
- Built: keyword search → Eventbrite (scraping) + Lu.ma (API) → event cards in 4-column grid
- Eventbrite: scrape search page for event list, enrich with ticket_classes API for pricing
- Lu.ma: public REST API, filter by keyword client-side, filter out sold out and online events
- Frontend: search bar, clickable event cards (image, name, date, venue, price), price filter with presets, invite-only toggle
- Discovered Eventbrite search API was deprecated in 2019 — pivoted to scraping
- SerpApi explored but dropped (Google index too thin vs Eventbrite's own search)
- Moved worktree convention from `.worktrees/` to `worktrees/` for Obsidian visibility
- Updated root CLAUDE.md with new worktree path convention
- `.env` lives at `Application/.env` (shared across frontend/backend)

### Key Decisions

- Eventbrite data via scraping `__SERVER_DATA__` JSON + ticket API (not their deprecated search API)
- Lu.ma data via their undocumented public REST API
- No SerpApi dependency — scraping gives better results
- Price filtering done client-side (no re-fetch needed)
- Events with unknown prices ("See listing") pass through price filter

### Next Steps

1. Scope Sprint 2
2. Potential areas: more event sources (19hz, Do The Bay), better search, UI polish, neighborhood filtering
