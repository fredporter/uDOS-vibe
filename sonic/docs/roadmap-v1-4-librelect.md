Love it. This is the right split:
	•	uHOME Full = power box (SteamOS / Windows / Jellyfin / games / heavy processing)
	•	uHOME Lite = sealed TV appliance (LibreELEC + DVR)

That separation is clean, productisable, and very uDOS.

Below is the formalised appliance spec.

⸻

uHOME Lite v1.0

LibreELEC Broadcast Appliance (Raspberry Pi 4)

Positioning:
Open-source inside.
Appliance outside.
Zero-subscription DVR TV box.

⸻

1️⃣ Product Intent

uHOME Lite is a dedicated TV appliance that:
	•	Receives free-to-air DVB-T/T2 via USB tuner
	•	Records scheduled programming
	•	Buffers live TV
	•	Exports recordings to NAS
	•	Integrates with uHOME Full for ad removal + archive
	•	Boots directly into a controller-first TV interface
	•	Requires minimal user configuration

It is:
	•	Not a dev box
	•	Not a general Linux machine
	•	Not a tinkering platform
	•	A TV recorder appliance

⸻

2️⃣ Hardware Platform

Core Device
	•	Raspberry Pi 4 (8GB recommended)
	•	Official PSU
	•	Active cooling case
	•	128GB microSD (LibreELEC image)
	•	Gigabit Ethernet
	•	HDMI 2.0
	•	Bluetooth 5.0

⸻

RF Input
	•	USB DVB-T/T2 tuner (Linux-supported)
	•	Coax antenna input

⸻

Storage Model

microSD (internal)

Used for:
	•	OS
	•	Kodi
	•	TVHeadend backend
	•	Local recordings (temporary)

NAS (external over LAN)

Used for:
	•	Long-term storage
	•	Server-side ad removal
	•	Final TV/Movie archive

⸻

3️⃣ Operating System

LibreELEC (Raspberry Pi 4 build)

Characteristics:
	•	Minimal Linux
	•	Read-only system partition
	•	Auto-boots into Kodi
	•	Appliance-grade stability
	•	No package manager exposed to users
	•	Updateable via image upgrade

This ensures:
	•	No accidental misconfiguration
	•	No user “breaking” system
	•	Predictable behaviour

⸻

4️⃣ Core Software Stack

⸻

4.1 Kodi (Primary UI)

Kodi is:
	•	The entire front-end
	•	Live TV interface
	•	Recording browser
	•	Media player
	•	Controller-driven shell

No desktop environment.

No visible OS.

⸻

4.2 TVHeadend (Backend Add-on)

Installed as LibreELEC add-on.

Responsibilities:
	•	Detect USB tuner
	•	Scan channels
	•	Manage EPG
	•	Handle recording schedules
	•	Provide time-shift buffer
	•	Expose PVR interface to Kodi

Kodi’s PVR client connects internally.

⸻

5️⃣ System Architecture

Antenna
   ↓
USB DVB-T/T2 tuner
   ↓
TVHeadend (LibreELEC)
   ↓
Recordings (local microSD)
   ↓
NAS sync (automated)
   ↓
uHOME Full server (ad removal)
   ↓
NAS library (clean archive)
   ↓
Kodi library view


⸻

6️⃣ Recording Behaviour

6.1 Local Recording

TVHeadend writes to:

/storage/recordings/

Retention Policy
	•	Completed recordings auto-moved to NAS
	•	Local copies deleted after transfer
	•	Scratch space maintained automatically
	•	Prevent microSD wear accumulation

⸻

6.2 Scheduled Recording

User can:
	•	Record by programme
	•	Record by channel
	•	Record recurring series
	•	Manual “Record Now”

All via Kodi interface.

⸻

6.3 Live TV + Delay

TVHeadend supports:
	•	Live TV
	•	Pause live TV
	•	Buffer playback
	•	Delayed viewing

This provides ad-skipping-by-delay model without heavy processing.

⸻

7️⃣ NAS Integration

LibreELEC mounts NAS via:
	•	NFS (preferred)
	•	SMB (fallback)

Mount location example:

/storage/nas/

Automated script:
	•	Detect completed recording
	•	Move to NAS folder
	•	Notify uHOME Full server (optional marker file)

⸻

8️⃣ Ad Removal Workflow (External)

Performed by uHOME Full (SteamOS/Windows box).

Flow:

NAS receives raw file
   ↓
