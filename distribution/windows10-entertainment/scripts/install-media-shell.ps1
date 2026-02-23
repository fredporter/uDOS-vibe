param(
    [ValidateSet('kodi','playnite','steam','custom')]
    [string]$ShellMode = 'kodi',
    [string]$OfflineRoot = "C:\\mount"
)

. "$PSScriptRoot\\common.ps1"

Write-Section "Configure Media Shell"

$windowsConfig = Get-UdosWindowsEntertainmentConfig
if (-not $PSBoundParameters.ContainsKey('OfflineRoot') -and $null -ne $windowsConfig -and -not [string]::IsNullOrWhiteSpace($windowsConfig.offline_root)) {
    $OfflineRoot = $windowsConfig.offline_root
}

$registryHive = "$OfflineRoot\\Windows\\System32\\config\\SOFTWARE"

Invoke-PlanStep "Load offline registry hive" "reg load HKLM\\UDOS_SOFTWARE $registryHive"
$shellPath = Get-UdosShellPath -ShellMode $ShellMode

Invoke-PlanStep "Set Winlogon shell" "reg add HKLM\\UDOS_SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon /v Shell /t REG_SZ /d '$shellPath' /f"
Invoke-PlanStep "Hide desktop notifications" "reg add HKLM\\UDOS_SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings /v NOC_GLOBAL_SETTING_ALLOW_NOTIFICATION_SOUND /t REG_DWORD /d 0 /f"
Invoke-PlanStep "Unload registry hive" "reg unload HKLM\\UDOS_SOFTWARE"
