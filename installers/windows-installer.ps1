<#
.SYNOPSIS
    Wazuh Browser Privacy Monitor Phase 3 - Windows Standalone Installer
    Author  : Ram Kumar G (IT Fortress)
    Version : 1.0.0 (Phase 3 - Privacy-Safe Telemetry Edition)

.DESCRIPTION
    Standalone installer for use from a cloned repo.
    Installs collector, registers Task Scheduler job (SYSTEM),
    writes config with selected interval, configures Wazuh ossec.conf.

.USAGE
    Set-ExecutionPolicy Bypass -Scope Process -Force
    .\installers\windows-installer.ps1
    .\installers\windows-installer.ps1 -Interval 300
    .\installers\windows-installer.ps1 -Uninstall
#>
param(
    [int]$Interval = 0,
    [switch]$Uninstall
)

#Requires -RunAsAdministrator
$ErrorActionPreference = "Stop"

$InstallDir  = "C:\BrowserPrivacyMonitor"
$ScriptName  = "browser-privacy-monitor.py"
$ConfigName  = ".browser_privacy_config.json"
$TaskName    = "BrowserPrivacyMonitor"
$LogFile     = "$InstallDir\browser_privacy.log"
$WazuhConf   = "C:\Program Files (x86)\ossec-agent\ossec.conf"
$WazuhSvc    = "WazuhSvc"
$DestScript  = "$InstallDir\$ScriptName"
$DestConfig  = "$InstallDir\$ConfigName"
$Marker      = "<!-- BROWSER_PRIVACY_MONITOR_P3 -->"
$Utf8NoBom   = New-Object System.Text.UTF8Encoding $false
$RepoRaw     = "https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main"
$LocalScript = Join-Path (Split-Path $PSScriptRoot -Parent) "collector\$ScriptName"

if ($Uninstall) {
    Write-Host "[UNINSTALL] Removing..." -ForegroundColor Yellow
    try { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}
    $Lnk = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\WazuhBrowserPrivacyMonitor.lnk"
    if (Test-Path $Lnk) { Remove-Item $Lnk -Force }
    if (Test-Path $InstallDir) { Remove-Item -Path $InstallDir -Recurse -Force }
    Write-Host "[OK] Uninstalled." -ForegroundColor Green; exit 0
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Wazuh Browser Privacy Monitor Phase 3 - Windows Installer       ║" -ForegroundColor Cyan
Write-Host "║  Version 1.0.0 | Privacy-Safe Telemetry | IT Fortress            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Design: Raw URLs stay on endpoint — Wazuh only receives redacted JSON" -ForegroundColor Cyan
Write-Host ""

# Step 1: Python
Write-Host "[1] Detecting Python..." -ForegroundColor Yellow
$PythonExe = $null
foreach ($p in @(
    "C:\Program Files\Python314\python.exe","C:\Program Files\Python313\python.exe",
    "C:\Program Files\Python312\python.exe","C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe","C:\Program Files\Python39\python.exe",
    "C:\Python314\python.exe","C:\Python313\python.exe","C:\Python312\python.exe"
)) { if (Test-Path $p) { $PythonExe = $p; break } }
if (-not $PythonExe) {
    $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notlike "*\Users\*") { $PythonExe = $cmd.Source }
}
if (-not $PythonExe) { Write-Host "[-] Python not found. Install from https://python.org" -ForegroundColor Red; exit 1 }
$PyDir      = Split-Path $PythonExe -Parent
$PythonWExe = Join-Path $PyDir "pythonw.exe"
if (-not (Test-Path $PythonWExe)) { $PythonWExe = $PythonExe }
Write-Host "    [+] $PythonWExe" -ForegroundColor Green

# Step 2: Interval
if ($Interval -gt 0) {
    $SECS = $Interval; $LABEL = "${Interval}s"; $MINS = [Math]::Max(1, [int]($Interval / 60))
    Write-Host "[2] CLI interval: ${SECS}s" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[2] Select scan interval:" -ForegroundColor Yellow
    Write-Host "     1)  1  minute   (testing only)" -ForegroundColor Gray
    Write-Host "     2)  5  minutes" -ForegroundColor Gray
    Write-Host "     3)  10 minutes" -ForegroundColor Gray
    Write-Host "     4)  20 minutes" -ForegroundColor Gray
    Write-Host "     5)  30 minutes  (recommended)" -ForegroundColor Cyan
    Write-Host "     6)  60 minutes" -ForegroundColor Gray
    Write-Host "     7)  2  hours" -ForegroundColor Gray
    Write-Host "     8)  6  hours" -ForegroundColor Gray
    Write-Host "     9)  12 hours" -ForegroundColor Gray
    Write-Host "    10)  24 hours" -ForegroundColor Gray
    Write-Host ""
    $ch = Read-Host "    Enter choice [1-10] (default: 5)"
    if ([string]::IsNullOrWhiteSpace($ch)) { $ch = "5" }
    $map = @{"1"=@{S=60;L="1m";M=1};"2"=@{S=300;L="5m";M=5};"3"=@{S=600;L="10m";M=10};
             "4"=@{S=1200;L="20m";M=20};"5"=@{S=1800;L="30m";M=30};"6"=@{S=3600;L="60m";M=60};
             "7"=@{S=7200;L="2h";M=120};"8"=@{S=21600;L="6h";M=360};"9"=@{S=43200;L="12h";M=720};
             "10"=@{S=86400;L="24h";M=1440}}
    if (-not $map.ContainsKey($ch)) { $ch = "5" }
    $SECS = $map[$ch].S; $LABEL = $map[$ch].L; $MINS = $map[$ch].M
    Write-Host "    [+] Selected: $LABEL ($SECS seconds)" -ForegroundColor Green
}
$RepeatMins = if ($MINS -ge 1440) { 1440 } else { $MINS }

