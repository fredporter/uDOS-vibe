param(
    [string]$OfflineRoot = "C:\\mount"
)

. "$PSScriptRoot\\common.ps1"

Write-Section "Media Mode Policies"

$windowsConfig = Get-UdosWindowsEntertainmentConfig
if (-not $PSBoundParameters.ContainsKey('OfflineRoot') -and $null -ne $windowsConfig -and -not [string]::IsNullOrWhiteSpace($windowsConfig.offline_root)) {
    $OfflineRoot = $windowsConfig.offline_root
}

$registryHive = "$OfflineRoot\\Windows\\System32\\config\\SOFTWARE"

Invoke-PlanStep "Load offline registry hive" "reg load HKLM\\UDOS_SOFTWARE $registryHive"
Invoke-PlanStep "Disable action center" "reg add HKLM\\UDOS_SOFTWARE\\Policies\\Microsoft\\Windows\\Explorer /v DisableNotificationCenter /t REG_DWORD /d 1 /f"
Invoke-PlanStep "Disable lock screen" "reg add HKLM\\UDOS_SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization /v NoLockScreen /t REG_DWORD /d 1 /f"
Invoke-PlanStep "Disable Cortana" "reg add HKLM\\UDOS_SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search /v AllowCortana /t REG_DWORD /d 0 /f"
Invoke-PlanStep "Unload registry hive" "reg unload HKLM\\UDOS_SOFTWARE"
