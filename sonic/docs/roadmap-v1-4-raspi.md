Perfect. Locking it in properly now.

This is a TV box first.
It records.
It plays.
It integrates with NAS.
It feels like a console.

Below is the clean formal spec.

⸻

uHOME Lite v0.9

Raspberry Pi 4 TV Recorder Console

Platform: Raspberry Pi OS (Debian 64-bit)

⸻

1️⃣ Purpose

uHOME Lite is a dedicated living-room TV box that:
	•	Receives DVB-T/T2 broadcast via USB tuner
	•	Records to local scratch storage (microSD)
	•	Automatically moves recordings to NAS
	•	Delegates ad removal to external server
	•	Plays live TV and recordings via Kodi
	•	Operates controller-first
	•	Boots like a console appliance

This is a prototype node aligned with future uHOME architecture.

⸻

2️⃣ Hardware Specification

Core Device
	•	Raspberry Pi 4 (8GB recommended)
	•	Official PSU
	•	Active cooling case
	•	128GB microSD (OS + scratch)
	•	Gigabit Ethernet (preferred)
	•	Wi-Fi (fallback)
	•	Bluetooth 5.0
	•	HDMI to TV

⸻

RF Input
	•	USB DVB-T/T2 tuner (single channel)
	•	Coax antenna input

⸻

Storage Model

microSD (128GB)

Used for:
	•	OS
	•	TVHeadend recordings (temporary)
	•	Buffer storage

Recordings retained temporarily only.

⸻

NAS (Primary Archive)

Mounted via:
	•	NFS (preferred)
	•	SMB (fallback)

Used for:
	•	Long-term storage
	•	Server-side ad removal
	•	Final media library

⸻

3️⃣ Software Stack

⸻

Operating System

Raspberry Pi OS (64-bit, Debian-based)

Use:
	•	Desktop version (easier setup)
	•	Or Lite + custom launcher (cleaner appliance mode)

⸻

Backend (DVR Engine)

TVHeadend

Responsibilities:
	•	Detect USB tuner
	•	Scan DVB-T/T2 channels
	•	Manage EPG
	•	Record live streams
	•	Serve streams to Kodi

⸻

Frontend (Playback)

Kodi

Responsibilities:
	•	Live TV playback
	•	Recorded TV playback
	•	Controller navigation
	•	Media library browsing

Kodi connects to TVHeadend via built-in PVR client.

⸻

Recording Flow

Antenna
   ↓
USB DVB-T tuner
   ↓
TVHeadend
   ↓
microSD scratch storage
   ↓
Auto-move to NAS
   ↓
Server performs ad removal
   ↓
Final stored in NAS library


⸻

4️⃣ Boot Behaviour (Console Mode)

⸻

Boot Sequence
	1.	Power on Pi
	2.	Autologin user
	3.	Launch uHOME Lite menu
	4.	Controller navigates interface

Options:
	•	Watch Live TV
	•	Watch Recordings
	•	Record Now
	•	Schedule Recording
	•	Move Recordings to NAS
	•	Network Status
	•	Storage Status
	•	Shutdown

Launching Live TV opens Kodi.

⸻

Appliance Settings
	•	Screen blanking disabled
	•	Sleep disabled
	•	HDMI always active
	•	Controller wakes UI
	•	Auto-restart on crash (optional)

⸻

5️⃣ Controller Support

Supported:
	•	USB Xbox controller
	•	Bluetooth Xbox controller
	•	8BitDo
	•	Standard HID controllers

Navigation mapping:

Button	Action
D-pad / Left Stick	Navigate
A / Cross	Select
B / Circle	Back
Start	Open menu
LB/RB	Skip
Triggers	Seek

Kodi already supports controller navigation.

uHOME Lite menu maps controller to keyboard events.

⸻

6️⃣ Network Model

⸻

Ethernet (Preferred)
	•	Stable NAS writes
	•	Stable IPTV streaming
	•	Low latency

⸻

Wi-Fi (Fallback)
	•	Acceptable for 1080p playback
	•	Not ideal for heavy NAS transfers

⸻

7️⃣ microSD Scratch Policy

To preserve card lifespan:
	•	Record locally
	•	Auto-move completed recordings to NAS
	•	Delete local copy after transfer
	•	Auto-clean files older than X hours
	•	Monitor free space

microSD is buffer only.

⸻

8️⃣ Performance Envelope

