<#
.SYNOPSIS
    BrowserGuard for Wazuh — AUTOMATIC (Silent) Windows Installer
    Author  : Ram Kumar G (IT Fortress)
    Version : 1.0.0 (Phase 3 — Privacy-Safe Telemetry Edition)

.DESCRIPTION
    Unattended deployment for Intune, SCCM, Ninja, Action1, PDQ, and any
    RMM/MDM workflow. Always installs with a fixed 30-minute scan interval
    and NEVER prompts.

    For INTERACTIVE installs, use:
        installers\windows-installer.ps1
        install.ps1

.ONE-LINE SILENT INSTALL (Admin PowerShell):
    powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; iwr -UseBasicParsing 'https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main/installers/automatic/install-windows.ps1' | iex"

.OVERRIDE THE 30m DEFAULT (optional):
    $env:BPM_INTERVAL = '2h'
    .\install-windows.ps1
#>

#Requires -RunAsAdministrator
param(
    [string]$Interval = "",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# Hard-defaults — no prompts, ever.
if (-not $env:BPM_INTERVAL)        { $env:BPM_INTERVAL        = "30m" }
if (-not $env:BPM_NONINTERACTIVE)  { $env:BPM_NONINTERACTIVE  = "1"   }

# A -Interval passed on the command line wins over the env default above.
if (-not [string]::IsNullOrWhiteSpace($Interval)) { $env:BPM_INTERVAL = $Interval }

Write-Host ""
Write-Host "[AUTO] BrowserGuard for Wazuh — Silent Windows Installer" -ForegroundColor Cyan
Write-Host "       Interval : $($env:BPM_INTERVAL)  (non-interactive)" -ForegroundColor Cyan
Write-Host ""

$RepoRaw    = "https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main"
$SelfDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$Standalone = Join-Path (Split-Path -Parent $SelfDir) "windows-installer.ps1"

# Prefer the colocated standalone installer; fall back to the one-line
# installer fetched from GitHub.
if (Test-Path $Standalone) {
    Write-Host "[+] Running local installer: $Standalone" -ForegroundColor Yellow
    $argsHash = @{
        Interval       = $env:BPM_INTERVAL
        NonInteractive = $true
    }
    if ($Uninstall) { $argsHash['Uninstall'] = $true }
    & $Standalone @argsHash
    exit $LASTEXITCODE
}

Write-Host "[+] Fetching installer from GitHub..." -ForegroundColor Yellow
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$tmp = Join-Path $env:TEMP ("bpm-install-{0}.ps1" -f ([guid]::NewGuid().ToString("N").Substring(0,8)))
Invoke-WebRequest -UseBasicParsing "$RepoRaw/install.ps1" -OutFile $tmp

try {
    $psArgs = @('-ExecutionPolicy','Bypass','-File',$tmp,'-Interval',$env:BPM_INTERVAL,'-NonInteractive')
    if ($Uninstall) { $psArgs += '-Uninstall' }
    & powershell.exe @psArgs
    exit $LASTEXITCODE
} finally {
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
