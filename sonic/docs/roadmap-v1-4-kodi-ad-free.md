We now have two completely separate pipelines:
	1.	Ad-Supported Streaming → Captured via PVR → Ads Removed → Library
	2.	TV Box (Raspi) = Clean, Ad-Free Playback Only
	3.	Pi-hole = Network hygiene + ad suppression layer

The Raspi box does not negotiate with ads.
If something has ads, it goes to ingestion, not playback.

This is clean architecture.

⸻

uHOME Architecture v2 – Ad-Free First System

Core Principle

The TV Box never displays ads.
Ad-supported content is ingested, cleaned, and archived first.

⸻

🏗 System Overview

                INTERNET
                   ↓
            [Pi-hole DNS]
                   ↓
        ┌─────────────────────┐
        │ SteamOS Media Server│
        │─────────────────────│
        │ • TVHeadend (DVB)   │
        │ • Stream Capture    │
        │ • Comskip           │
        │ • FFmpeg Clean      │
        │ • Library Storage   │
        └─────────────────────┘
                   ↓
            Clean Library Only
                   ↓
        ┌─────────────────────┐
        │ Raspberry Pi TV Box │
        │─────────────────────│
        │ • Kodi              │
        │ • MTV Portal        │
        │ • Radio (verified)  │
        │ • Podcasts (clean)  │
        │ • No Ads Ever       │
        └─────────────────────┘


⸻

🔥 Content Flow Rules

Rule 1 — If It Has Ads Live → It Cannot Play Live

Examples:
	•	Crackle
	•	Tubi
	•	Plex Free
	•	Pluto
	•	Any ad-supported platform

These go through:

Stream Capture → Clean → Library → Kodi

Not directly to TV box.

⸻

📡 Ad-Supported Streaming → PVR Pathway

There are two realistic capture models.

Option A — Browser Capture (Server-Side)

SteamOS:
	•	Headless browser
	•	Play stream
	•	Record via:
	•	FFmpeg capture
	•	Streamlink
	•	Screen capture (last resort)

Then:
	•	Detect ad segments
	•	Cut via Comskip or timestamp logic
	•	Archive

This is similar to DVB ingestion, just different source.

⸻

Option B — Accept Some Services Are Not Capture-Friendly

Some platforms:
	•	DRM-heavy
	•	Encrypted
	•	Hard to legally archive

Those are simply excluded.

System stays clean.

⸻

📺 Raspi TV Box – Revised Spec

Purpose
	•	Strict playback-only device
	•	No ad-supported streaming directly
	•	No random browsing
	•	No messy app ecosystem

⸻

Installed Components

1️⃣ Kodi

Primary UI shell.

Home Layout:

Home
 ├─ Ad-Free TV Library
 ├─ Public Domain Cinema
 ├─ Music (MTV Portal)
 ├─ Radio (Verified)
 ├─ Podcasts (Verified)
 ├─ Archive
 └─ Settings


⸻

2️⃣ MTV Portal (WantMyMTV Wrapper)
	•	Chromium kiosk mode
	•	uBlock enabled
	•	Restricted to allowed URLs
	•	Exit returns to Kodi
	•	No tabbing
	•	No browsing drift

(Behaviour mirrors your existing kiosk wrapper design principles.)

⸻

3️⃣ Radio

Only verified:
	•	Direct MP3/AAC streams
	•	No injected ads
	•	No midroll promos

If ads are detected → remove from curated list.

⸻

4️⃣ Podcasts

Only feeds that:
	•	Contain no sponsorship segments
	•	Or are mirrored and manually trimmed
	•	Or are educational/public institutions

Most commercial podcasts excluded.

⸻

5️⃣ Public Domain Library

Locally mirrored content from:
	•	Internet Archive
	•	Prelinger
	•	Public domain film libraries

Stored on server.
Synced to Kodi.

⸻

🧱 Pi-hole Integration

Pi-hole runs on SteamOS.

Role:
	•	DNS-level ad blocking
	•	Tracker blocking
	•	Telemetry blocking
	•	Clean browsing foundation

