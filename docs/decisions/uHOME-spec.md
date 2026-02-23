uHOME OS v1.2.1

Broadcast DVR Node (Unpaid Stack)

Packaged & Installed by uDOS Sonic

⸻

1. Overview

uHOME OS v1.2.1 introduces a local broadcast ingestion and ad-filtered DVR system designed to:
	•	Ingest free-to-air TV via antenna
	•	Convert RF broadcast to IP streams
	•	Record scheduled or rule-based programming
	•	Automatically detect and remove commercials (unpaid stack)
	•	Build a growing ad-free movie/news archive
	•	Provide time-shifted viewing (watch delayed instead of live)
	•	Serve media to Smart TVs via LAN

This version is:
	•	Fully local
	•	No subscription required
	•	No cloud dependencies
	•	No Plex Pass
	•	Compatible with uDOS Sonic deployment model

⸻

2. System Philosophy

uHOME becomes the Broadcast Brain of the household.

The Smart TV becomes a display.
The antenna becomes a data source.
The network becomes the transport.

This aligns with:
	•	Offline-first design
	•	Deterministic infrastructure
	•	Sovereign media processing
	•	Minimal vendor lock-in

⸻

3. Physical Architecture

3.1 Recommended Hardware Topology

[Antenna]
     ↓
[HDHomeRun Network Tuner]
     ↓ (Ethernet)
[Router / Switch]
     ↓
[uHOME Machine]
     ↓ (Ethernet preferred / Wi-Fi supported)
[Smart TV]

Alternative (direct display mode):

[Antenna]
     ↓
[HDHomeRun]
     ↓
[uHOME]
     ↓ (HDMI)
[Smart TV]


⸻

4. Hardware Requirements

4.1 Required Components

Network Tuner

Example class:
	•	SiliconDust HDHomeRun (DVB-T/T2 for AU, ATSC for US)

Requirements:
	•	Ethernet connectivity
	•	Minimum dual tuner recommended (4 ideal)
	•	MPEG-TS IP output

uHOME Machine

Minimum:
	•	Quad-core CPU
	•	8GB RAM
	•	256GB SSD (OS)
	•	2TB+ storage for recordings
	•	Gigabit Ethernet

Recommended:
	•	16GB RAM
	•	4TB–8TB storage
	•	Hardware video encoding support (optional future use)

⸻

5. Software Stack (Unpaid)

Installed and configured by uDOS Sonic.

5.1 Core Components

Component	Role
Windows 10 (Entertainment mode)	Host OS
Jellyfin	Media server + DVR engine
Comskip	Commercial detection
FFmpeg	Optional commercial cutting
PowerShell / Python scripts	Post-processing automation

No paid services required.

⸻

6. Broadcast Ingestion Flow

6.1 Channel Acquisition
	1.	Antenna feeds HDHomeRun.
	2.	HDHomeRun exposes channels over LAN.
	3.	Jellyfin scans tuner and EPG.
	4.	Channels indexed in uHOME library.

Smart TV is NOT used as signal source.

⸻

7. DVR Operation Model

7.1 Scheduled Recording

User configures:
	•	Programme-based rules
	•	Channel-based rules
	•	Time-block rules
	•	“Record any Movie” rule

Jellyfin records MPEG-TS streams directly from HDHomeRun.

Files stored under:

/Media/Recordings/Raw/


⸻

8. Ad Detection & Removal Pipeline

8.1 Post-Processing Workflow

Triggered after recording completes:

Raw Recording
      ↓
Comskip analysis
      ↓
Generate .edl file
      ↓
Option A: Mark for skip
Option B: Hard cut + reassemble
      ↓
Move to Clean Library


⸻

8.2 Modes

Mode A — Skip Markers (Fast)
	•	No re-encoding
	•	Player skips ads
	•	Lower CPU usage

Mode B — Hard Cut (Archival)
	•	Ads permanently removed
	•	Clean standalone files
	•	Recommended for movie harvesting

Nightly batch process recommended.

⸻

9. Background Broadcast Movie Harvester

This is a key v1.2.1 feature.

9.1 Rule-Based Capture

uHOME can:
	•	Record any programme tagged “Movie”
	•	Record specific channels at specific times
	•	Record recurring film blocks

9.2 Nightly Processing

At 2am:
	1.	Run Comskip on all new recordings
	2.	Remove ads
	3.	Fetch metadata
	4.	Rename cleanly
	5.	Move to:

/Media/Movies/Broadcast/

Result:
An automatically growing ad-free movie library sourced from free-to-air TV.

No manual channel switching required.

⸻

10. Time-Shift Viewing Model

Instead of watching live:
	1.	Select channel.
	2.	Recording starts immediately.
	3.	Wait 15–30 minutes.
	4.	Begin playback from start.

By first ad break:
	•	Detection is complete.
	•	Ads skipped automatically.

This is the preferred method over live muting.

⸻

11. Smart TV Integration

11.1 Primary Mode

Smart TV runs Jellyfin client app.

uHOME streams over LAN.

Ethernet preferred.
Wi-Fi supported for 1080p.

⸻

11.2 HDMI Mode

uHOME connected directly to TV via HDMI.

Full uDOS interface available.

⸻

12. Sonic Packaging

uDOS Sonic installer performs:
	1.	Detect HDHomeRun on LAN
	2.	Install Jellyfin silently
	3.	Configure tuner
	4.	Install Comskip
	5.	Deploy processing scripts
	6.	Configure directory structure
	7.	Create default rules:
	•	Record Movies
	•	Record 6pm News
	8.	Enable nightly processing task
	9.	Add firewall rules
	10.	Validate playback to Smart TV

⸻

13. Directory Structure