Supports:
	•	1 live stream
	•	1 recording
	•	NAS transfer in background
	•	Smooth 1080p playback
	•	Controller UI responsiveness

Limitations:
	•	No multi-tuner
	•	No heavy re-encoding
	•	No full ad removal locally

⸻

9️⃣ Ad Removal Strategy

Performed externally on:
	•	SteamOS machine
	•	Future Mini PC
	•	NAS-side server

Workflow:

NAS receives raw file
   ↓
Server runs Comskip + optional cut
   ↓
Clean file stored in:
   /Media/TV/Broadcast

Pi only ingests and exports.

⸻

🔟 Integration With SteamOS Console

Pi integrates by:
	•	Sharing NAS library
	•	Optional Steam Link client
	•	Matching controller mapping
	•	Dark theme UI
	•	LAN connectivity

To user:
Feels like same ecosystem.

⸻

1️⃣1️⃣ Why This Is The Right Prototype
	•	Low cost
	•	Stable Debian base
	•	Clean DVR stack
	•	Clear separation of roles
	•	Easy migration to HDHomeRun + Mini PC later
	•	Preserves uHOME philosophy

⸻

Final Architecture Summary

Pi 4 TV Box (Debian)
   - TVHeadend
   - Kodi
   - Scratch recording
   - Controller UI

NAS
   - Archive storage
   - Ad removal server

Future:
HDHomeRun + Mini PC replaces Pi for full uHOME


⸻

If you want next, I can:
	•	Write the step-by-step installation order
	•	Recommend specific USB DVB-T tuners that behave well on Pi
	•	Draft the NAS ad-removal automation spec
	•	Or design the uHOME Lite menu layout visually

What do we formalise next?
-----

Previous, still relevant— here’s a detailed development brief for your multi-stream home media ecosystem featuring:
	1.	Raspberry Pi Always-On TV Box (1-channel PVR)
	2.	SteamOS + Windows10 Kiosk Mode (uHOME Server Option 1)
	3.	Steam + Ubuntu/Alpine + uDOS (uHOME Server Option 2)

This brief is structured to guide design, implementation, and future scalability.

⸻

🧩 uHOME Media System Development Brief

📌 Project Vision

Build a resilient, sovereign, ad-free home media system that:
	•	Continuously records and archives TV broadcasts
	•	Processes recorded content to remove ads
	•	Serves a curated play library
	•	Supports multiple server configurations
	•	Integrates into uHOME/uDOS architecture
	•	Provides frontends for playback (Kodi)
	•	Supports failover and optional heavy-processing tiers

⸻

🚀 System Streams Overview

You’re building three distinct but integrated streams:

🔹 1) Raspi TV Box — Always-On Recording Node

Goal: Record one broadcast channel continuously and reliably with ad-free post-processing pipeline.

🔹 2) SteamOS + Windows10 Kiosk — Server Option 1

Goal: Hybrid gaming + server node capable of additional processing, portal access, and admin tasks.

🔹 3) Steam + Ubuntu/Alpine + uDOS — Server Option 2

Goal: Full-featured headless server mode on open-Linux foundation, with maximum flexibility and performance.

⸻

🧠 1. Raspberry Pi Always-On TV Box (1-Channel PVR Node)

🎯 Role
	•	Acts as the primary TV recorder using one USB DVB-T tuner.
	•	Handles broadcast reception, scheduling, raw recording.
	•	Executes ad detection & processing locally or queues to server.
	•	Stores recordings locally.
	•	Shares cleaned media to network library.
	•	Provides fallback processing when server is unavailable.

📦 Hardware

Component	Specification
Raspberry Pi	Pi 4 (4GB/8GB)
TV Tuner	USB DVB-T2 (RTL2832U + R820T2 recommended)
Antenna	DVB-T directional/upgraded indoor or outdoor
Storage	USB3 SSD (≥1–2TB recommended)
Networking	Gigabit Ethernet

🧱 Software Stack

Component	Purpose
TVHeadend	PVR backend — scheduling & capture
Comskip	Ad detection
FFmpeg	Cutting/encoding
Samba/NFS	Network library export
Pi-hole (optional)	Network ad blocking
Systemd	Service management

🛠 Functional Flows

📍 Recording Pipeline

Antenna → USB tuner → TVHeadend → Raw .ts saved
             ↓
         Comskip → Markers
             ↓
         FFmpeg → Cleaned .mkv
             ↓
      Local library folder

