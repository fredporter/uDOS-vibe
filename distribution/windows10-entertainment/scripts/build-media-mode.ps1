# Windows 10 Media Mode image builder (LTSC preferred)
# Non-destructive plan by default. Use -Execute to run commands.

param(
    [string]$IsoPath = "C:\\isos\\windows10-ltsc.iso",
    [string]$WorkingDir = "C:\\udos\\media-mode",
    [string]$OutputImage = "C:\\udos\\images\\windows-media.wim",
    [ValidateSet('kodi','playnite','steam','custom')]
    [string]$ShellMode = "kodi",
    [switch]$Execute
)

. "$PSScriptRoot\\common.ps1" -Execute:$Execute

Write-Section "Media Mode Build Plan"
Require-Admin
Require-Tool "dism.exe"

Invoke-PlanStep "Create working directories" "New-Item -ItemType Directory -Force -Path $WorkingDir, (Split-Path $OutputImage)"
Invoke-PlanStep "Mount Windows ISO" "Mount-DiskImage -ImagePath $IsoPath"
Invoke-PlanStep "Apply Windows image (LTSC)" "dism /Apply-Image /ImageFile:D:\\sources\\install.wim /Index:1 /ApplyDir:$WorkingDir\\mount"
Invoke-PlanStep "Inject drivers (optional)" "dism /Image:$WorkingDir\\mount /Add-Driver /Driver:$WorkingDir\\drivers /Recurse"
Invoke-PlanStep "Disable telemetry services" "dism /Image:$WorkingDir\\mount /Disable-Feature /FeatureName:Windows-Feedback-Service"
Invoke-PlanStep "Set shell replacement (Kodi preferred)" "PowerShell -ExecutionPolicy Bypass -File $PSScriptRoot\\install-media-shell.ps1 -ShellMode $ShellMode -OfflineRoot $WorkingDir\\mount"
Invoke-PlanStep "Harden media mode policies" "PowerShell -ExecutionPolicy Bypass -File $PSScriptRoot\\media-policies.ps1 -OfflineRoot $WorkingDir\\mount"
Invoke-PlanStep "Capture image" "dism /Capture-Image /ImageFile:$OutputImage /CaptureDir:$WorkingDir\\mount /Name:'Windows Media Mode'"
Invoke-PlanStep "Unmount ISO" "Dismount-DiskImage -ImagePath $IsoPath"

Write-Host "\nMedia Mode build plan complete. Re-run with -Execute to apply." -ForegroundColor Green
