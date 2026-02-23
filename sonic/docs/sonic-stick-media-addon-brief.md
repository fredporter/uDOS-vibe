# Sonic Stick – Media & Streaming HTPC Add-On Brief

**Add-on module for the Windows Game Server (“Sonic Stick”)**

---

## 1) Objective

Extend the **Windows Game Server (Sonic Stick)** into a **hybrid Smart TV + Media Centre + Streaming Hub** while preserving its primary role as a game server.

Key outcomes:
- **Remote-first** living-room UX (true 10‑foot interface)
- Strong **commercial streaming compatibility** (DRM-safe via browser)
- Rich **local media library** support (local disks, USB, NAS)
- Optional **whole‑home streaming** via Plex
- Distinctive **ambient music TV mode** via WantMyMTV

---

## 2) Included Feature

**WantMyMTV player**  
https://wantmymtv.vercel.app/player.html

Purpose: instant “music television” playback for background, parties, or idle lounge use.

---

## 3) System Overview

```
[ TV / Projector ]
        ↑ HDMI
[ Sonic Stick (Windows) ]
        │
        ├─ Kodi (primary 10‑foot UI shell)
        ├─ Plex (library + cross‑device streaming)
        ├─ Browser Streaming (Netflix, YouTube, Disney+, Prime)
        └─ WantMyMTV (full‑screen web player)

(Game server services continue running in the background)
```

Kodi acts as the **Smart TV shell**, while Plex and browser apps handle modern streaming and DRM.

---

## 4) Core Components

### 4.1 Kodi — Primary TV Interface
**Role**
- Full‑screen UI launched automatically on boot
- Manages local movies, TV, and music
- Optional IPTV / PVR support

**Why Kodi**
- Best-in-class remote and controller support
- Mature plugin ecosystem
- Proven HTPC stability

---

### 4.2 Plex — Library & Remote Streaming
**Role**
- Centralised metadata-rich library
- Streaming to mobile, tablets, TVs, and browsers

**Deployment**
- Plex Server may run on Sonic Stick (optional)
- Plex Client launched directly or via Kodi

**Integration models**
- PlexKodiConnect (Kodi UI backed by Plex)
- Separate Kodi (local) + Plex (remote)

---

### 4.3 Browser-Based Streaming
**Role**
- Guaranteed compatibility with commercial platforms

**Method**
- Edge or Chrome shortcuts launched from Kodi
- Supports full DRM (Widevine / PlayReady)

Examples:
- Netflix (4K where supported)
- YouTube
- Disney+
- Prime Video

---

### 4.4 WantMyMTV — Ambient Channel Mode
**Role**
- One-click retro music TV experience
- Designed for hands-off or social use

**Behaviour**
- Launches in kiosk / full‑screen browser
- Returns cleanly to Kodi when exited

---

## 5) Couch User Experience

1. Power on TV
2. Sonic Stick boots Windows
3. Auto‑login completes
4. Kodi (or Mode Selector) appears
5. User chooses:
   - Local media (Kodi)
   - Plex
   - Streaming apps
   - WantMyMTV

Goal: **feels like a Smart TV, behaves like a server**.

---

## 6) Input & Control

Supported:
- IR remote (FLIRC recommended)
- Bluetooth remote
- Xbox / game controller
- Keyboard (maintenance only)

Design rule: **no mouse required for daily use**.

---

## 7) Audio / Video Capability

- 4K / HDR playback (hardware dependent)
- Multi‑channel audio passthrough (Dolby / DTS)
- Automatic refresh‑rate switching

---

## 8) Benefits & Positioning

- Turns Sonic Stick into a **daily‑use lounge device**
- Eliminates Smart TV ads and OEM lock‑in
- Combines **gaming + media + streaming** in one box

**Positioning statement**

> The Sonic Stick Media Add‑On transforms a Windows game server into a full Smart TV replacement — without sacrificing power, control, or openness.

---

## 9) Optional Future Enhancements

- Sonic Stick branded Kodi skin
- User profiles (Kids / Guest)
- Scheduled ambient playback
- Home automation hooks