📍 Processing Logic
	•	If Steam server reachable → queue job to remote host
	•	Else → process locally
	•	Final file exported to /media/library/TV

🧩 Failure Modes & Soft-Fail Logic

Condition	Behavior
Server offline	Pi processes locally
Network down	Pi caches and sync later
Multiple recordings	Reject or queue (single tuner limit)


⸻

🧠 2. SteamOS + Windows10 Kiosk (uHOME Server Option 1)

🎯 Role
	•	Optional hybrid gaming + media server tier.
	•	Acts as an administrative & heavy processing node.
	•	Available via HDMI kiosk on TV for system control and diagnostics.
	•	Offloads processing jobs from Pi.
	•	Optional Kodi playback directly.
	•	Hosts services when not gaming.

📦 Hardware + Environment

Component	Specification
PC	SteamOS installed
GPU	Gaming capable (GTX/RTX or AMD equivalent)
Storage	SSD + large HDD pool
OS	SteamOS + Windows10 dual boot or virtualization
Peripherals	HDMI to TV, Bluetooth keyboard


⸻

🧱 Software Stack (Primary)

Component	Purpose
SteamOS	Primary base OS
Windows10 (Kiosk)	Fortnite + gaming
TVHeadend (Linux)	Heavy tier PVR backend
File shares	Library sync & archive
Network services	Pi-hole / DNS / NTP

🤝 Integration with Pi
	•	Job Queueing: Pi enqueues processing tasks; SteamOS picks up and executes.
	•	Shared storage: Processed files mirrored.
	•	Kodi clients: Can point to SteamOS library share.
	•	Admin UI: TV usable for diagnostics / media browser.

⸻

🎮 Dual Boot / Multi-OS Setup

You can set up:

Disk:
 ├─ SteamOS partition
 ├─ Windows10 partition
 └─ Shared data partition (exFAT/NTFS for Windows + Linux access)

Or:

Linux host + Windows VM (GPU passthrough)

Note: True simultaneous OS operation requires virtualization to keep background services up while gaming.

⸻

🧠 3. Steam + Ubuntu/Alpine + uDOS (Server Option 2)

🎯 Role
	•	Headless, robust server tier for maximum control + performance.
	•	Runs core ingestion pipeline as authoritative master.
	•	Ideal for uDOS integration.
	•	Reduced GUI; CLI/Web admin.
	•	Target for future upgrades (Alpine when fully headless).

📦 Hardware + Environment

Component	Specification
PC / small server	x86-64 capable
CPU	Multicore Xeon/i7/Ryzen
RAM	16GB+
Storage	RAID/NAS integration
Ubuntu + Containers	Primary stack
Future target	Alpine headless


⸻

🧱 Software Stack

Component	Purpose
uDOS wizard	System control
tvheadend	PVR backend
comskip + ffmpeg	Processing pipeline
mongo/postgres	Metadata store
samba/NFS	Library shares
pi-hole	Network blocklist
systemd	Service orchestration

🛠 Architectural Patterns

📍 Headless Service Pods
	•	Capture pod
	•	Processing pod
	•	Library indexing pod
	•	Job queue manager
	•	NFS/Samba export pod

📍 Future Alpine Migration
	•	Migrate non-critical pods to Alpine
	•	Minimal base image footprint
	•	Leverage musl + BusyBox + container slices
	•	Primary orchestration via uDOS daemons

⸻

🔄 Cross-Stream Interactions

💡 Pi → SteamOS Sync

Post-Record Script (TVHeadend)

trigger_postprocessing.sh <recording.ts> {
    if steam_available; then
        send_to_steam queue
    else
        local_ffmpeg_clean
    fi
}

💾 Shared Storage

/media/library/TV/
 /media/library/Podcasts/
 /media/library/Radio/

Exported via:
	•	Samba (Windows + Linux)
	•	NFS (Linux clients)
	•	DLNA optional

📡 Client Access

Client	Access Path
Kodi Pi UI	//pi-library/TV
Steam Desktop	//steam-share/TV
Android/TV	Kodi + SMB/NFS
Mobile	Jellyfin/Plex (optional)


⸻

🧩 Kodi Library Schema

TV/
 ├─ Show/Series/
 │   ├─ S01/
 │   └─ S02/
Movies/
 ├─ PublicDomain/
 │   ├─ Noir/
 │   └─ SciFi/
Podcasts/
Radio/

