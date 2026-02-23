# Windows 10 Game Mode image builder
# Non-destructive plan by default. Use -Execute to run commands.

param(
    [string]$IsoPath = "C:\\isos\\windows10-ltsc.iso",
    [string]$WorkingDir = "C:\\udos\\game-mode",
    [string]$OutputImage = "C:\\udos\\images\\windows-game.wim",
    [switch]$Execute
)

. "$PSScriptRoot\\common.ps1" -Execute:$Execute

Write-Section "Game Mode Build Plan"
Require-Admin
Require-Tool "dism.exe"

Invoke-PlanStep "Create working directories" "New-Item -ItemType Directory -Force -Path $WorkingDir, (Split-Path $OutputImage)"
Invoke-PlanStep "Mount Windows ISO" "Mount-DiskImage -ImagePath $IsoPath"
Invoke-PlanStep "Apply Windows image" "dism /Apply-Image /ImageFile:D:\\sources\\install.wim /Index:1 /ApplyDir:$WorkingDir\\mount"
Invoke-PlanStep "Inject GPU drivers" "dism /Image:$WorkingDir\\mount /Add-Driver /Driver:$WorkingDir\\drivers /Recurse"
Invoke-PlanStep "Enable gaming features" "dism /Image:$WorkingDir\\mount /Enable-Feature /FeatureName:DirectPlay"
Invoke-PlanStep "Configure launcher (Playnite preferred)" "PowerShell -ExecutionPolicy Bypass -File $PSScriptRoot\\install-game-launcher.ps1 -OfflineRoot $WorkingDir\\mount"
Invoke-PlanStep "Capture image" "dism /Capture-Image /ImageFile:$OutputImage /CaptureDir:$WorkingDir\\mount /Name:'Windows Game Mode'"
Invoke-PlanStep "Unmount ISO" "Dismount-DiskImage -ImagePath $IsoPath"

Write-Host "\nGame Mode build plan complete. Re-run with -Execute to apply." -ForegroundColor Green