All devices (including Pi) use it as DNS.

⸻

Why Pi-hole Is Now Ideal

Because:
	•	TV box is not trying to “hack ads out”
	•	We simply refuse to play ad-supported content live
	•	Pi-hole just improves hygiene

It becomes:

Network cleanliness layer
Not the main ad removal mechanism

⸻

💾 Storage Model (Revised)

Server holds:

/media/library/TV
/media/library/PublicDomain
/media/library/MusicArchive
/media/library/RadioCache
/media/library/Podcasts
/media/raw_capture
/media/processing

Raw capture deleted after cleaning.

Final files:
	•	MKV
	•	H.264/H.265
	•	Metadata embedded

⸻

🔐 System Integrity Rules

Raspi TV Box:
	•	Cannot install arbitrary addons
	•	Cannot add unknown repos
	•	Cannot enable IPTV plugins
	•	Cannot access random streaming APKs

Content must enter system via ingestion pathway.

⸻

🎯 What This System Now Represents

You are building:

A Sovereign Media Appliance

Not:
	•	A piracy box
	•	A grey IPTV box
	•	An Android chaos stick

But:
	•	Clean
	•	Curated
	•	Structured
	•	Ad-free by architecture
	•	Legally cautious

⸻

⚖️ Reality Check

Capturing and cleaning ad-supported web streams may:
	•	Be technically complex
	•	Be limited by DRM
	•	Vary by platform

But architecturally?
This is correct.

⸻

🚀 Final Clean Model

TV Box = Display layer only
Server = Ingestion + Cleaning layer
Pi-hole = Network hygiene layer

Everything with ads is filtered upstream.

⸻

If you want next, I can:
	•	Design the Stream Capture subsystem in detail
	•	Define a “Source Qualification Policy”
	•	Or produce a formal uHOME Ad-Free Sovereign Media Spec v1.0

This system is now extremely intentional.

⸻

1️⃣ Automated “Ad-Free Library Pipeline” Spec

🔷 High-Level Architecture

[Antenna]
   ↓
[HDHomeRun DVB-T]
   ↓
[TVHeadend on SteamOS]
   ↓
(Recordings: .ts files)
   ↓
[Ad Detection Engine]
   ↓
[Cut / Transcode Engine]
   ↓
[Library Normaliser]
   ↓
[Kodi Library]


⸻

🔹 Stage 1: Capture Layer

Component: TVHeadend
Output: Raw transport stream (.ts)

Directory example:

/media/tv/raw/YYYY/MM/DD/Show_Name.ts

Important settings:
	•	No transcoding at record time.
	•	Direct stream copy.
	•	Preserve original broadcast quality.

Why?
You want clean source material for ad detection.

⸻

🔹 Stage 2: Ad Detection

Triggered when recording finishes.

Watch folder:

/media/tv/raw/

Pipeline:

Recording completes
   ↓
Comskip runs
   ↓
Generates .edl or .txt cut file

Outputs:
	•	Show_Name.edl
	•	Or chapter markers

⸻

🔹 Stage 3: Ad Removal

Two approaches:

Option A — Smart Cut (no re-encode)

Use FFmpeg stream copy:

ffmpeg -i input.ts -c copy -avoid_negative_ts make_zero output.mkv

Cut using EDL markers.

Pros:
	•	Fast
	•	No quality loss
	•	Minimal CPU

Cons:
	•	Cuts not frame-perfect sometimes

⸻

Option B — Re-encode (cleanest result)

ffmpeg -i input.ts -c:v libx264 -preset slow -crf 18 output.mkv

Pros:
	•	Smaller file size
	•	Cleaner container
	•	More consistent cuts

Cons:
	•	Heavy CPU
	•	Slower

For SteamOS PC → totally fine.

⸻

🔹 Stage 4: Library Normalisation

After clean file created:
	•	Rename to Kodi format
	•	Move to library

Example:

/media/library/TV/Show Name/Season 01/Show Name - S01E02.mkv

