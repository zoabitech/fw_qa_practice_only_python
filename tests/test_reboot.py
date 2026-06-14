import time
import paramiko
import logging
from config import DEVICE, THRESHOLDS

def wait_for_device(timeout=60):
    """
    Keep trying to SSH every 5 seconds until device responds.
    This is how FW QA handles device reboots — you wait
    for the device to come back online after a firmware flash.
    """
    logging.info(f"Waiting for device to come back online (max {timeout}s)...")
    start = time.time()

    while time.time() - start < timeout:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                DEVICE["host"],
                username= DEVICE["user"],
                password= DEVICE["pass"],
                timeout = 5
            )
            elapsed = round(time.time() - start)
            logging.info(f"Device back online after {elapsed}s")
            return client
        except Exception:
            logging.info("Device not ready yet, retrying in 5s...")
            time.sleep(5)

    return None  # timed out

def reboot_tests(client, Result, run):
    results = []

    # ── test 1: reboot the device and wait for it ─────────────
    r = Result("Device comes back online after reboot")
    logging.info("Sending reboot command...")

    try:
        # send reboot — connection will drop immediately
        run(client, "sudo reboot")
    except Exception:
        pass  # connection dropping is expected after reboot

    # wait 10 seconds before trying to reconnect
    time.sleep(10)

    new_client = wait_for_device(timeout=60)

    if new_client:
        r.passed()
    else:
        r.failed("Device did not come back online within 60 seconds")
        results.append(r)
        return results, None  # can't run further tests

    results.append(r)

    # ── test 2: SSH works after reboot ────────────────────────
    r = Result("SSH service active after reboot")
    output, _ = run(new_client, "systemctl is-active ssh")
    if output == "active":
        r.passed()
    else:
        r.failed(f"SSH not active after reboot: '{output}'")
    results.append(r)

    # ── test 3: uptime is low (proves it actually rebooted) ───
    r = Result("Uptime confirms fresh reboot")
    output, _ = run(new_client, "cat /proc/uptime | awk '{print int($1)}'")
    try:
        uptime_seconds = int(output)
        threshold      = THRESHOLDS["max_uptime_after_reboot_sec"]
        uptime_minutes = round(uptime_seconds / 60, 1)
        if uptime_seconds < threshold: # less than 2 minutes
            r.passed()
        else:
           r.failed(
            f"Uptime is {uptime_minutes} minutes ({uptime_seconds}s) — "
            f"expected less than {threshold}s after reboot. "
            f"Device may not have actually rebooted."
        )
    except ValueError:
        r.failed(f"Could not read uptime: '{output}'")
    results.append(r)

    # ── test 4: no errors in log after reboot ─────────────────
    r = Result("No critical errors after reboot")
    output, _ = run(new_client, "journalctl -b -n 50 --no-pager")
    critical  = [l for l in output.splitlines() if "CRITICAL" in l]
    if len(critical) == 0:
        r.passed()
    else:
        r.failed(f"Found {len(critical)} critical lines after reboot")
    results.append(r)

    return results, new_client