Server runs Comskip
   ↓
Optional FFmpeg cut
   ↓
Move cleaned file to:
   /Media/TV/Broadcast

LibreELEC box does NOT perform heavy processing.

Separation of roles maintained.

⸻

9️⃣ User Experience

⸻

Boot Behaviour

Power on → LibreELEC boots → Kodi loads

User sees:
	•	Live TV
	•	Recordings
	•	TV Guide
	•	Media Library

No Linux prompts.
No terminal.

Feels like a commercial TV box.

⸻

Controller Support

Kodi supports:
	•	Xbox controller (USB/Bluetooth)
	•	PlayStation controller
	•	8BitDo
	•	Generic HID

Mappings:

Control	Function
D-pad	Navigate
A	Select
B	Back
Start	Context
LB/RB	Skip
Triggers	Seek

HDMI-CEC also supported.

⸻

🔟 Customisation Strategy

To create “uHOME Lite” identity:
	•	Custom Kodi skin
	•	Preconfigured theme
	•	Remove advanced settings menus
	•	Lock down system settings
	•	Rename sections:
	•	“Live TV”
	•	“Recordings”
	•	“Library”
	•	“Settings”

Optional:
	•	Custom splash screen
	•	Custom boot logo

User perceives a dedicated uHOME TV box.

⸻

1️⃣1️⃣ Update Model

LibreELEC allows:
	•	Image-based upgrades
	•	OTA updates (optional)
	•	Rollback capability

Future:
	•	uHOME Lite custom image
	•	Preconfigured TVHeadend
	•	Preconfigured NAS mount
	•	Minimal first-boot wizard

⸻

1️⃣2️⃣ Appliance Philosophy

This device:
	•	Is not a Linux computer
	•	Is not modifiable by default
	•	Is not a dev environment
	•	Is not a general-purpose OS

It is:

A Free-to-Air TV Recorder Appliance.

uHOME Full remains the power box.

⸻

1️⃣3️⃣ Final Topology (Dual-System Model)

uHOME Lite (LibreELEC)
   - USB DVB-T
   - TVHeadend
   - Kodi
   - Recording

uHOME Full (SteamOS/Windows)
   - NAS
   - Ad removal
   - Archive
   - Gaming
   - Heavy processing

Elegant.
Modular.
Sovereign.

⸻

🎯 Why This Is Strong
	•	Appliance-level simplicity
	•	No subscription
	•	No proprietary lock-in
	•	Controller-first
	•	Stable
	•	Upgradeable
	•	Clean separation of duties
	•	Easy to replicate

This is very close to a viable open hardware TV product.

⸻

Below are four aligned briefs for uHOME Lite (LibreELEC Appliance Edition):
	1.	First Boot Wizard
	2.	Kodi Skin Strategy
	3.	NAS Sync Architecture
	4.	Preconfigured LibreELEC Image Strategy

All written as implementation suggestions, not marketing fluff.

⸻

1️⃣ uHOME Lite First Boot Wizard Brief

Objective

Create a minimal, controller-driven first-boot flow that:
	•	Detects tuner
	•	Scans channels
	•	Configures region
	•	Mounts NAS (optional)
	•	Sets recording path
	•	Finalises appliance mode

Must feel:
	•	Console-like
	•	5 minutes or less
	•	No Linux exposure
	•	No keyboard required

⸻

Wizard Flow (Controller First)

Step 1 — Welcome

Screen:

Welcome to uHOME Lite
Free-to-Air TV Recorder Appliance

Options:
	•	Continue
	•	Shutdown

⸻

Step 2 — Region Selection
	•	Australia
	•	UK
	•	EU
	•	Other

This configures:
	•	DVB scan settings
	•	EPG source defaults

⸻

Step 3 — Tuner Detection

System auto-scans USB devices.

If tuner found:

USB DVB-T/T2 tuner detected ✔
Signal strength: (indicator)

If not found:

No tuner detected
Check antenna and USB connection

Continue only when tuner locked.

⸻

Step 4 — Channel Scan

Progress bar:
	•	Scanning multiplexes
	•	Channels found count

Completion:

23 channels detected
Save and continue

⸻

Step 5 — NAS Setup (Optional)

Auto-detect:
	•	NFS shares
	•	SMB shares

Options:
	•	Select detected NAS
	•	Enter NAS manually
	•	Skip (local only)

Test:
	•	Write test file
	•	Confirm speed