# Step 3: Dir
Write-Host ""
Write-Host "[3] Creating $InstallDir..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
$Acl = Get-Acl $InstallDir
$Acl.SetAccessRuleProtection($true, $false)
$Acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule("SYSTEM","FullControl","ContainerInherit,ObjectInherit","None","Allow")))
$Acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule("Administrators","FullControl","ContainerInherit,ObjectInherit","None","Allow")))
Set-Acl $InstallDir $Acl
Write-Host "    [+] Created (SYSTEM + Admins only)" -ForegroundColor Green

# Step 4: Collector
Write-Host ""
Write-Host "[4] Installing collector..." -ForegroundColor Yellow
if (Test-Path $LocalScript) {
    Copy-Item $LocalScript $DestScript -Force
    Write-Host "    [+] Installed from local copy" -ForegroundColor Green
} else {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -UseBasicParsing "$RepoRaw/collector/$ScriptName" -OutFile $DestScript
    Write-Host "    [+] Downloaded from GitHub" -ForegroundColor Green
}

# Step 5: Config
Write-Host ""
Write-Host "[5] Writing config (BOM-free UTF-8)..." -ForegroundColor Yellow
[System.IO.File]::WriteAllText($DestConfig,
    "{`"scan_interval_seconds`": $SECS, `"scan_interval_label`": `"$LABEL`", `"version`": `"1.0.0`"}",
    $Utf8NoBom)
Write-Host "    [+] $DestConfig  [$LABEL = $SECS s]" -ForegroundColor Green

# Step 6: Kill old
Get-Process -Name python*,pythonw* -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)" -EA SilentlyContinue).CommandLine
    if ($cmd -like "*browser-privacy-monitor*") { Stop-Process -Id $_.Id -Force -EA SilentlyContinue }
}

# Step 7: Task Scheduler
Write-Host ""
Write-Host "[7] Creating Scheduled Task (SYSTEM, AtStartup + repeat every $RepeatMins min)..." -ForegroundColor Yellow
$Action    = New-ScheduledTaskAction -Execute $PythonWExe -Argument "`"$DestScript`"" -WorkingDirectory $InstallDir
$Trigger   = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
$Settings  = New-ScheduledTaskSettingsSet -Hidden -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartInterval (New-TimeSpan -Minutes ([Math]::Max(1,$RepeatMins))) `
    -RestartCount 9999 -MultipleInstances IgnoreNew
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal | Out-Null
Set-ScheduledTask -TaskName $TaskName -Settings $Settings | Out-Null
Write-Host "    [+] Task registered" -ForegroundColor Green

# Step 8: Startup shortcut
$Lnk = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\WazuhBrowserPrivacyMonitor.lnk"
$WS = New-Object -ComObject WScript.Shell
$SC = $WS.CreateShortcut($Lnk)
$SC.TargetPath=$PythonWExe; $SC.Arguments="`"$DestScript`""; $SC.WorkingDirectory=$InstallDir; $SC.Save()

# Step 9: Wazuh conf
Write-Host ""
Write-Host "[9] Configuring Wazuh ossec.conf..." -ForegroundColor Yellow
if (Test-Path $WazuhConf) {
    $Content = Get-Content $WazuhConf -Raw
    if ($Content -notmatch [regex]::Escape($Marker)) {
        $Block = "`n  $Marker`n  <localfile>`n    <log_format>json</log_format>`n    <location>$LogFile</location>`n    <label key=`"integration`">browser-privacy-monitor</label>`n  </localfile>"
        [System.IO.File]::WriteAllText($WazuhConf, ($Content -replace "</ossec_config>","$Block`n</ossec_config>"), $Utf8NoBom)
        try { Restart-Service $WazuhSvc -EA SilentlyContinue } catch {}
        Write-Host "    [+] localfile added (log_format=json)" -ForegroundColor Green
    } else { Write-Host "    [=] Already configured" -ForegroundColor Gray }
} else { Write-Host "    [!] ossec.conf not found at $WazuhConf" -ForegroundColor Yellow }

# Step 10: Start
Start-ScheduledTask -TaskName $TaskName -EA SilentlyContinue; Start-Sleep -Seconds 2

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  [SUCCESS] Phase 3 Installation Complete!                        ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Interval  : $LABEL ($SECS seconds)"
Write-Host "  Log file  : $LogFile  [JSON — NO raw URLs]"
Write-Host "  Watch     : Get-Content '$LogFile' -Tail 20 -Wait" -ForegroundColor Cyan
Write-Host "  Task      : Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host "  Uninstall : .\windows-installer.ps1 -Uninstall" -ForegroundColor Cyan
Write-Host ""
