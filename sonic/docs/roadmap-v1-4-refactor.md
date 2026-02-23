# **uHOME Hybrid Console: Final Development Brief**
**Project Name**: uHOME Hybrid Console (SteamOS + Windows 10 Dual-Boot)
**Version**: 1.0 Final
**Date**: February 23, 2026
**Author**: Fred Porter / uDOS Team
**Status**: Approved for Development

---

## **1. Project Overview**
The **uHOME Hybrid Console** is a **dual-OS gaming and media appliance** designed to merge the strengths of **SteamOS (Linux)** for media and non-EAC gaming with **Windows 10** for Fortnite and anti-cheat titles. The system will feature an **integrated OS switcher** for seamless toggling between modes, deployed via **Sonic** for scalability.

### **Key Objectives**:
- **Dual-OS Experience**: SteamOS (primary) + Windows 10 (gaming).
- **Seamless Switching**: Reboot-based OS switcher with controller-friendly UI.
- **Fortnite Support**: Native Windows 10 for EAC compatibility.
- **Plex Integration**: SteamOS-hosted media server with Steam UI access.
- **Sonic Deployment**: Automated setup for consistency across units.

---

## **2. System Architecture**

### **A. Hardware Specifications**
| **Component**       | **Requirement**               | **Notes**                                  |
|----------------------|--------------------------------|--------------------------------------------|
| **CPU**              | AMD Ryzen 5 5600G              | Balanced performance/price; integrated GPU backup. |
| **GPU**              | AMD RX 6600                    | Avoid NVIDIA for GPU passthrough compatibility. |
| **RAM**              | 16GB DDR4 (3200MHz)            | Sufficient for gaming/media multitasking.  |
| **Storage**          | 1TB NVMe SSD                  | Split: 100GB Windows, 900GB SteamOS.       |
| **Case**             | Mini-ITX (e.g., Velka 3)      | Compact, console-like form factor.         |
| **Power Supply**     | 500W 80+ Gold                 | Efficient and quiet.                       |
| **Cooling**          | Low-profile CPU cooler        | Ensure quiet operation.                   |
| **Extras**           | OLED screen (optional)        | For OS switcher status notifications.     |

**Budget**: **$890–$1,150 AUD per unit** (see Appendix A for breakdown).

---

### **B. Software Stack**
| **Component**        | **Technology**                | **Purpose**                                  |
|----------------------|--------------------------------|---------------------------------------------|
| **Primary OS**       | SteamOS 3.0 (Arch-based)      | Media, non-EAC games, Plex Server.          |
| **Game Mode OS**     | Windows 10 (licensed)         | Fortnite and anti-cheat games.             |
| **Bootloader**       | GRUB2                         | Dual-boot manager with custom themes.       |
| **OS Switcher**      | Python/Bash scripts           | Reboot into Windows/SteamOS seamlessly.      |
| **Media Server**     | Plex Media Server             | Host and stream media.                     |
| **Game Launcher**    | Steam Big Picture Mode        | Console-like UI for games/media.           |
| **Deployment Tool**  | Sonic                         | Automate OS/installation across units.     |

---

## **3. Core Features**

### **A. SteamOS Mode (Media/Gaming)**
- **Auto-Login**: Boots directly into **Steam Big Picture Mode**.
- **Plex Server**:
  - Runs as a **background service** on SteamOS.
  - Accessible via Steam’s **web browser** or custom **Electron app**.
- **Non-EAC Games**: Native support via Steam/Proton.
- **uHOME Menu**:
  - Custom **Steam shortcut** to switch to **Game Mode (Windows)**.
  - Controller-friendly navigation.

### **B. Windows 10 Game Mode**
- **Auto-Login**: Directly into **Fortnite/Steam**.
- **Fortnite Optimization**:
  - Pre-configured **Epic Games Launcher** and **Fortnite settings** (1080p, controller bindings).
  - **Return to SteamOS** shortcut on desktop.
- **Anti-Cheat Compatibility**: Native Windows 10 for EAC/BattlEye titles.

### **C. OS Switcher/Rebooter**
- **SteamOS → Windows**:
  - **Python script** (`switch_to_windows.py`) triggered via Steam shortcut.
  - Displays **"Switching to Game Mode..."** notification (OLED/on-screen).
  - Reboots into Windows using GRUB:
    ```python
    os.system("sudo grub-reboot 4 && sudo reboot")  # Adjust "4" to Windows GRUB entry
    ```
- **Windows → SteamOS**:
  - **Batch script** (`switch_to_steamos.bat`) on the Windows desktop:
    ```batch
    bcdedit /set {bootmgr} path \EFI\ubuntu\grubx64.efi
    shutdown /r /t 0
    ```
- **GRUB Customization**:
  - **GRUB Customizer** for a polished boot menu with:
    - **"uHOME Media Mode (SteamOS)"**
    - **"uHOME Game Mode (Windows)"**

