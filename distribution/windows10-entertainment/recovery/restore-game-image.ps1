param(
    [string]$ImagePath = "C:\\udos\\images\\windows-game.wim",
    [string]$Target = "E:",
    [switch]$Execute
)

. "$PSScriptRoot\\..\\scripts\\common.ps1" -Execute:$Execute

Write-Section "Restore Game Mode Image"
Require-Admin
Require-Tool "dism.exe"

Invoke-PlanStep "Apply image to WINDOWS_GAMES" "dism /Apply-Image /ImageFile:$ImagePath /Index:1 /ApplyDir:$Target"