Metadata:
	•	.nfo per file
	•	Local scraper only
	•	No cloud dependency

⸻

📘 Development Milestones

Phase 1 — Pi PVR Node
	•	USB tuner support & signal calibration
	•	TVHeadend install + channel mapping
	•	Comskip auto detection pipelines
	•	FFmpeg integration
	•	Local storage schema
	•	Job queue logic

Phase 2 — Server Option 1
	•	SteamOS + dual-boot support
	•	Shared storage setup
	•	Admin UI / kiosk tools
	•	Offload processing tests
	•	Sync reliability

Phase 3 — Server Option 2 (uDOS)
	•	Ubuntu + container base layer
	•	uDOS orchestration
	•	Headless deployment pattern
	•	Alpine migration roadmap
	•	Clusterable services

Phase 4 — Client UI
	•	Kodi curated UX
	•	WantMyMTV Web wrapper
	•	Radio/Podcasts plugin curation
	•	Pi-hole network hygiene integration

⸻

📊 Capability Matrix

Feature	Raspi PVR	SteamOS	uDOS/Alpine
Capture TV	✔	Optional	✔
Dual processing	Limited	High	Highest
Gaming	✘	✔	✘
Headless	✔	Partial	✔
Always-on	✔	✘	✔
Library share	SMB/NFS	SMB/NFS	SMB/NFS
Ad-free playback	✔	✔	✔


⸻

📌 Risks & Mitigations

Risk	Mitigation
Single tuner bottleneck	Add secondary tuner
Processing lag on Pi	Offload to server
Storage fill rate	Archival pruning policy
Network outages	Local caching + retry queue
Steam server down	Pi handles all capture


⸻

📌 Glossary of Terms
	•	PVR: Personal Video Recorder
	•	DVB-T/T2: Digital Video Broadcast (Australia)
	•	Comskip: Ad detection tool
	•	FFmpeg: Media processing engine
	•	TVHeadend: PVR backend server
	•	Kodi: Frontend playback UI
	•	Pi-hole: Network ad blocker
	•	uDOS: uHOME Operating System project framework
	•	Kiosk mode: Locked UI for non-admin use

⸻

If you want, I can also produce:

🔹 A step-by-step install guide for Phase 1
🔹 A job script template for post-processing
🔹 Kodi home layout mock
🔹 A hardware procurement checklist for AU

Just tell me which deliverable to generate next.

---

PREVIOUS (still relevant, may have been tweaked above)...

Here’s your refined **uDOS Lite (RPi4) + uHOME Media Player + Retro Game Pack** brief, including the ability to **boot from USB on a PC** for added flexibility. This creates a **niche, portable, and versatile media/retro gaming solution** that leverages the Raspberry Pi 4’s strengths while extending functionality to x86 PCs via USB boot.

---

# **uDOS Lite + uHOME Media Player & Retro Game Pack**
**Project Name**: uDOS Lite Hybrid (RPi4 + USB Boot for PC)
**Version**: 1.0
**Date**: February 25, 2026
**Author**: Fred Porter / uDOS Team

---

## **1. Overview**
**uDOS Lite Hybrid** combines:
1. **Raspberry Pi 4 (ARM)** as a **dedicated retro gaming and media center** (uHOME Media Player + RetroArch).
2. **USB-bootable uDOS Lite for x86 PCs**, allowing the same experience on any PC via USB.
3. **Sonic-compatible reflashing** for bulk deployment.

This creates a **niche, portable, and dual-platform** solution for **media, retro gaming, and lightweight PC use**.

---

## **2. Objectives**
| **Goal**                          | **Priority** | **Notes**                                  |
|-----------------------------------|--------------|--------------------------------------------|
| **Retro gaming console** (RPi4)  | High         | RetroArch + uHOME-themed UI.               |
| **uHOME Media Player**           | High         | Plex/Kodi + custom uHOME skin.             |
| **USB-bootable for PC**          | High         | Extends uDOS Lite to x86 PCs.               |
| **Sonic reflashing support**     | High         | Automate deployment for RPi4 and USB.     |
| **Controller-only navigation**   | High         | No keyboard/mouse required.                |
| **Low cost**                     | High         | Under $150 AUD per unit.                   |

---