### **D. Sonic Deployment**
- **Automated Installation**:
  - Sonic deploys **both OSes**, partitions, and scripts.
  - Includes **Plex Server**, Steam, and OS switcher scripts.
- **Post-Install Configuration**:
  - Auto-login for both OSes.
  - GRUB defaults to SteamOS.

---

## **4. Development Phases**

| **Phase**               | **Tasks**                                                                 | **Timeframe** | **Dependencies**          |
|-------------------------|---------------------------------------------------------------------------|---------------|----------------------------|
| **1. Hardware Procurement** | Finalize and order components.                                          | 1–2 weeks     | Budget approval            |
| **2. OS Setup**         | Install Windows 10 + SteamOS; configure GRUB.                            | 3–5 days      | Hardware ready             |
| **3. OS Switcher**      | Develop and test `switch_to_windows.py` and `switch_to_steamos.bat`.     | 2–3 days      | OS setup complete          |
| **4. Plex Integration** | Install Plex; integrate with Steam.                                     | 1–2 days      | SteamOS installed          |
| **5. Sonic Deployment** | Create Sonic profile for dual-OS setup.                                  | 3–5 days      | All scripts tested         |
| **6. UI/UX Polish**     | Custom GRUB theme; test controller navigation.                          | 2–3 days      | Functional prototype      |
| **7. Testing & QA**     | Functional, user, and stress testing.                                   | 1 week        | All phases complete        |

**Total Timeline**: **4–6 weeks**.

---

## **5. Technical Specifications**

### **A. OS Switcher Scripts**
#### **SteamOS → Windows (`switch_to_windows.py`)**
```python
#!/usr/bin/env python3
import os
import time

print("Switching to uHOME Game Mode (Windows)...")
time.sleep(3)  # Display message for 3 seconds
os.system("sudo grub-reboot 4 && sudo reboot")  # Replace "4" with Windows GRUB entry
```

#### **Windows → SteamOS (`switch_to_steamos.bat`)**
```batch
@echo off
echo Switching to uHOME Media Mode (SteamOS)...
bcdedit /set {bootmgr} path \EFI\ubuntu\grubx64.efi
shutdown /r /t 0
```

### **B. GRUB Customization**
1. Install GRUB Customizer:
   ```bash
   sudo add-apt-repository ppa:danielrichter2007/grub-customizer
   sudo apt update
   sudo apt install grub-customizer
   ```
2. Rename entries to:
   - **"uHOME Media Mode (SteamOS)"**
   - **"uHOME Game Mode (Windows)"**

### **C. Fortnite Pre-Configuration (Windows)**
- **Resolution**: 1080p (adjustable via Sonic).
- **Controller Bindings**: Pre-set for Xbox/PlayStation gamepads.
- **Epic Games Launcher**: Auto-login (if possible) or guest mode.

### **D. Plex Server (SteamOS)**
- **Installation**:
  ```bash
  curl https://downloads.plex.tv/plex-keys/PlexSign.key | sudo apt-key add -
  echo "deb https://downloads.plex.tv/repo/deb public main" | sudo tee /etc/apt/sources.list.d/plexmediaserver.list
  sudo apt update
  sudo apt install plexmediaserver
  ```
- **Steam Integration**:
  - Add Plex as a **non-Steam shortcut** in Steam (via browser or Electron app).

---

## **6. Sonic Deployment Package**
### **Included Components**:
1. **Dual-OS Installer**:
   - Partitions disk (100GB Windows, 900GB SteamOS).
   - Installs Windows 10 + SteamOS.
2. **Auto-Login Configuration**:
   - SteamOS: Auto-login to Steam Big Picture.
   - Windows: Auto-login to Fortnite/Steam.
3. **OS Switcher Scripts**:
   - `switch_to_windows.py` and `switch_to_steamos.bat`.
4. **Plex Server**:
   - Pre-configured for uHOME media libraries.
5. **GRUB Customization**:
   - uHOME-themed boot menu.
6. **Fortnite Settings**:
   - Pre-configured resolution/controller bindings.

### **Deployment Steps**:
1. **Boot Sonic USB** on target machine.
2. **Select "uHOME Hybrid Console"** profile.
3. **Automated Installation**:
   - Partitions disk.
   - Installs OSes, scripts, and Plex.
4. **Reboot** into SteamOS (default).

---

## **7. UI/UX Design**

### **A. Console Menu (SteamOS)**
- **Main Screen**:
  - **"Media"** (Plex, non-EAC games).
  - **"Switch to Game Mode"** (triggers `switch_to_windows.py`).
  - **"Settings"** (network, display, Plex config).
- **Controller Navigation**:
  - **A Button**: Select.
  - **B Button**: Back.
  - **D-Pad**: Navigate menus.

