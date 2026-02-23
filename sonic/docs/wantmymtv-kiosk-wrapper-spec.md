# WantMyMTV – Full‑Screen / Kiosk Wrapper Spec (Windows)

Target URL  
https://wantmymtv.vercel.app/player.html

---

## 1) Goals

- Instant full‑screen playback
- Remote‑only control
- No visible browser chrome
- Clean return to Kodi

---

## 2) Recommended Implementation — Edge Fullscreen / Kiosk

**Behaviour**
- Launches directly into WantMyMTV
- Full‑screen display
- Single‑site browsing

**Exit strategy**
- Remote‑mapped key closes window (Alt+F4 or custom)
- Kodi regains focus immediately

---

## 3) Alternative — Chrome App Mode

- Launch with `--app=<url>`
- Borderless window
- Optional fullscreen flag

Trade‑off: slightly less locked‑down than Edge kiosk.

---

## 4) Kodi Integration

- Kodi menu item launches kiosk command
- Browser runs on top of Kodi
- Closing browser returns user to Kodi UI

---

## 5) Remote Control Mapping (Minimum)

Recommended key mappings:
- Back / Exit → Close browser window
- Home → Close browser / return to Kodi
- Play / Pause → Space
- Volume → System volume

FLIRC or Bluetooth remotes recommended.

---

## 6) Resilience

- Kodi remains running if browser crashes
- WantMyMTV can always be relaunched
- No multi‑tab or general browsing allowed

---

## 7) Nice‑to‑Haves

- Party Mode (launch + set volume + disable notifications)
- Screensaver suppression
- Sonic Stick branded tile/icon

---

## 8) Raspberry Pi TV Box Addendum (Kodi / LibreELEC)

### Scope
- Same UX target as Windows kiosk: one-click MTV-style fullscreen playback, remote-only control, fast return to Kodi.

### Runtime recommendation
- Prefer Chromium kiosk mode on Raspberry Pi:
  - `chromium-browser --kiosk https://wantmymtv.vercel.app/player.html`
  - Optional hardening flags:
    - `--noerrdialogs`
    - `--disable-session-crashed-bubble`
    - `--autoplay-policy=no-user-gesture-required`

### Open-source MTV concept layer (channel/zapping)
- Include **PseudoTV Live** (Kodi add-on, open source) as the MTV-style channel layer.
- Role in stack:
  - PseudoTV Live = scheduled “channel” experience and zapping behavior.
  - WantMyMTV player page = branded playback destination for direct kiosk launch.
- Result: users can either “watch channel” (PseudoTV Live flow) or jump straight into WantMyMTV kiosk.

### Control and exit contract
- Remote Back/Home must close kiosk and refocus Kodi.
- Keep a single authoritative return path (no nested browser states, no tabs).

### Operational notes
- Disable screen blanking/screensaver during playback.
- Keep Kodi resident so browser exits return instantly.
- Boot option: auto-start Kodi, then expose a single “WantMyMTV” tile in home menu.

---

## 9) Content Platform Expansion (Legal Sources Only)

### Required media types
- Internet radio
- Podcasts
- YouTube (official/public content only)
- Existing MTV-style music video playback

### Preconfigured curated library (default on first boot)
- Ship with a starter library that is ready to browse immediately.
- Library should include:
  - Curated internet radio stations (genre + mood + decade)
  - Curated podcast picks (music history, culture, interviews, news)
  - Curated YouTube playlists/channels with stable public URLs
- All defaults must use legal/publicly accessible sources and metadata.

### User customization requirements
- User can:
  - Search content across supported sources
  - Add new stations/shows/channels/playlists
  - Remove items from their local library
  - Reorder/favorite/pin content
  - Create custom collections (e.g., “Morning Radio”, “Late Night MTV”)
- Curated defaults remain available, but user changes are saved separately so updates do not wipe personal edits.

### Legal and policy contract
- No piracy workflows.
- No bundled copyrighted media files.
- Only link/index sources the user is authorized to access or that are publicly available.
- Include a visible “Source & Rights” note in settings:
  - “You are responsible for rights and terms of any content sources you add.”

### UX expectations
- One unified media browser with source filters: `Radio | Podcasts | YouTube | MTV`.
- Fast remote-friendly actions: `Play`, `Add`, `Favorite`, `Back`.
- Search should support both title and channel/show/station name.