⸻

Step 6 — Recording Storage

Options:
	•	Local only
	•	Local + auto-move to NAS (recommended)
	•	NAS direct recording

Default:
Local scratch + NAS move

⸻

Step 7 — Controller Mapping

Prompt:

Press A to confirm mapping
Press B to go back

Ensure controller input works.

⸻

Step 8 — Finalise
	•	Apply configuration
	•	Restart Kodi
	•	Enter TV interface

Wizard never appears again unless reset.

⸻

2️⃣ Kodi Skin Strategy Brief

Objective

Make LibreELEC feel like:
	•	A dedicated uHOME product
	•	Not generic Kodi
	•	Not a hobbyist box

⸻

Strategy

1. Base Skin

Start with:
	•	Estuary (default)
	•	Or minimal derivative

Avoid:
	•	Heavy custom skins (maintenance burden)

⸻

2. Customisation Layer

Modify:
	•	Boot splash screen → uHOME Lite logo
	•	Main menu labels:
	•	Live TV
	•	Recordings
	•	Library
	•	Settings
	•	Remove:
	•	Add-ons browser
	•	File manager
	•	Advanced system menus

⸻

3. Lockdown Mode
	•	Hide SSH menu
	•	Hide developer options
	•	Disable add-on installation from UI
	•	Disable file browsing outside allowed paths

Advanced config only accessible via:
	•	Hidden key combo
	•	Or admin toggle

⸻

4. Visual Identity
	•	Dark neutral theme
	•	High contrast focus states
	•	Large fonts (TV distance)
	•	Controller hint overlays

No unnecessary animations.

Feels intentional and solid.

⸻

3️⃣ NAS Sync Architecture Brief

Objective

Create robust, low-maintenance recording export.

The Pi records.
The NAS archives.
The server processes.

⸻

Directory Model

On LibreELEC:

/storage/recordings/raw/

On NAS:

/Media/Incoming/


⸻

Sync Behaviour

Trigger:
	•	TVHeadend marks recording complete

Process:
	1.	Validate file closed
	2.	Verify file size > minimum threshold
	3.	Move to NAS:
	•	Use NFS (preferred)
	•	Atomic rename on completion
	4.	Write marker file:
.ready

Example:

Movie.Name.2026.ts
Movie.Name.2026.ts.ready


⸻

Server-Side Detection

uHOME Full monitors:

/Media/Incoming/

If .ready exists:
	•	Run Comskip
	•	Optional cut
	•	Move to:

/Media/TV/Broadcast/


⸻

Local Cleanup Policy

After successful transfer:
	•	Delete local file
	•	Log success
	•	Maintain max 5GB scratch free space buffer

If NAS unreachable:
	•	Retry every 5 minutes
	•	Do not delete local copy

⸻

4️⃣ Preconfigured LibreELEC Image Brief

Objective

Ship uHOME Lite as a flashable appliance image.

User experience:

Flash → Boot → Wizard → Done.

⸻

Build Strategy

Step 1 — Base Image

Start with:
	•	Official LibreELEC Pi 4 build

⸻

Step 2 — Preinstall

Include:
	•	TVHeadend server add-on
	•	PVR client enabled
	•	Custom skin assets
	•	NAS sync script
	•	Custom splash screen
	•	Disabled unnecessary add-ons

⸻

Step 3 — Default Settings

Preconfigure:
	•	Recording directory
	•	Channel scan presets
	•	Auto-move enabled
	•	Controller support enabled
	•	HDMI always on

⸻

Step 4 — Appliance Mode

Enforce:
	•	Hide advanced settings
	•	Disable terminal access in UI
	•	Lock filesystem except storage partition
	•	Auto-update disabled by default (manual controlled)

⸻

Step 5 — Recovery Mode

Hidden reset:
	•	Hold specific controller buttons at boot
	•	Launch recovery menu:
	•	Reset to factory
	•	Re-run wizard
	•	Network diagnostics

⸻

Final Architecture Summary

uHOME Lite =
	•	LibreELEC appliance
	•	Kodi front-end
	•	TVHeadend backend
	•	USB tuner ingestion
	•	NAS export
	•	External ad removal
	•	Controller-first
	•	Locked-down experience
	•	Flashable reproducible image

uHOME Full =
	•	NAS
	•	Processing engine
	•	Archive library
	•	Gaming system
	•	Heavy compute

Clean separation.
Clean product logic.

⸻
