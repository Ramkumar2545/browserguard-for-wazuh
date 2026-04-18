"""Build all BrowserGuard for Wazuh diagrams."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _style import (
    new_fig, box, arrow, title, footer, legend, save,
    BG, PANEL, PANEL_HI, TEXT, MUTED, GRID,
    BLUE, GREEN, AMBER, RED, PURPLE, CYAN, PINK,
)

OUT = os.path.dirname(__file__)


# ─────────────────────────────────────────────────────────────────────────────
# 01 — High-level architecture
# ─────────────────────────────────────────────────────────────────────────────
def fig_01_architecture():
    fig, ax = new_fig(14, 8)
    title(ax, "BrowserGuard for Wazuh — High-Level Architecture",
          "Raw data stays on the endpoint · Only redacted JSON reaches the SIEM")

    # Row 1: Endpoints
    box(ax, 2, 63, 28, 22,
        title="Windows Endpoint",
        subtitle="SYSTEM scheduled task",
        lines=["Chrome · Edge · Brave · Firefox",
               "Opera · OperaGX · Vivaldi · Chromium",
               "C:\\BrowserPrivacyMonitor\\"],
        color=BLUE)
    box(ax, 36, 63, 28, 22,
        title="Linux Endpoint",
        subtitle="systemd service",
        lines=["Chrome · Chromium · Brave · Firefox",
               "Opera · OperaGX · Vivaldi",
               "/root/.browser-privacy-monitor/"],
        color=GREEN)
    box(ax, 70, 63, 28, 22,
        title="macOS Endpoint",
        subtitle="LaunchAgent",
        lines=["Safari · Chrome · Edge · Brave",
               "Firefox · Opera · Vivaldi",
               "~/.browser-privacy-monitor/"],
        color=PURPLE)

    # Row 2: Local collector (spans)
    box(ax, 15, 38, 70, 18,
        title="Phase 3 Collector  —  browser-privacy-monitor.py",
        subtitle="Reads browser history locally · classifies risk · redacts · hashes",
        lines=["1. Read history DB (read-only)     4. Classify risk category",
               "2. Detect sensitive patterns       5. Redact URL, token, title",
               "3. SHA-256 hash for correlation    6. Emit JSON line to local log"],
        color=CYAN)

    # Row 3: Wazuh
    box(ax, 10, 10, 38, 20,
        title="Wazuh Agent",
        subtitle="Reads local browser_privacy.log (log_format=json)",
        lines=["ossec.conf <localfile>",
               "label key=\"integration\"",
               "  → browser-privacy-monitor"],
        color=AMBER)
    box(ax, 52, 10, 38, 20,
        title="Wazuh Manager & Dashboard",
        subtitle="Decoder + rules → alerts",
        lines=["0320-browser_privacy_decoder.xml",
               "0320-browser_privacy_rules.xml",
               "Rule IDs 901000 – 901030"],
        color=RED)

    # Arrows
    for x in (16, 50, 84):
        arrow(ax, x, 63, x, 56, color=MUTED, style="-|>", lw=1.3)
    arrow(ax, 50, 38, 29, 30, color=CYAN, label="redacted JSON lines",
          label_offset=(0, 1.6))
    arrow(ax, 48, 20, 52, 20, color=AMBER, label="forward events",
          label_offset=(0, 1.6))

    legend(ax, [("Endpoints", BLUE), ("Collector", CYAN),
                ("Wazuh Agent", AMBER), ("Manager", RED)], x=2, y=5)
    footer(ax, "github.com/Ramkumar2545/wazuh-browser-privacy-monitor")
    save(fig, os.path.join(OUT, "01-architecture.png"))


# ─────────────────────────────────────────────────────────────────────────────
# 02 — End-to-end data flow
# ─────────────────────────────────────────────────────────────────────────────
def fig_02_dataflow():
    fig, ax = new_fig(15, 7.5)
    title(ax, "End-to-End Data Flow",
          "From browser history to a Wazuh alert — in six steps")

    stages = [
        dict(x=2,  color=BLUE,   t="1 · Browser",
             s="native history DB",
             lines=["User visits a URL",
                    "Written to history",
                    "(Chrome/Edge/Firefox/…)"]),
        dict(x=18, color=CYAN,   t="2 · Collect",
             s="every N minutes",
             lines=["Read history SQLite",
                    "Only rows since last",
                    "scan (state file)"]),
        dict(x=34, color=AMBER,  t="3 · Classify",
             s="risk rules on endpoint",
             lines=["domain categories",
                    "pattern detection",
                    "risk_score 0–10"]),
        dict(x=50, color=PURPLE, t="4 · Redact",
             s="strip before writing",
             lines=["url → url_redacted",
                    "url_hash (SHA-256)",
                    "title_redacted"]),
        dict(x=66, color=GREEN,  t="5 · Log",
             s="browser_privacy.log",
             lines=["JSON-lines file",
                    "chmod 600",
                    "label integration"]),
        dict(x=82, color=RED,    t="6 · Alert",
             s="Wazuh manager",
             lines=["decoder extracts",
                    "rules 901000–901030",
                    "dashboard alert"]),
    ]
    for s in stages:
        box(ax, s["x"], 38, 14, 36, title=s["t"], subtitle=s["s"],
            lines=s["lines"], color=s["color"], title_size=11)

    # Flow arrows
    for i in range(len(stages) - 1):
        x1 = stages[i]["x"] + 14
        x2 = stages[i + 1]["x"]
        arrow(ax, x1, 56, x2, 56, color=MUTED, lw=1.4)

    # Bottom strip: WHAT LEAVES the endpoint
    box(ax, 4, 7, 92, 22,
        title="What actually leaves the endpoint",
        subtitle="One JSON line per detected browser visit",
        lines=[
            '{ "integration": "browser-privacy-monitor",  "event_type": "browser_visit",',
            '  "endpoint": "WIN-LC4CKA943ST",   "user": "ram",   "browser": "edge",',
            '  "domain": "accounts.google.com", "sensitive_detected": "true",',
            '  "sensitive_type": "credential_page",  "risk_category": "auth",  "risk_score": 8,',
            '  "url_redacted": "https://accounts.google.com/****",   "url_hash": "a1b2c3…",',
            '  "title_redacted": "Sign in - ****",                   "title_hash": "9f8e7d…" }',
        ],
        color=GREEN, mono=True, text_size=9)

    footer(ax, "No raw URLs · No tokens · No passwords · Only masked evidence + SHA-256 for correlation")
    save(fig, os.path.join(OUT, "02-dataflow.png"))


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint OS diagram (shared helper)
# ─────────────────────────────────────────────────────────────────────────────
def endpoint_diagram(
    filename, os_name, accent,
    install_path, log_path, config_path, runner_label, runner_lines,
    install_cmd, start_cmd, restart_cmd, uninstall_cmd,
    browsers,
):
    fig, ax = new_fig(14, 8.5)
    title(ax, f"{os_name} Endpoint — Install & Runtime",
          "How the Phase 3 collector runs on this OS")

    # Top: User & browsers
    box(ax, 4, 70, 30, 18,
        title="User browsers",
        subtitle="read-only history access",
        lines=browsers, color=BLUE)

    # Center: Collector process
    box(ax, 40, 68, 30, 22,
        title=runner_label,
        subtitle="runs browser-privacy-monitor.py",
        lines=runner_lines, color=accent)

    # Right: Wazuh agent
    box(ax, 76, 70, 22, 18,
        title="Wazuh Agent",
        subtitle="localfile → manager",
        lines=["log_format=json",
               "label integration",
               "= browser-privacy-monitor"],
        color=AMBER)

    # Files on disk
    box(ax, 4, 40, 60, 20,
        title="Files on disk",
        subtitle=f"{install_path}",
        lines=[
            f"collector : browser-privacy-monitor.py",
            f"config    : {config_path}",
            f"log (600) : {log_path}",
        ],
        color=MUTED, fill=PANEL_HI, mono=True)

    # Commands
    box(ax, 68, 40, 30, 20,
        title="Operator commands",
        subtitle="",
        lines=[
            f"install   : {install_cmd}",
            f"start     : {start_cmd}",
            f"restart   : {restart_cmd}",
            f"uninstall : {uninstall_cmd}",
        ],
        color=accent, fill=PANEL_HI, mono=True, text_size=8.5)

    # Arrows
    arrow(ax, 34, 79, 40, 79, color=BLUE, label="history DB read")
    arrow(ax, 55, 68, 55, 60, color=accent, label="append JSON line",
          label_offset=(10, 0))
    # Curve the Wazuh-agent tail arrow high above the Files-on-disk panel
    # so its label sits above the collector, clear of the "append JSON line" label.
    arrow(ax, 64, 50, 76, 78, color=AMBER, label="tail log_format=json",
          curved=-0.45, label_offset=(-2, 6))

    footer(ax, f"Scan interval is set at install time and saved in {config_path}")
    save(fig, os.path.join(OUT, filename))


def fig_03_windows():
    endpoint_diagram(
        "03-endpoint-windows.png", "Windows", BLUE,
        install_path=r"C:\BrowserPrivacyMonitor\\",
        log_path=r"C:\BrowserPrivacyMonitor\browser_privacy.log",
        config_path=r"C:\BrowserPrivacyMonitor\.browser_privacy_config.json",
        runner_label="Scheduled Task (SYSTEM)",
        runner_lines=["TaskName: BrowserPrivacyMonitor",
                      "Trigger : AtStartup + Repeat",
                      "RunAs   : SYSTEM  (Highest)",
                      "Exec    : pythonw.exe"],
        install_cmd="iwr install.ps1 | iex",
        start_cmd ="Start-ScheduledTask",
        restart_cmd="Restart-Service WazuhSvc",
        uninstall_cmd=".\\install.ps1 -Uninstall",
        browsers=["Chrome · Edge · Brave",
                  "Firefox · Opera · OperaGX",
                  "Vivaldi · Chromium"],
    )


def fig_04_linux():
    endpoint_diagram(
        "04-endpoint-linux.png", "Linux", GREEN,
        install_path="/root/.browser-privacy-monitor/",
        log_path="/root/.browser-privacy-monitor/browser_privacy.log",
        config_path="/root/.browser-privacy-monitor/.browser_privacy_config.json",
        runner_label="systemd service",
        runner_lines=["Unit    : browser-privacy-monitor",
                      "Type    : simple",
                      "Restart : always (RestartSec=10)",
                      "Exec    : python3 collector.py"],
        install_cmd="curl … | sudo bash",
        start_cmd ="systemctl start browser-privacy-monitor",
        restart_cmd="systemctl restart wazuh-agent",
        uninstall_cmd="sudo bash linux-installer.sh --uninstall",
        browsers=["Chrome · Chromium · Brave",
                  "Firefox · Opera · OperaGX",
                  "Vivaldi"],
    )


def fig_05_macos():
    endpoint_diagram(
        "05-endpoint-macos.png", "macOS", PURPLE,
        install_path="~/.browser-privacy-monitor/",
        log_path="~/.browser-privacy-monitor/browser_privacy.log",
        config_path="~/.browser-privacy-monitor/.browser_privacy_config.json",
        runner_label="LaunchAgent",
        runner_lines=["Label   : com.ramkumar.browser-privacy-monitor",
                      "RunAtLoad + KeepAlive",
                      "StartInterval = scan_interval_seconds",
                      "Requires: Full Disk Access"],
        install_cmd="curl … | bash",
        start_cmd ="launchctl load plist",
        restart_cmd="/Library/Ossec/bin/wazuh-control restart",
        uninstall_cmd="launchctl unload plist + rm -rf ~/.browser-privacy-monitor",
        browsers=["Safari · Chrome · Edge",
                  "Brave · Firefox · Opera",
                  "Vivaldi"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# 06 — Privacy / redaction diagram
# ─────────────────────────────────────────────────────────────────────────────
def fig_06_privacy():
    fig, ax = new_fig(14, 8)
    title(ax, "Privacy-Safe Redaction",
          "Raw browsing data never leaves the endpoint — only masked evidence does")

    # Left: raw
    box(ax, 2, 40, 44, 46,
        title="RAW (stays on endpoint only)",
        subtitle="Never written to Wazuh log",
        lines=[
            "url      = https://accounts.google.com/signin",
            "          ?token=eyJhbGciOiJIUzI1NiJ9…",
            "title    = Sign in - ram@example.com",
            "cookies  = SID=xyz123; HSID=abc…",
            "referrer = https://mail.google.com/mail/u/0/",
            "",
            "Lives only in :",
            "  browser history DB (read-only)",
            "  collector process memory (ephemeral)",
        ],
        color=RED, fill=PANEL_HI, mono=True, text_size=9.5)

    # Right: redacted
    box(ax, 54, 40, 44, 46,
        title="REDACTED (safe to log & forward)",
        subtitle="Everything Wazuh actually sees",
        lines=[
            "domain          = accounts.google.com",
            "url_redacted    = https://accounts.google.com/****",
            "url_hash        = a1b2c3d4… (SHA-256)",
            "title_redacted  = Sign in - ****",
            "title_hash      = 9f8e7d6c… (SHA-256)",
            "sensitive_type  = credential_page",
            "risk_category   = auth",
            "risk_score      = 8",
        ],
        color=GREEN, fill=PANEL_HI, mono=True, text_size=9.5)

    # Arrow between
    arrow(ax, 46, 63, 54, 63, color=PURPLE, label="redact + SHA-256", lw=2,
          label_offset=(0, 2))

    # Bottom: guarantees
    box(ax, 2, 7, 96, 24,
        title="Guarantees",
        subtitle="",
        lines=[
            "✓ No raw URL         ✓ No tokens / JWT     ✓ No passwords        ✓ No API keys",
            "✓ No full title      ✓ No cookies / SID    ✓ No email addresses  ✓ No referrer URLs",
            "",
            "Correlation still works — analysts pivot on url_hash / title_hash across endpoints",
            "without ever learning the underlying URL or title.",
        ],
        color=CYAN, fill=PANEL_HI, text_size=10)

    footer(ax, "Phase 3 — Privacy-Safe Telemetry Edition")
    save(fig, os.path.join(OUT, "06-privacy-redaction.png"))


# ─────────────────────────────────────────────────────────────────────────────
# 07 — Rule chain (Suricata 86600 → 901xxx)
# ─────────────────────────────────────────────────────────────────────────────
def fig_07_rules():
    fig, ax = new_fig(14, 9)
    title(ax, "Wazuh Rule Chain",
          "Built-in Suricata rule 86600 · chained → custom rules 901000–901030")

    # Top: event arrives
    box(ax, 30, 80, 40, 10,
        title="Incoming JSON event",
        subtitle="browser_privacy.log line",
        lines=['integration = "browser-privacy-monitor"',
               'event_type  = "browser_visit"'],
        color=CYAN, mono=True, text_size=9)

    # Layer 1: 86600
    box(ax, 30, 62, 40, 12,
        title="Rule 86600 (built-in Suricata JSON catch-all)",
        subtitle="matches any JSON event with event_type set",
        lines=['<field name="event_type">\\.+</field>   →   level 0'],
        color=AMBER, mono=True, text_size=9)
    arrow(ax, 50, 80, 50, 74, color=MUTED)

    # Layer 2: parents (if_sid 86600)
    box(ax, 2, 38, 30, 18,
        title="901000  service_started",
        subtitle="if_sid 86600",
        lines=["match integration",
               "match event_type = service_started"],
        color=GREEN, text_size=9)
    box(ax, 35, 38, 30, 18,
        title="901001  service_stopped",
        subtitle="if_sid 86600",
        lines=["match integration",
               "match event_type = service_stopped"],
        color=GREEN, text_size=9)
    box(ax, 68, 38, 30, 18,
        title="901010  browser_visit  (parent)",
        subtitle="if_sid 86600",
        lines=["match integration",
               "match event_type = browser_visit"],
        color=BLUE, text_size=9)

    for x in (17, 50, 83):
        arrow(ax, 50, 62, x, 56, color=MUTED, lw=1.3)

    # Layer 3: children of 901010
    children = [
        ("901011 clean",          GREEN),
        ("901012 sensitive",      AMBER),
        ("901013 auth_token",     RED),
        ("901014 password_reset", RED),
        ("901015 auth_code",      RED),
        ("901016 api_key",        RED),
        ("901017 credential",     RED),
        ("901018 email",          AMBER),
        ("901019 internal_doc",   AMBER),
        ("901020 cloud_storage",  AMBER),
        ("901021 anonymizer",     PINK),
        ("901022 file_download",  AMBER),
        ("901023 token",          RED),
        ("901024 credential_page",RED),
    ]
    # grid 7 cols x 2 rows — shrink font so labels fit inside their boxes
    col_w = 13.8
    row_h = 6
    start_x = 2
    for i, (lbl, col) in enumerate(children):
        r, c = divmod(i, 7)
        x = start_x + c * col_w
        y = 22 - r * (row_h + 1)
        box(ax, x, y, col_w - 0.8, row_h,
            title=lbl, subtitle=None, lines=None,
            color=col, fill=PANEL_HI, title_size=7.6)

    arrow(ax, 83, 38, 50, 28, color=BLUE, curved=0.2,
          label="if_sid 901010", label_offset=(0, 1.2))

    # Composite high-risk — lifted above footer
    box(ax, 30, 6, 40, 7,
        title="901030  high-risk composite",
        subtitle="correlates multiple 90101x hits · level 12",
        lines=None, color=PINK, fill=PANEL_HI)

    footer(ax, "Chaining via if_sid 86600 prevents Suricata's JSON catch-all from swallowing our events")
    save(fig, os.path.join(OUT, "07-rule-chain.png"))


if __name__ == "__main__":
    fig_01_architecture()
    fig_02_dataflow()
    fig_03_windows()
    fig_04_linux()
    fig_05_macos()
    fig_06_privacy()
    fig_07_rules()
    print("All diagrams generated in:", OUT)
