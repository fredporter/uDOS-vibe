# RetroArch Single Profile Setup + Netplay Co‑Op Guide

This document turns RetroArch into a **single‑profile, console‑like system** for:
- NES
- Game Boy
- Game Boy Color

It also explains **Netplay co‑op** clearly and practically.

---

## 🎮 Goal

- One global controller setup  
- One low‑latency video/audio setup  
- Per‑system visual differences handled cleanly  
- No constant tweaking  

Result: **boot → pick game → play**

---

## 🧠 RetroArch Configuration Hierarchy

```
GLOBAL CONFIG
│
├── Core Overrides
│   ├── NES (Nestopia)
│   └── GB / GBC (Gambatte)
│
└── Game Overrides (rare, optional)
```

We will use:
- **Global config** → input, latency, fullscreen
- **Core overrides** → NES vs handheld look

---

## ⚡ Step 1: Global Settings (Once Only)

### 🎮 Controller (Global)

```
Settings → Input → Port 1 Binds
```

- Bind D‑Pad, A, B, Start, Select
- Optional: disable analog stick for purity

Applies to **all systems**.

---

### 📺 Video (Low‑Latency Defaults)

```
Settings → Video
```

- Fullscreen: ON
- Windowed Fullscreen: OFF
- VSync: ON
- Hard GPU Sync: ON (if available)
- Threaded Video: OFF

```
Settings → Video → Synchronisation
```

- Max Swapchain Images: 2 (if present)

---

### 🔊 Audio

```
Settings → Audio
```

- Driver: XAudio
- Latency: 64–96 ms

---

## ⚡ Step 2: NES Core Override (Nestopia UE)

1. Launch any NES game
2. Open **Quick Menu**

### Core Options
```
Quick Menu → Core Options
```
- Disable sprite flicker (optional)
- Correct aspect ratio

### CRT Shader
```
Quick Menu → Shaders → Load Preset
crt/crt-easymode
```

Then:
```
Quick Menu → Overrides → Save Core Overrides
```

NES‑only settings are now locked in.

---

## ⚡ Step 3: Game Boy / Game Boy Color Core Override (Gambatte)

1. Launch any GB or GBC game

### Core Options
```
Quick Menu → Core Options
```
- Enable colour correction (optional)
- Enable DMG palette (GB)

### LCD Shader (Optional)
```
handheld/lcd-grid
```

Then:
```
Quick Menu → Overrides → Save Core Overrides
```

Handheld look is preserved without affecting NES.

---

## 📁 Recommended Folder Layout

```
RetroGames/
│
├── NES/
│   └── Homebrew/
│
├── GB/
│
└── GBC/
```

RetroArch playlists will auto‑generate correctly.

---

## ✅ Final Result

- One controller profile
- One latency profile
- Correct visuals per system
- Zero future fiddling

This mirrors **RetroPie / MiSTer‑style discipline**.

---

# 🌐 What Is Netplay Co‑Op?

**Netplay** lets you play retro games online with friends **as if you were on the same couch**.

---

## 🧠 How Netplay Works

```
HOST (You)
│
├── Same ROM
├── Same Core
└── Input Synchronisation
     │
     └── CLIENT (Friend)
```

- Host runs the game
- Clients send controller input
- Emulator stays in lockstep

---

## 🎮 Best Games for Netplay

Works best with:
- NES
- SNES
- GB / GBC
- Arcade

Ideal genres:
- Co‑op platformers
- Beat ’em ups
- Shooters
- Puzzle games

Examples:
- Micro Mages
- Twin Dragons
- From Below

---

## ⚠️ Netplay Caveats

- Both players must use:
  - Same ROM
  - Same core
- Ethernet preferred over Wi‑Fi
- Not ideal for:
  - Precision fighters
  - Rhythm games

---

## 🧠 When to Use Netplay

Use it when:
- You want nostalgic co‑op
- Timing tolerance is OK

Skip it when:
- You need perfect frame timing
- Competitive play matters

---

## TL;DR

- **Single RetroArch profile** = console‑like simplicity
- **Core overrides** handle system differences cleanly
- **Netplay** = online couch co‑op, best for NES homebrew

---

End of document.
