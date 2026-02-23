param(
    [switch]$Execute
)

. "$PSScriptRoot\\..\\scripts\\common.ps1" -Execute:$Execute

Write-Section "Diagnostics"
Require-Admin

Invoke-PlanStep "List BCD entries" "bcdedit /enum"
Invoke-PlanStep "List disks" "Get-Disk"
Invoke-PlanStep "List volumes" "Get-Volume"
Invoke-PlanStep "Check controller devices" "Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Xbox|Controller' }"
