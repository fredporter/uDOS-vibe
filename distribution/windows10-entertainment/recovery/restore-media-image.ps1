param(
    [string]$ImagePath = "C:\\udos\\images\\windows-media.wim",
    [string]$Target = "D:",
    [switch]$Execute
)

. "$PSScriptRoot\\..\\scripts\\common.ps1" -Execute:$Execute

Write-Section "Restore Media Mode Image"
Require-Admin
Require-Tool "dism.exe"

Invoke-PlanStep "Apply image to WINDOWS_MEDIA" "dism /Apply-Image /ImageFile:$ImagePath /Index:1 /ApplyDir:$Target"
