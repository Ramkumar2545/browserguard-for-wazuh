# Automatic (Silent) Installers

Unattended installers for **mass deployment** — MDM, RMM, Ansible, Intune,
Jamf, SCCM, Ninja, Action1, PDQ, Puppet, Chef, etc.

| File | Platform | Default interval |
|------|----------|------------------|
| `install-linux.sh`   | Linux (Ubuntu, Debian, RHEL, Alma, CentOS) | **30 minutes** |
| `install-macos.sh`   | macOS 12+                                  | **30 minutes** |
| `install-windows.ps1`| Windows 10/11/Server                       | **30 minutes** |

These scripts:

- Never prompt the user.
- Pin the scan interval to **30 minutes** by default.
- Call the matching standalone installer (`installers/linux-installer.sh`,
  `installers/macos-installer.sh`, `installers/windows-installer.ps1`) with
  `--interval 30m` / `-Interval 30m` under the hood.
- Exit non-zero if installation fails — safe to use in a CI/CD pipeline or
  MDM pre-flight script.

---

## Difference from the interactive installers

| | `installers/automatic/` | `installers/` (standalone) | `install.sh` / `install.ps1` (root) |
|---|---|---|---|
| Prompts the user? | **Never** | Yes (or `--interval`) | Yes (or `--interval` / `-Interval`) |
| Default interval | **30 m** | User picks | User picks (30 m if skipped) |
| Intended for | MDM / automation | Admin running by hand | Casual one-liner |

The silent installers are a **thin wrapper** over the standalone ones — any
fix we make to the main installers is inherited automatically.

---

## One-line install commands

### Linux (silent, 30 m)

```bash
curl -sSL https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main/installers/automatic/install-linux.sh | sudo bash
```

### macOS (silent, 30 m)

```bash
curl -sSL https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main/installers/automatic/install-macos.sh | bash
```

### Windows (silent, 30 m — Admin PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; iwr -UseBasicParsing 'https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main/installers/automatic/install-windows.ps1' | iex"
```

---

## Override the 30 m default

You can still choose a different interval without dropping back to the
interactive installer — just set the `BPM_INTERVAL` env var or pass
`--interval` / `-Interval`. Accepted values: menu number `1..10`, raw
seconds, or shorthand `30m` / `2h` / `1d` (clamped to `[60s, 86400s]`).

### Linux / macOS

```bash
# Via env var (works with curl | bash):
curl -sSL .../install-linux.sh | sudo BPM_INTERVAL=2h bash

# Via flag (from a cloned repo):
sudo bash installers/automatic/install-linux.sh --interval 1h
bash      installers/automatic/install-macos.sh --interval 300
```

### Windows

```powershell
# Via env var (works with iwr | iex):
$env:BPM_INTERVAL='2h'
iwr -UseBasicParsing 'https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main/installers/automatic/install-windows.ps1' | iex

# Via param (from a downloaded file):
.\install-windows.ps1 -Interval 1h
```

---

## Uninstall

Same mechanism as the standalone installers:

```bash
# Linux
sudo bash installers/linux-installer.sh --uninstall

# macOS
launchctl unload ~/Library/LaunchAgents/com.ramkumar.browser-privacy-monitor.plist
rm -rf ~/.browser-privacy-monitor
```

```powershell
# Windows
.\installers\automatic\install-windows.ps1 -Uninstall
# or
.\install.ps1 -Uninstall
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | Install succeeded |
| 1    | Generic failure (missing Python, permission denied, network error) |
| Other| Propagated from the underlying standalone installer |
