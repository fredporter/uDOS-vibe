# uDOS Package Tiers - Installation Guide

**Date:** 20251213-160000UTC (December 13, 2025)  
**Location:** Package Distribution  
**Version:** v1.2.23

## Overview

uDOS offers 5 installation tiers to match your needs and constraints. Choose based on available storage, internet access, and required features.

---

## 📦 Installation Tiers

### 1. Ultra (~8MB) - Core Only

**Minimal installation with zero external dependencies.**

```bash
pip install udos[ultra]
```

**Includes:**
- ✅ Core system (8MB)
- ✅ Basic commands (STATUS, TREE, FILE, etc.)
- ✅ uPY scripting runtime
- ✅ Offline operation

**Excludes:**
- ❌ Knowledge base
- ❌ Extensions
- ❌ AI features

**Best For:**
- Embedded systems
- Extreme storage constraints
- Custom knowledge integration
- Development/testing

---

### 2. Lite (~16MB) - Core + Knowledge (DEFAULT)

**Complete offline survival system with 230+ guides.**

```bash
pip install udos
# or explicitly:
pip install udos[lite]
```

**Includes:**
- ✅ Core system (8MB)
- ✅ Knowledge base (8MB - 230+ survival guides)
  - Water purification (26 guides)
  - Fire starting (20 guides)
  - Shelter building (20 guides)
  - Food preservation (23 guides)
  - Navigation (20 guides)
  - Medical/first-aid (27 guides)
  - Tools, skills, reference (94 guides)
- ✅ All core commands
- ✅ Unified task management (v1.2.23)
- ✅ UNDO/REDO/BACKUP/RESTORE
- ✅ File organization (TIDY/CLEAN/ARCHIVE)

**Excludes:**
- ❌ Extensions (AI, graphics, gameplay)
- ❌ Font assets (11MB)
- ❌ Cloud features

**Best For:**
- ⭐ **Recommended for most users**
- Offline survival preparation
- Minimal bandwidth/storage
- Quick installation
- Embedded/portable systems

---

### 3. Standard (~28MB) - Core + Knowledge + AI

**Add AI-powered assistance to Lite tier.**

```bash
pip install udos[standard]
```

**Includes:**
- ✅ Everything in Lite tier (16MB)
- ✅ AI Assistant extension (12MB)
  - OK Assistant (O-key panel)
  - Gemini AI integration
  - MAKE commands (WORKFLOW/SVG/DOC/TEST/MISSION)
  - Context-aware help
- ✅ Google Generative AI library

**Requires:**
- 🔑 Gemini API key (optional, degrades gracefully)
- 🌐 Internet for AI features (offline mode available)

**Best For:**
- Content generation
- AI-assisted workflows
- Documentation automation
- Learning/exploration

---

### 4. Full (~58MB) - Complete System

**Everything including gameplay, graphics, and fonts.**

```bash
pip install udos[full]
```

**Includes:**
- ✅ Everything in Standard tier (28MB)
- ✅ Gameplay extensions (30MB)
  - XP/achievement system
  - Map engine with grid visualization
  - MeshCore mesh networking integration
  - SPRITE and MAP commands
- ✅ Graphics assets
  - Font library (11MB - 18 fonts)
  - ASCII art patterns
  - Teletext rendering
- ✅ Image processing (Pillow)

**Best For:**
- Complete uDOS experience
- Adventure/quest modes
- Custom graphics
- Mesh networking scenarios
- Training/education

---

### 5. Enterprise (~120MB+) - Cloud + Business Intelligence

**Full system plus cloud sharing and analytics.**

```bash
pip install udos[enterprise]
```

**Includes:**
- ✅ Everything in Full tier (58MB)
- ✅ Cloud extensions (62MB+)
  - Group management
  - Secure tunneling
  - Content sharing (POKE/SHARE)
  - BIZINTEL analytics
  - Entity resolution
  - Database integration (SQLAlchemy)
- ✅ Google Cloud APIs
- ✅ Fuzzy matching (fuzzywuzzy, Levenshtein)

**Requires:**
- 🔑 Google Cloud credentials
- 🌐 Internet connection
- 💾 Database setup (optional)

**Best For:**
- Team collaboration
- Business intelligence
- Data analytics
- Enterprise deployments
- Multi-user scenarios

---

## 🎯 Quick Comparison

