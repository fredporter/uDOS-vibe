param(
    [string]$OfflineRoot = "C:\\mount"
)

. "$PSScriptRoot\\common.ps1"

Write-Section "Configure Game Launcher"

$windowsConfig = Get-UdosWindowsEntertainmentConfig
if (-not $PSBoundParameters.ContainsKey('OfflineRoot') -and $null -ne $windowsConfig -and -not [string]::IsNullOrWhiteSpace($windowsConfig.offline_root)) {
    $OfflineRoot = $windowsConfig.offline_root
}

if ($null -ne $windowsConfig -and -not [string]::IsNullOrWhiteSpace($windowsConfig.default_game_launcher_path)) {
    $launcherPath = $windowsConfig.default_game_launcher_path
}
else {
    $launcherPath = 'C:\\Program Files\\Playnite\\Playnite.FullscreenApp.exe'
}

$registryHive = "$OfflineRoot\\Windows\\System32\\config\\SOFTWARE"

Invoke-PlanStep "Load offline registry hive" "reg load HKLM\\UDOS_SOFTWARE $registryHive"
Invoke-PlanStep "Set Winlogon shell (Playnite preferred)" "reg add HKLM\\UDOS_SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon /v Shell /t REG_SZ /d '$launcherPath' /f"
Invoke-PlanStep "Unload registry hive" "reg unload HKLM\\UDOS_SOFTWARE"
