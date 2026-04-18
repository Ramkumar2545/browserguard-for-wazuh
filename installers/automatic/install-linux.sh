#!/usr/bin/env bash
# =============================================================================
#  BrowserGuard for Wazuh — AUTOMATIC (Silent) Linux Installer
#  Author  : Ram Kumar G (IT Fortress)
#  Version : 1.0.0 (Phase 3 — Privacy-Safe Telemetry Edition)
#
#  PURPOSE
#    Unattended deployment for MDM / Ansible / Intune / SCCM / Puppet /
#    mass-provisioning scripts. Always installs with a fixed 30-minute
#    scan interval and NEVER prompts.
#
#  FOR INTERACTIVE INSTALLS, USE:
#    installers/linux-installer.sh     (asks for interval interactively)
#    install.sh                        (one-line, interactive by default)
#
#  ONE-LINE SILENT INSTALL:
#    curl -sSL https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main/installers/automatic/install-linux.sh | sudo bash
#
#  OVERRIDE THE 30m DEFAULT IF YOU WANT (optional):
#    curl -sSL .../installers/automatic/install-linux.sh | sudo BPM_INTERVAL=2h bash
#    sudo bash installers/automatic/install-linux.sh --interval 1h
# =============================================================================
set -euo pipefail

# Hard-defaults — no prompts, ever.
export BPM_INTERVAL="${BPM_INTERVAL:-30m}"
export BPM_NONINTERACTIVE="${BPM_NONINTERACTIVE:-1}"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e ""
echo -e "${CYAN}[AUTO] BrowserGuard for Wazuh — Silent Linux Installer${NC}"
echo -e "${CYAN}       Interval : ${BPM_INTERVAL}  (non-interactive)${NC}"
echo -e ""

# Forward any extra CLI args to the underlying installer (e.g. --interval 1h).
EXTRA_ARGS=("$@")

# Prefer the colocated standalone installer; fall back to network.
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
STANDALONE="$SELF_DIR/../linux-installer.sh"

if [ -f "$STANDALONE" ]; then
    echo -e "${YELLOW}[+] Running local installer: $STANDALONE${NC}"
    exec sudo -E bash "$STANDALONE" "${EXTRA_ARGS[@]}"
else
    REPO_RAW="https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main"
    echo -e "${YELLOW}[+] Fetching installer from GitHub...${NC}"
    TMP="$(mktemp -t bpm-install.XXXXXX.sh)"
    trap 'rm -f "$TMP"' EXIT
    if command -v curl >/dev/null 2>&1; then
        curl -sSL "$REPO_RAW/install.sh" -o "$TMP"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "$TMP" "$REPO_RAW/install.sh"
    else
        echo "[-] Need curl or wget." >&2
        exit 1
    fi
    exec sudo -E bash "$TMP" "${EXTRA_ARGS[@]}"
fi