### **B. Game Mode (Windows)**
- **Main Screen**:
  - **"Fortnite"** (auto-launch).
  - **"Steam Games"** (non-EAC titles).
  - **"Return to Media Mode"** (triggers `switch_to_steamos.bat`).
- **Controller Navigation**: Mirror SteamOS layout.

### **C. Boot Menu (GRUB)**
- **Theme**: uHOME branding (dark background, green/white accents).
- **Entries**:
  1. **uHOME Media Mode (SteamOS)** [Default]
  2. **uHOME Game Mode (Windows)**
  3. **Advanced Options**

---

## **8. Testing Plan**

### **A. Functional Testing**
| **Test**                     | **Criteria**                                  | **Pass/Fail** |
|------------------------------|-----------------------------------------------|---------------|
| OS Switcher (SteamOS→Windows)| Reboots into Windows in <1 minute.          |               |
| OS Switcher (Windows→SteamOS)| Reboots into SteamOS in <1 minute.           |               |
| Fortnite Launch             | Loads in <30 seconds; no EAC errors.         |               |
| Plex Streaming              | 1080p/4K playback without buffering.          |               |
| Controller Navigation       | All menus accessible via gamepad.            |               |

### **B. User Testing**
- **Participants**: 5–10 uDOS team members.
- **Tasks**:
  1. Switch between OSes using the menu.
  2. Launch Fortnite and play a match.
  3. Stream media via Plex.
- **Feedback**: Rate ease of use (1–5) and note any confusion.

### **C. Stress Testing**
- **Plex + Gaming**: Transcode 4K media while gaming.
- **Reboot Cycles**: 50+ OS switches to test reliability.

---

## **9. Risks and Mitigations**

| **Risk**                          | **Mitigation**                                  |
|-----------------------------------|------------------------------------------------|
| GRUB misconfiguration             | Backup MBR; test on VM first.                  |
| Windows EAC blocks Fortnite      | Use licensed Windows 10; avoid modding.       |
| Plex transcoding performance      | Use NVMe SSD; allocate 8GB RAM to Plex.        |
| Sonic deployment failures         | Test on identical hardware; log errors.        |
| Controller input issues          | Test with Xbox/PlayStation controllers.       |
| GPU passthrough complexity        | Start with reboot-based switching.            |

---

## **10. Success Metrics**
- **Functional**:
  - OS switcher works **100% of the time** without manual intervention.
  - Fortnite launches in **<30 seconds** after switching to Windows.
  - Plex streams **1080p/4K** without buffering.
- **User Experience**:
  - Users can navigate **entirely via controller**.
  - OS switch takes **<1 minute** (including reboot).
- **Deployment**:
  - Sonic deploys **error-free** to **90% of test units**.

---

## **11. Appendices**

### **A. Budget Breakdown**
| **Item**               | **Estimated Cost (AUD)** | **Notes**                     |
|------------------------|--------------------------|--------------------------------|
| Mini-ITX Case          | $100–$150               | Velka 3 or similar.           |
| AMD Ryzen 5 5600G      | $200–$250               | Integrated GPU backup.         |
| AMD RX 6600            | $300–$350               | GPU passthrough compatibility.|
| 16GB DDR4 RAM          | $80–$100                | 3200MHz CL16.                 |
| 1TB NVMe SSD           | $100–$150               | Samsung 980 or similar.       |
| 500W 80+ Gold PSU      | $80–$100                | Efficient and quiet.          |
| OLED Screen (optional) | $30–$50                 | For switcher notifications.   |
| **Total**             | **$890–$1,150**         | Per unit.                     |

### **B. GRUB Customizer Guide**
1. Install GRUB Customizer:
   ```bash
   sudo add-apt-repository ppa:danielrichter2007/grub-customizer
   sudo apt update
   sudo apt install grub-customizer
   ```
2. Rename entries to:
   - **"uHOME Media Mode (SteamOS)"**
   - **"uHOME Game Mode (Windows)"**
3. Set default to SteamOS and save.

### **C. Fortnite Pre-Configuration (Sonic)**
- **Resolution**: 1080p.
- **Controller Bindings**: Xbox/PlayStation layouts.
- **Epic Games Launcher**: Auto-login (if possible) or guest mode.

### **D. Plex Server Setup**
- **Libraries**: Pre-configured for `/media/uhome` (movies, TV, music).
- **Transcoding**: Enable hardware acceleration (AMD GPU).

---

## **12. Open Questions (Resolved)**
| **Question**                          | **Decision**                                  |
|---------------------------------------|-----------------------------------------------|
| Force reboot or GPU passthrough?     | **Reboot-based switching** for simplicity.   |
| Plex embedded in Steam or separate?   | **Embed via Steam browser** for consistency. |
| Sonic pre-configures Fortnite?        | **Yes** (resolution/controller bindings).    |

---