## **3. Hardware Specifications**
### **A. Raspberry Pi 4 (Primary Device)**
| **Component**       | **Requirement**               | **Notes**                                  |
|----------------------|-------------------------------|--------------------------------------------|
| **Raspberry Pi 4**   | 8GB model                     | For multitasking (Plex + RetroArch).      |
| **Storage**          | 128GB USB SSD                 | Faster than microSD.                       |
| **Power Supply**     | Official RPi 4 PSU (5V/3A)   | Avoid cheap PSUs.                          |
| **Cooling**          | Argon One case (passive fan)  | Prevents throttling.                       |
| **Controller**       | 8BitDo Pro 2 (Bluetooth)      | Xbox/PlayStation layout.                   |

**Budget**: **$120–$150 AUD** (including SSD and case).

### **B. USB-Bootable uDOS Lite (for PC)**
| **Component**       | **Requirement**               | **Notes**                                  |
|----------------------|-------------------------------|--------------------------------------------|
| **USB Drive**        | 128GB USB 3.0                 | Fast read/write for OS.                   |
| **PC Requirements**  | Any x86 PC with USB boot     | Modern PCs (2015+) support USB boot.      |
| **GUI**             | Openbox + uHOME thin layer    | Lightweight, controller-friendly.          |

**Budget**: **$20–$30 AUD** (USB drive only; assumes PC already owned).

---

## **4. Software Stack**
### **A. Raspberry Pi 4 (ARM)**
| **Component**          | **Technology**               | **Purpose**                                  |
|-------------------------|-------------------------------|----------------------------------------------|
| **OS Base**             | Raspberry Pi OS Lite (64-bit) | Minimal overhead.                           |
| **Retro Gaming**        | RetroArch                    | Multi-system emulator (NES–PS1).           |
| **Media Center**        | Kodi + uHOME Skin             | Customized media UI.                        |
| **Media Server**        | Plex Media Server            | Host and stream media.                     |
| **GUI**                | Openbox + uHOME Thin Layer    | Lightweight, controller-friendly.          |
| **Bootloader**          | Custom uDOS Lite Bootloader   | Sonic-compatible reflashing.               |

### **B. USB-Bootable uDOS Lite (x86)**
| **Component**          | **Technology**               | **Purpose**                                  |
|-------------------------|-------------------------------|----------------------------------------------|
| **OS Base**             | Alpine Linux (x86)           | Lightweight, fast boot.                     |
| **Retro Gaming**        | RetroArch                    | Same experience as RPi4.                    |
| **Media Center**        | Kodi + uHOME Skin             | Consistent UI across platforms.              |
| **GUI**                | Openbox + uHOME Thin Layer    | Controller-friendly.                        |
| **Bootloader**          | GRUB (USB-bootable)          | Works on most x86 PCs.                       |

---

## **5. Core Features**
### **A. uHOME Media Player (RPi4 + USB)**
- **Plex Server**:
  - Pre-configured libraries (`/media/movies`, `/media/tv`).
  - **Direct play** for 1080p (4K limited by RPi4 CPU).
- **Kodi**:
  - **uHOME-themed skin** (matching RetroArch UI).
  - **Controller navigation** (no keyboard needed).
- **Media Sync**:
  - **USB drive** syncs media libraries between RPi4 and PC.

### **B. Retro Game Pack (RPi4 + USB)**
- **RetroArch**:
  - Pre-loaded with **NES, SNES, Genesis, PS1** cores.
  - **uHOME-themed bezels/overlays**.
  - **Controller auto-mapping** (XInput/DInput).
- **ROM Management**:
  - **Sonic deploys ROMs** to `/home/uhome/roms/`.
  - **Auto-scraping** for metadata (Skraper).
- **Save Sync**:
  - **USB drive** syncs save states between RPi4 and PC.

### **C. USB-Bootable uDOS Lite for PC**
- **Portable uDOS**:
  - Boot from USB on **any x86 PC** (no installation needed).
  - **Same UI/UX** as RPi4 (Openbox + uHOME Thin Layer).
- **Performance**:
  - **Faster on PC** (x86 CPU/GPU).
  - **RetroArch**: Full speed for **PS1/N64** (vs. RPi4’s PS1 limit).
- **Use Cases**:
  - **Travel-friendly retro gaming**.
  - **Temporary media center** (hotels, friend’s PC).

### **D. Sonic Reflashing Support**
- **RPi4 Image**:
  - **Single-command deployment**:
    ```bash
    curl -sSL https://udos.io/rpi4-install | bash
    ```
  - **Partitions**:
    - `/boot`: 256MB (FAT32).
    - `/`: 8GB (ext4, OS).
    - `/home`: Remaining space (ext4, ROMs/media).