/Media
   /Recordings
       /Raw
       /Processing
   /Movies
       /Broadcast
   /TV
       /Broadcast
/Logs
   /Comskip
   /DVR


⸻

14. Performance Considerations
	•	Comskip CPU-intensive on first run
	•	Use scheduled processing during low-usage hours
	•	Multi-tuner allows simultaneous record + playback

⸻

15. Future Expansion (Not in 1.2.1)
	•	Smart mute overlay
	•	GPU-accelerated ad detection
	•	uHOME UI skin over Jellyfin
	•	Sonic Device DB codec tuning
	•	Auto-archive pruning rules
	•	Broadcast analytics dashboard

⸻

16. Security Model
	•	LAN-only exposure by default
	•	No external port forwarding
	•	No cloud login required
	•	All recordings stored locally
	•	Sonic validates network isolation

⸻

17. Version Summary

uHOME OS v1.2.1 introduces:
	•	Network broadcast ingestion
	•	Unpaid DVR engine
	•	Automated ad detection
	•	Background movie harvesting
	•	Time-shift viewing
	•	Smart TV LAN streaming
	•	Sonic automated deployment

It transforms uHOME into a sovereign broadcast processing node.

⸻

Good catch — those are mandatory for this to feel like a true “console replacement” and not just a headless server.

Below is the updated and hardened hardware spec for:
	•	HDHomeRun FLEX (4 tuners)
	•	Mini PC (Ryzen 5 / i5)
	•	16GB RAM
	•	4TB internal
	•	HDMI output required
	•	Full game-controller support required

Target: uHOME OS v1.2.1 — Living Room Broadcast Console

⸻

uHOME OS v1.2.1

Broadcast Console Hardware Specification (Finalised)

⸻

1. System Role

This Mini PC is not just a DVR node.

It is:
	•	Broadcast ingestion engine
	•	Ad-processing system
	•	Media server
	•	Primary TV interface
	•	Game-controller driven media console

It must behave like a living-room appliance.

⸻

2. Physical Architecture

Antenna (coax)
     ↓
HDHomeRun FLEX (4 tuners)
     ↓ Ethernet
Router / Switch
     ↓ Ethernet
uHOME Mini PC
     ↓ HDMI
Smart TV

Game controller connects to:

Game Controller → Bluetooth or USB → uHOME Mini PC


⸻

3. Mini PC Hardware Requirements (Mandatory)

3.1 CPU
	•	AMD Ryzen 5 (6 cores minimum)
OR
	•	Intel Core i5 (8th gen or newer)

Must support:
	•	Hardware video decode (H.264 / H.265)
	•	Smooth 1080p/4K playback
	•	Background processing

⸻

3.2 RAM
	•	16GB DDR4 minimum
	•	Dual channel preferred

⸻

3.3 Storage
	•	512GB NVMe SSD (OS + apps)
	•	4TB internal drive (media storage)

Media drive can be:
	•	SATA SSD (preferred for silence)
	•	5400/7200 RPM HDD (acceptable for budget)

⸻

3.4 HDMI Output (Mandatory)

Mini PC must include:
	•	HDMI 2.0 or higher
	•	1080p60 minimum
	•	4K output preferred
	•	Audio over HDMI (multichannel passthrough)

This allows:
	•	Direct connection to Smart TV
	•	Boot-to-TV experience
	•	Full console replacement mode

⸻

3.5 Game Controller Support (Mandatory)

The Mini PC must support:
	•	Bluetooth 5.0 (or newer)
	•	At least 2 USB-A ports
	•	XInput compatible controllers
	•	DirectInput support fallback

Supported controller types:
	•	Xbox controller (wired or Bluetooth)
	•	PlayStation controller (Bluetooth)
	•	8BitDo
	•	Generic USB controllers

Windows 10 has native controller support.

uHOME will support:
	•	D-pad navigation
	•	Trigger-based seek
	•	One-button “Smart Mute”
	•	One-button “Watch Delayed”
	•	Full media control

⸻

4. Living Room Behaviour Requirements

To function as a console:

4.1 Boot Mode
	•	Auto-login to uHOME profile
	•	Launch uHOME Broadcast Panel on startup
	•	Optional full-screen Jellyfin mode

⸻

4.2 Power Behaviour
	•	Disable aggressive sleep
	•	Wake on controller input
	•	Wake on LAN enabled
	•	Resume to last interface

⸻

4.3 Audio
	•	HDMI audio passthrough
	•	Bitstream support if AVR present
	•	Stereo fallback if TV only

⸻

5. Performance Envelope

This configuration supports:
	•	4 simultaneous recordings
	•	1–2 concurrent playback streams
	•	Comskip analysis in background
	•	FFmpeg cutting overnight
	•	Smooth controller UI navigation

All while remaining quiet and low power.

⸻

6. Why Controller Support Matters

This converts uHOME from:

“Headless server under the TV”

Into:

“Broadcast + Media Console”

Controller allows:
	•	Sofa navigation
	•	No keyboard required
	•	No mouse required
	•	Seamless family use
	•	Familiar console UX

⸻

7. Final Approved Hardware Profile

Required Devices

RF Front-End
	•	HDHomeRun FLEX (4 tuners)

Console Node

Mini PC with:
	•	Ryzen 5 or i5
	•	16GB RAM
	•	512GB NVMe
	•	4TB internal
	•	HDMI 2.0+
	•	Bluetooth 5.0
	•	2+ USB ports
	•	Gigabit Ethernet

Optional
	•	NAS for expansion
	•	AVR for audio passthrough

⸻

8. What This System Now Replaces
	•	Smart TV internal tuner
	•	Smart TV USB DVR
	•	Plex subscription
	•	Streaming box
	•	Xbox media mode

It becomes:

A sovereign broadcast console.

⸻
