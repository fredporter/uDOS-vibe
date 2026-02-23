# Sonic Stick – Kodi Launcher Flow & Boot Modes (ASCII)

---

## A) Kodi Launcher Flow Diagrams

### Option A — Kodi as the Shell (Appliance‑style)
```
[ Power On ]
     |
     v
[ Windows Boot ]
     |
     v
[ Auto‑Login ]
     |
     v
[ Kodi Fullscreen ]
     |
     +--> Local Library
     |
     +--> Plex
     |
     +--> Streaming Apps
     |
     +--> WantMyMTV
     |
     v
[ Sleep / Hibernate ]
```

---

### Option B — Mode Selector First (Productised)
```
[ Power On ]
     |
     v
[ Windows Boot + Auto‑Login ]
     |
     v
[ Sonic Stick Mode Selector ]
     |
     +--> MEDIA MODE
     |       |
     |       v
     |   [ Kodi Fullscreen ]
     |       |
     |       +--> Plex / Streaming / WantMyMTV
     |
     +--> GAME SERVER MODE
             |
             v
     [ Server Dashboard ]
             |
             +--> Service status
             +--> Start / Stop servers
             +--> Switch to Media Mode
```

---

## B) Media Mode vs Game Server Mode

### Media Mode
**Intent:** Smart TV behaviour

- Launches Kodi immediately
- Server services run silently in background
- Remote “Power” triggers sleep/hibernate
- Hidden admin escape to desktop

**Success:** usable by anyone with a remote in <10 seconds.

---

### Game Server Mode
**Intent:** Stability & maintenance

- Minimal UI or dashboard
- Clear service health indicators
- Optional launch of Steam Big Picture
- Button to switch to Media Mode

**Success:** server health visible without desktop access.

---

## C) Mode Selection Strategies

Choose one:
1. Timed selector (default to Media Mode)
2. Persist last-used mode
3. Remote override on boot (e.g. hold HOME)