- **USB Image**:
  - **GRUB-configurable** for x86 USB boot.
  - **Sonic pushes updates** to USB drive.

---

## **6. Development Phases**
| **Phase**               | **Tasks**                                                                 | **Timeframe** | **Dependencies**          |
|--------------------------|---------------------------------------------------------------------------|---------------|----------------------------|
| **1. Hardware Procurement** | Order RPi4, USB SSDs, and USB drives.                                  | 1 week         | Budget approval.          |
| **2. RPi4 OS Base Setup**  | Install Raspberry Pi OS Lite + Openbox.                                  | 2 days         | Hardware ready.           |
| **3. RetroArch + uHOME**  | Configure RetroArch + uHOME theme/bezels.                               | 3 days         | OS base complete.         |
| **4. Media Center**      | Install Plex/Kodi + uHOME skin.                                          | 2 days         | RetroArch working.        |
| **5. USB-Bootable Alpine**| Create Alpine + uHOME USB image.                                          | 3 days         | Media center tested.      |
| **6. Sonic Integration** | Develop ARM/x86 Sonic installers.                                         | 3 days         | USB image ready.          |
| **7. Testing & QA**      | Functional, user, and stress testing.                                   | 1 week         | All phases complete.      |

**Total Timeline**: **3–4 weeks**.

---

## **7. Technical Specifications**
### **A. RPi4: RetroArch + uHOME Media Player**
#### **RetroArch Configuration**
```bash
# Install RetroArch
sudo apt install retroarch

# uHOME RetroArch Config
mkdir -p /home/uhome/.config/retroarch
cat > /home/uhome/.config/retroarch/retroarch.cfg <<EOF
video_driver = "dispmanx"
audio_driver = "alsa"
input_driver = "udev"
menu_driver = "rgui"
video_smooth = true
video_shader_enable = true
EOF

# Download uHOME Bezels
git clone https://github.com/udos/retroarch-bezels /home/uhome/.config/retroarch/overlays/udos
```

#### **uHOME Kodi Skin**
```bash
# Install Kodi + uHOME Skin
sudo apt install kodi
git clone https://github.com/udos/kodi-skin-uhome /home/uhome/.kodi/addons/skin.uhome
```

### **B. USB-Bootable Alpine: GRUB Configuration**
#### **GRUB Config for USB Boot**
```bash
# Install GRUB to USB
sudo grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=uDOS --recheck

# Edit /boot/grub/grub.cfg
menuentry "uDOS Lite (USB)" {
    linux /boot/vmlinuz-lts root=/dev/sdb1 quiet
    initrd /boot/initramfs-lts.img
}
```

### **C. Sonic Deployment Scripts**
#### **RPi4 Installer**
```bash
#!/bin/bash
# uDOS Lite RPi4 Installer
sudo apt update && sudo apt upgrade -y
sudo apt install -y retroarch kodi plexmediaserver openbox lightdm
git clone https://github.com/udos/udos-lite-rpi4 /home/uhome/udos
chmod +x /home/uhome/udos/scripts/*.sh
```

#### **USB Installer (Alpine)**
```bash
#!/bin/bash
# uDOS Lite USB Installer (x86)
apk add retroarch kodi openbox lightdm
git clone https://github.com/udos/udos-lite-usb /mnt/usb/udos
```

---

## **8. Performance Expectations**
| **Task**               | **RPi4 Performance**               | **USB (x86) Performance**          | **Notes**                          |
|-------------------------|------------------------------------|------------------------------------|------------------------------------|
| **RetroArch (PS1)**     | ✅ 60 FPS (full speed)            | ✅ 60 FPS + (N64/PS2 possible)     | RPi4 limited to PS1.              |
| **Kodi (1080p)**        | ✅ Smooth playback                | ✅ Smooth playback                |                                    |
| **Plex (1080p)**        | ✅ Direct play                    | ✅ Direct play + transcoding       | x86 handles 4K transcoding better. |
| **Boot Time**           | ~15 seconds                       | ~10 seconds                       | USB SSD faster than microSD.      |
| **Controller Input**    | ✅ Native support                | ✅ Native support                |                                    |

---

