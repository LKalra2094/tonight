# Product Backlog

**Created**: March 2026
**Status**: In Progress

---

## How This Works

Each row is an **epic** — a full user story from the PRD that may take multiple sprints to complete. When an epic is picked up, an epic doc is created in `Epics/` that breaks it into deliverable stories with acceptance criteria. Sprint tech specs reference which epic stories they deliver.

An epic's status is **Done** only when all its stories in the epic doc are shipped.

---

| # | Epic | User Journey Phase | Priority | Status | Epic Doc | Notes |
|---|------|--------------------|----------|--------|----------|-------|
| 1 | Google OAuth sign-up + display name (US-1) | Onboard | P0 | Pending | — | Calendar read access granted at sign-up |
| 2 | Location permission (US-2) | Onboard | P0 | Pending | — | — |
| 3 | Age collection (US-3) | Onboard | P1 | Pending | — | Birthdate picker, required for 21+ filtering |
| 4 | Gender collection (US-4) | Onboard | P1 | Pending | — | Used for dress code personalization |
| 5 | Dietary restrictions (US-5) | Onboard | P1 | Pending | — | Multi-select, editable in Settings |
| 6 | Geographic comfort zone (US-6) | Onboard | P1 | Pending | — | SF only / SF + East Bay / full Bay Area |
| 7 | Activity preferences (US-7) | Onboard | P1 | Pending | — | Multi-select, skippable |
| 8 | Cuisine preferences (US-8) | Onboard | P1 | Pending | — | Multi-select, skippable |
| 9 | Natural language input (US-9) | Set the Scene | P0 | Pending | — | Primary input, no other field required |
| 10 | Date selection (US-10) | Set the Scene | P0 | Pending | — | Default: Tonight, max 14 days out |
| 11 | Budget ceiling (US-11) | Set the Scene | P0 | Pending | — | Preset + custom, default $500 |
| 12 | Group type (US-12) | Set the Scene | P1 | Pending | — | Solo / Date / Friends / Group |
| 13 | Starting location (US-13) | Set the Scene | P0 | Pending | — | Quick-select + custom address |
| 14 | Head-out time (US-14) | Set the Scene | P0 | Pending | — | 30-min increments, smart default |
| 15 | End time (US-15) | Set the Scene | P0 | Pending | — | Preset options, default Midnight |
| 16 | Neighborhood preference (US-16) | Set the Scene | P1 | Pending | — | Multi-select SF neighborhoods, session-only |
| 17 | Occasion tag (US-17) | Set the Scene | P2 | Pending | — | Single-select, influences vibe |
| 18 | Indoor/outdoor (US-18) | Set the Scene | P1 | Pending | — | Weather warning if outdoor + bad weather |
| 19 | Vibe selection (US-19) | Set the Scene | P1 | Pending | — | Preset options only, single-select |
| 20 | Smart defaults (US-20) | Set the Scene | P2 | Pending | — | Pre-fill from saved defaults |
| 21 | Hidden fields (US-21) | Set the Scene | P2 | Pending | — | Fields hidden via Settings |
| 22 | Field mode configuration (US-22) | Set the Scene | P2 | Pending | — | Ask / Pre-fill / Don't ask per field |
| 23 | Google Calendar integration (US-23) | Set the Scene | P2 | Pending | — | Uses OAuth from sign-up, reads busy blocks |
| 24 | Plan cards (US-24) | Browse Plans | P0 | Pending | — | Exactly 3 cards, ranked |
| 25 | Specific vs vague input handling (US-25) | Browse Plans | P0 | Pending | — | Varies plan diversity by input specificity |
| 26 | History-informed plans (US-26) | Browse Plans | P2 | Pending | — | Weights from past ratings |
| 27 | Discovery pick (US-27) | Browse Plans | P1 | Pending | — | 3rd card always discovery |
| 28 | Time-driven stop count (US-28) | Browse Plans | P0 | Pending | — | 1-3 stops based on available time |
| 29 | Source attribution on cards (US-29) | Browse Plans | P0 | Pending | — | Source label + link per anchor event |
| 30 | Show me more (US-30) | Browse Plans | P1 | Pending | — | 3 new plans, no anchor overlap |
| 31 | Change inputs (US-31) | Browse Plans | P1 | Pending | — | Back to Set the Scene, fields preserved |
| 32 | Full sequenced evening (US-32) | Your Plan | P0 | Pending | — | Chronological stops with times, venues, travel |
| 33 | Cost breakdown (US-33) | Your Plan | P0 | Pending | — | Total + per-category, per person |
| 34 | Travel time between stops (US-34) | Your Plan | P0 | Pending | — | Walk if <15 min, otherwise rideshare |
| 35 | Venue photos (US-35) | Your Plan | P1 | Pending | — | 3-5 photos per venue, swipeable |
| 36 | Source attribution on plan (US-36) | Your Plan | P0 | Pending | — | Source + link per venue/event |
| 37 | Visual timeline (US-37) | Your Plan | P0 | Pending | — | Bare-bones vertical timeline: stops, times, travel |
| 38 | Embedded map (US-38) | Your Plan | P1 | Pending | — | Google Maps Embed per venue |
| 39 | Browse alternatives and swap stops (US-39) | Refine | P1 | Pending | — | Carousel for dining/drinks, swap for events |
| 40 | Back to plan cards (US-40) | Refine | P1 | Pending | — | Return to Browse Plans, plans preserved |
| 41 | Travel mode override (US-41) | Refine | P1 | Pending | — | Per-segment: walk, bike, rideshare, transit |
| 42 | What to wear (US-42) | Commit | P1 | Pending | — | Weather + dress code, gender-aware |
| 43 | Vibe info (US-43) | Commit | P1 | Pending | — | Per-venue vibe from reviews |
| 44 | Save to Google Calendar (US-44) | Commit | P2 | Pending | — | One event per stop, departure reminders |
| 45 | Save to history (US-45) | Commit | P1 | Pending | — | Auto-save on commit |
| 46 | Share as link (US-46) | Socialize | P2 | Pending | — | Read-only shareable URL, no login to view |
| 47 | Visual plan card for social (US-47) | Socialize | P2 | Pending | — | Styled image for Stories / sharing |
| 48 | Invite friends (US-48) | Socialize | P2 | Pending | — | Invite via link, phone, or email |
| 49 | Rate each stop (US-49) | Feedback | P2 | Pending | — | Next-day prompt, thumbs up/down |
| 50 | Flag vibe mismatch (US-50) | Feedback | P2 | Pending | — | Per-stop, selectable categories |
| 51 | Didn't go out prompt (US-51) | Feedback | P2 | Pending | — | Captures primary reason |
| 52 | Browse past plans (US-52) | History | P2 | Pending | — | Reverse chronological, full detail view |
| 53 | Re-run a past plan (US-53) | History | P2 | Pending | — | Pre-fills Set the Scene from past input |
| 54 | Settings management (US-54) | Settings | P1 | Pending | — | All onboarding fields + field modes editable |
| 55 | Saved addresses (US-55) | Settings | P2 | Pending | — | Named addresses for starting location |
