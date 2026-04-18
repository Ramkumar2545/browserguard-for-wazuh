#!/bin/bash
# =============================================================================
#  BrowserGuard for Wazuh — AUTOMATIC (Silent) macOS Installer
#  Author  : Ram Kumar G (IT Fortress)
#  Version : 1.0.0 (Phase 3 — Privacy-Safe Telemetry Edition)
#  Supports: macOS 12 Monterey, 13 Ventura, 14 Sonoma, 15 Sequoia
#
#  PURPOSE
#    Unattended deployment for Jamf / Kandji / Mosyle / Intune-for-Mac and
#    any mass-provisioning workflow. Always installs with a fixed 30-minute
#    scan interval and NEVER prompts.
#
#  FOR INTERACTIVE INSTALLS, USE:
#    installers/macos-installer.sh
#    install.sh
#
#  ONE-LINE SILENT INSTALL:
#    curl -sSL https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main/installers/automatic/install-macos.sh | bash
#
#  OVERRIDE THE 30m DEFAULT (optional):
#    BPM_INTERVAL=2h bash installers/automatic/install-macos.sh
#    bash installers/automatic/install-macos.sh --interval 1h
# =============================================================================
set -e

# Hard-defaults — no prompts, ever.
export BPM_INTERVAL="${BPM_INTERVAL:-30m}"
export BPM_NONINTERACTIVE="${BPM_NONINTERACTIVE:-1}"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e ""
echo -e "${CYAN}[AUTO] BrowserGuard for Wazuh — Silent macOS Installer${NC}"
echo -e "${CYAN}       Interval : ${BPM_INTERVAL}  (non-interactive)${NC}"
echo -e ""

EXTRA_ARGS=("$@")

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
STANDALONE="$SELF_DIR/../macos-installer.sh"

if [ -f "$STANDALONE" ]; then
    echo -e "${YELLOW}[+] Running local installer: $STANDALONE${NC}"
    exec bash "$STANDALONE" "${EXTRA_ARGS[@]}"
else
    REPO_RAW="https://raw.githubusercontent.com/Ramkumar2545/wazuh-browser-privacy-monitor/main"
    echo -e "${YELLOW}[+] Fetching installer from GitHub...${NC}"
    TMP="$(mktemp -t bpm-install)"
    trap 'rm -f "$TMP"' EXIT
    if command -v curl >/dev/null 2>&1; then
        curl -sSL "$REPO_RAW/install.sh" -o "$TMP"
    else
        echo "[-] curl is required on macOS." >&2
        exit 1
    fi
    exec bash "$TMP" "${EXTRA_ARGS[@]}"
fi
