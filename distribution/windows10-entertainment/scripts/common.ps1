# Shared helpers for Windows 10 Entertainment Stack scripts
# These scripts are non-destructive by default. Use -Execute to run commands.

param(
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'

function Invoke-PlanStep {
    param(
        [string]$Title,
        [string]$Command
    )

    Write-Host "[PLAN] $Title" -ForegroundColor Cyan
    Write-Host "       $Command" -ForegroundColor DarkGray

    if ($Execute) {
        Write-Host "[RUN ] $Command" -ForegroundColor Yellow
        Invoke-Expression $Command
    }
}

function Require-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        throw "Run this script as Administrator."
    }
}

function Require-Tool {
    param([string]$Tool)
    if (-not (Get-Command $Tool -ErrorAction SilentlyContinue)) {
        throw "Required tool not found: $Tool"
    }
}

function Write-Section {
    param([string]$Title)
    Write-Host "\n==== $Title ====" -ForegroundColor Green
}

function Get-UdosRepoRoot {
    $candidate = Resolve-Path (Join-Path $PSScriptRoot "..\\..\\..")
    return $candidate.Path
}

function Get-UdosPackagingManifest {
    $repoRoot = Get-UdosRepoRoot
    try {
        $json = & uv run python -m core.services.packaging_adapters.cli windows entertainment-config --repo-root $repoRoot
        if (-not $json) { return $null }
        return $json | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-UdosWindowsEntertainmentConfig {
    return Get-UdosPackagingManifest
}

function Get-UdosShellPath {
    param(
        [ValidateSet('kodi','playnite','steam','custom')]
        [string]$ShellMode
    )

    $repoRoot = Get-UdosRepoRoot
    try {
        $resolved = & uv run python -m core.services.packaging_adapters.cli windows shell-path --repo-root $repoRoot --mode $ShellMode
        if (-not [string]::IsNullOrWhiteSpace($resolved)) {
            return $resolved
        }
    } catch {
        throw "Failed to resolve shell path from packaging adapter manifest: $($_.Exception.Message)"
    }
    throw "Empty shell path returned for mode '$ShellMode'"
}