| Feature | Ultra | Lite | Standard | Full | Enterprise |
|---------|-------|------|----------|------|------------|
| **Size** | 8MB | 16MB | 28MB | 58MB | 120MB+ |
| **Core System** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Knowledge (230+ guides)** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **OK Assistant (AI)** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Fonts/Graphics** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Gameplay/XP** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Cloud Sharing** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **BIZINTEL Analytics** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Offline Capable** | ✅ | ✅ | ✅* | ✅* | ✅* |
| **API Keys Required** | ❌ | ❌ | Optional | Optional | Yes |

\* AI/Cloud features require internet, but core functionality works offline

---

## 📥 Installation Examples

### Fresh Installation

```bash
# Lite tier (recommended)
pip install udos

# Specific tier
pip install udos[standard]
```

### Upgrade Existing Installation

```bash
# Upgrade to Standard from Lite
pip install --upgrade udos[standard]

# Upgrade to Full
pip install --upgrade udos[full]
```

### Multiple Tiers (for development)

```bash
# Install lite + dev tools
pip install udos[lite,dev]

# Install full + dev tools
pip install udos[full,dev]
```

### From Source

```bash
# Clone repository
git clone https://github.com/fredporter/uDOS-vibe.git
cd uDOS

# Install in development mode with tier
pip install -e .[lite]
```

---

## 🔧 Post-Installation

### Verify Installation

```bash
udos
uDOS> STATUS
uDOS> TREE --sizes
```

### Configure API Keys (Standard/Full/Enterprise only)

```bash
# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Test AI features
uDOS> OK ASK "what is uDOS?"
```

### Optional Extensions (Full/Enterprise)

```bash
# MeshCore (for mesh networking)
cd extensions/cloned/
git clone https://github.com/meshcore-dev/MeshCore.git meshcore

# Verify
uDOS> REPAIR
```

---

## 🎓 Migration from v1.2.22

If upgrading from v1.2.22, run migration scripts:

```bash
# Migrate tasks to unified system
python dev/tools/migrate_to_unified_tasks.py --dry-run
python dev/tools/migrate_to_unified_tasks.py

# Rename files to uDOS ID format
python dev/tools/rename_distributable_files.py --dry-run
python dev/tools/rename_distributable_files.py

# Verify structure
uDOS> CONFIG CHECK
uDOS> CONFIG FIX
```

---

## 💡 Recommendations

**For Most Users:** Start with **Lite** tier (16MB)
- Complete survival knowledge
- All core features
- Fastest installation
- Perfect for offline use

**For Content Creators:** Use **Standard** tier (28MB)
- AI-powered content generation
- Automated workflows
- Still lightweight

**For Full Experience:** Use **Full** tier (58MB)
- Complete feature set
- Graphics and gameplay
- Best for learning/training

**For Teams:** Use **Enterprise** tier (120MB+)
- Collaboration features
- Business intelligence
- Analytics and reporting

---

## 🐛 Troubleshooting

### Package Too Large?

```bash
# Check actual size
pip show udos | grep Location
du -sh <location>/udos

# Use smaller tier
pip uninstall udos
pip install udos[ultra]  # Minimal
```

### Missing Features?

```bash
# Check installed tier
pip show udos

# Upgrade tier
pip install --upgrade udos[full]
```

### Offline Installation?

```bash
# Download package on internet-connected machine
pip download udos[lite]

# Transfer .whl file to offline machine
pip install udos-1.2.23-*.whl
```

---

## 📊 Bandwidth Requirements

| Tier | Download Size | Unpacked Size | Installation Time* |
|------|--------------|---------------|-------------------|
| Ultra | ~8MB | ~15MB | 5-10s |
| Lite | ~16MB | ~30MB | 10-20s |
| Standard | ~28MB | ~50MB | 20-30s |
| Full | ~58MB | ~100MB | 40-60s |
| Enterprise | ~120MB | ~200MB | 90-120s |

\* Assuming 10Mbps connection

---

## 🔗 Additional Resources

- **Documentation:** https://github.com/fredporter/uDOS-vibe/wiki
- **Getting Started:** https://github.com/fredporter/uDOS-vibe/wiki/Getting-Started
- **Installation Guide:** https://github.com/fredporter/uDOS-vibe/wiki/Installation-Guide
- **Bug Reports:** https://github.com/fredporter/uDOS-vibe/issues
- **Discussions:** https://github.com/fredporter/uDOS-vibe/discussions

---

**Date:** 20251213-160000UTC  
**Version:** v1.2.23  
**Status:** Production Ready