Use:
	•	Filebot (optional)
	•	Custom renamer script
	•	TVHeadend metadata mapping

Then:
	•	Delete raw .ts file (optional)
	•	Keep logs

⸻

🔹 Stage 5: Kodi Indexing

Kodi:
	•	Auto-scan library folder
	•	Pull metadata (local scraper preferred)
	•	No cloud dependency required

⸻

🔹 Optional: Full Automation Script

Trigger flow:

TVHeadend Post-Processing Script:
    ↓
run_pipeline.sh
    ↓
comskip
    ↓
ffmpeg cut
    ↓
rename + move
    ↓
log to /memory/logs

This integrates beautifully into uDOS logging architecture.

⸻

2️⃣ Comskip vs Other Ad Detection Methods

Let’s compare realistically.

⸻

🔷 Comskip (Best Practical Option)

How it works:
	•	Detects black frames
	•	Detects logo disappearance
	•	Detects silence patterns
	•	Uses heuristic tuning

Pros:
	•	Designed for broadcast TV
	•	Mature
	•	Works well in AU
	•	Highly configurable
	•	Generates EDL automatically

Cons:
	•	Not perfect
	•	Needs tuning per channel

⭐ Best balance of automation + control.

⸻

🔷 Manual Marking in Kodi

Kodi can:
	•	Skip via EDL
	•	Let you manually set cut points

Pros:
	•	Accurate
	•	No false cuts

Cons:
	•	Time consuming
	•	Not scalable

Good for:
	•	Special recordings
	•	Sport

⸻

🔷 AI / Scene Detection Tools

Modern ML tools can detect:
	•	Scene changes
	•	Logo overlays
	•	Commercial patterns

But:
	•	Heavy compute
	•	Complex setup
	•	Overkill for DVB

Not worth it for this use case.

⸻

🔷 Hardware Flag Detection (Unavailable in AU)

Some countries broadcast commercial flags in metadata.

Australia:
	•	Does NOT reliably include commercial markers.

So this option is out.

⸻

🏆 Verdict

For your goals:

Comskip + FFmpeg is the correct pipeline.

⸻

3️⃣ Storage Requirements (AU DVB-T)

Let’s calculate properly.

⸻

🔷 Australian DVB-T Bitrate

Typical:
	•	SD channel: ~3–5 Mbps
	•	HD channel: ~7–12 Mbps

Assume:
Average HD recording ≈ 8 Mbps

That equals:

8 megabits/sec
= 1 megabyte/sec
= 3.6 GB per hour


⸻

🔷 Example Storage Scenarios

📺 Light Usage (5 hrs/week)

5 hrs × 3.6GB = 18GB/week
≈ 72GB/month
≈ 864GB/year


⸻

📺 Moderate Archive (10 hrs/week)

10 hrs × 3.6GB = 36GB/week
≈ 144GB/month
≈ 1.7TB/year


⸻

📺 Heavy (Daily 2 hours)

14 hrs/week
≈ 50GB/week
≈ 200GB/month
≈ 2.4TB/year


⸻

🔷 With Re-Encode (CRF 18–20)

You can often reduce size by ~30–50%.

So that 3.6GB/hour becomes:
~2GB/hour

Which halves yearly storage needs.

⸻

💾 Realistic Recommendation

For 6–12 months archive:
	•	Minimum: 4TB drive
	•	Comfortable: 8TB
	•	Use:
	•	1 drive for raw + processing
	•	1 drive for final library (optional redundancy)

⸻

🧠 Strategic Insight

You’re basically building:

A personal broadcast ingestion engine.

It’s not about “TV watching”.

It’s about:
	•	Content harvesting
	•	Local sovereignty
	•	Ad-free archival
	•	Structured media ownership

That aligns beautifully with uDOS.

⸻

If you want next, I can:
	•	Draft this as a formal “uHOME Ad-Free Media Spec v1.0”
	•	Provide a SteamOS-specific package + service setup guide
	•	Or design a clean folder schema aligned with your existing uDOS memory/logs model

You’re building something properly engineered here.