# Configure BCD entries for Media/Game mode switching
param(
    [string]$MediaIdentifier = "{media}",
    [string]$GameIdentifier = "{game}",
    [switch]$Execute
)

. "$PSScriptRoot\\common.ps1" -Execute:$Execute

Write-Section "Mode Switcher (BCD)"
Require-Admin
Require-Tool "bcdedit.exe"

$windowsConfig = Get-UdosWindowsEntertainmentConfig
if ($null -ne $windowsConfig -and $null -ne $windowsConfig.mode_switch) {
    $modeSwitch = $windowsConfig.mode_switch
    if (-not $PSBoundParameters.ContainsKey('MediaIdentifier') -and -not [string]::IsNullOrWhiteSpace($modeSwitch.media_identifier)) {
        $MediaIdentifier = $modeSwitch.media_identifier
    }
    if (-not $PSBoundParameters.ContainsKey('GameIdentifier') -and -not [string]::IsNullOrWhiteSpace($modeSwitch.game_identifier)) {
        $GameIdentifier = $modeSwitch.game_identifier
    }
    if (-not [string]::IsNullOrWhiteSpace($modeSwitch.media_partition)) {
        $mediaPartition = $modeSwitch.media_partition
    }
    else {
        $mediaPartition = "\\Device\\HarddiskVolume3"
    }
    if (-not [string]::IsNullOrWhiteSpace($modeSwitch.game_partition)) {
        $gamePartition = $modeSwitch.game_partition
    }
    else {
        $gamePartition = "\\Device\\HarddiskVolume4"
    }
    if ($modeSwitch.boot_timeout_seconds -gt 0) {
        $bootTimeoutSeconds = [int]$modeSwitch.boot_timeout_seconds
    }
    else {
        $bootTimeoutSeconds = 5
    }
}
else {
    $mediaPartition = "\\Device\\HarddiskVolume3"
    $gamePartition = "\\Device\\HarddiskVolume4"
    $bootTimeoutSeconds = 5
}

Invoke-PlanStep "Copy current Windows loader for Media mode" "bcdedit /copy {current} /d 'Windows Media Mode'"
Invoke-PlanStep "Copy current Windows loader for Game mode" "bcdedit /copy {current} /d 'Windows Game Mode'"
Invoke-PlanStep "Set media mode partition" "bcdedit /set $MediaIdentifier device partition=$mediaPartition"
Invoke-PlanStep "Set media mode osdevice" "bcdedit /set $MediaIdentifier osdevice partition=$mediaPartition"
Invoke-PlanStep "Set game mode partition" "bcdedit /set $GameIdentifier device partition=$gamePartition"
Invoke-PlanStep "Set game mode osdevice" "bcdedit /set $GameIdentifier osdevice partition=$gamePartition"
Invoke-PlanStep "Set boot menu timeout" "bcdedit /timeout $bootTimeoutSeconds"

Write-Host "\nUpdate the volume numbers to match your partition layout." -ForegroundColor Yellow
