from config import THRESHOLDS, LOG_ERROR_KEYWORDS

def network_tests(client, Result, run):
    """
    All tests related to network health.
    """
    results = []

    # ── test 1 ───────────────────────────────────────────────
    r = Result("Network interface is UP")
    output, _ = run(client, "ip link show | grep 'state UP'")
    if "UP" in output:
        r.passed()
    else:
        r.failed("No interface in UP state")
    results.append(r)

    # ── test 2 ───────────────────────────────────────────────
    r = Result("Can reach gateway")
    gateway, _ = run(client, "ip route | grep default | awk '{print $3}'")
    output, _  = run(client, f"ping -c 3 -W 2 {gateway}")
    if "0% packet loss" in output:
        r.passed()
    else:
        r.failed(f"Packet loss to gateway {gateway}")
    results.append(r)

    # ── test 3 ───────────────────────────────────────────────

    r = Result("Free memory above 100MB")
    output, _ = run(client, "free -m | awk '/^Mem:/{print $4}'")
    try:
        free_mb = int(output)
        threshold = THRESHOLDS["min_free_memory_mb"]
        if free_mb > threshold:
             r.passed()
        else:
         r.failed(f"Only {free_mb}MB free — minimum is {threshold}MB")

    except ValueError:
        r.failed(f"Could not read memory value: '{output}'")
    results.append(r)

    # ── test 4 ───────────────────────────────────────────────
    r = Result("No critical errors in system log")
    output, _ = run(client, "journalctl -n 50 --no-pager")
    critical = [l for l in output.splitlines()
            if any(kw in l for kw in LOG_ERROR_KEYWORDS)]
    if len(critical) == 0:
        r.passed()
    else:
        r.failed(f"Found {len(critical)} critical lines")
    results.append(r)

    return results
