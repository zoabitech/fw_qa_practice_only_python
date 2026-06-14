import os
from dotenv import load_dotenv

load_dotenv()

# ── device under test ─────────────────────────────────────────
DEVICE = {
    "host" : os.getenv("DEVICE_HOST"),
    "user" : os.getenv("DEVICE_USER"),
    "pass" : os.getenv("DEVICE_PASS"),
    "port" : int(os.getenv("DEVICE_PORT", 22)),
}

# ── test thresholds ───────────────────────────────────────────
THRESHOLDS = {
    "min_free_memory_mb" : 100,
    "max_packet_loss_pct": 0,
    "ping_count"         : 5,
    "ping_timeout"       : 2,
    "log_lines_to_check" : 100,
    "max_uptime_after_reboot_sec" : 120,  # 2 minutes
}

# ── keywords that indicate a failure in logs ──────────────────
LOG_ERROR_KEYWORDS = [
    "CRITICAL",
    "kernel panic",
    "segfault",
    "out of memory",
    "hardware error",
]