## **9. Testing Plan**
### **A. Functional Testing**
| **Test**                     | **Criteria**                                  | **Pass/Fail** |
|------------------------------|-----------------------------------------------|---------------|
| RetroArch (PS1) on RPi4      | Loads ROMs, 60 FPS, no audio glitches.        |               |
| RetroArch (N64) on USB       | Loads ROMs, 30+ FPS.                         |               |
| Kodi (1080p) on RPi4         | Plays MKV/MP4 without buffering.             |               |
| Kodi (4K) on USB             | Plays 4K H.264 without buffering.            |               |
| Plex (Direct Play) on RPi4   | Streams 1080p MKV to client.                 |               |
| Plex (Transcode) on USB      | Transcodes 1080p to 720p.                    |               |
| USB Boot on PC              | Boots on 3+ different PCs.                   |               |
| Sonic Deployment            | Flashes RPi4 and USB in <10 mins.            |               |

### **B. User Testing**
- **Participants**: 5 uDOS team members.
- **Tasks**:
  1. Boot RPi4 and USB on PC.
  2. Navigate uHOME menu with controller.
  3. Play a PS1 game on RetroArch.
  4. Stream media via Kodi/Plex.
- **Feedback**: Rate ease of use (1–5).

### **C. Stress Testing**
- **Plex + RetroArch**: Run both simultaneously on RPi4.
- **Thermals**: Monitor CPU temp under load (`vcgencmd measure_temp`).
- **USB Longevity**: Test read/write cycles on USB drive.

---

## **10. Risks and Mitigations**
| **Risk**                          | **Mitigation**                                  |
|-----------------------------------|------------------------------------------------|
| **RPi4 thermal throttling**       | Use **Argon One case + passive cooling**.      |
| **USB drive corruption**         | Use **high-endurance USB** (e.g., Samsung Fit).|
| **RetroArch performance (RPi4)**  | Limit to **PS1 and older**.                   |
| **Plex transcoding (RPi4)**       | Use **direct play** where possible.           |
| **Sonic ARM/x86 compatibility**   | Test on **RPi3/4 and x86 PCs**.               |

---

## **11. Budget Breakdown**
| **Item**               | **Estimated Cost (AUD)** | **Notes**                     |
|-------------------------|--------------------------|--------------------------------|
| Raspberry Pi 4 (8GB)    | $80                      | Official retailer.            |
| USB SSD (128GB)         | $30                      | For RPi4.                     |
| USB Drive (128GB)       | $25                      | For x86 USB boot.             |
| Argon One Case          | $25                      | Includes cooling.             |
| 8BitDo Controller       | $40                      | Bluetooth.                    |
| **Total**              | **$200**                 | Per full setup (RPi4 + USB).  |

---
**Note**: Costs can be reduced by reusing existing USB drives/controllers.

---

## **12. Deployment Checklist**
### **A. Raspberry Pi 4**
- [ ] Procure RPi4, USB SSD, and case.
- [ ] Flash **uDOS Lite RPi4 image** via Sonic.
- [ ] Test RetroArch, Kodi, and Plex.
- [ ] Configure controller mappings.

### **B. USB-Bootable uDOS Lite**
- [ ] Create **Alpine USB image** with uHOME GUI.
- [ ] Test boot on **3+ x86 PCs**.
- [ ] Sync RetroArch saves/media with RPi4.

### **C. Sonic Integration**
- [ ] Develop **ARM (RPi4) and x86 (USB) installers**.
- [ ] Test **bulk deployment** to 5+ devices.

---

## **13. Final Recommendations**
### **Why This Works**
✅ **Niche Appeal**:
- **Retro gaming + media center** in one device.
- **Portable USB boot** extends uDOS to any PC.
- **Low cost** (<$200 AUD for full setup).

✅ **Flexibility**:
- Use **RPi4 at home** (dedicated device).
- Use **USB on PCs** (travel, friends’ houses).

✅ **Sonic-Compatible**:
- **Reflash RPi4 and USB drives** with one tool.

### **Next Steps**
1. **Procure hardware** (RPi4, USB drives).
2. **Develop uDOS Lite images** (RPi4 + USB).
3. **Integrate RetroArch + uHOME Media Player**.
4. **Test USB boot on x86 PCs**.
5. **Finalize Sonic deployment scripts**.

---
**Approval**:
- **Fred Porter**: [Approved] ✅
- **uDOS Team**: [Reviewed] ✅

**Next Review**: March 20, 2026 (Prototype Demo + USB Boot Test).