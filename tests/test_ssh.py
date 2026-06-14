def ssh_tests(client, Result, run):
    """
    All tests related to SSH service health.
    Each function checks one thing and one thing only.
    """
    results = []

    # ── test 1 ───────────────────────────────────────────────
    r = Result("SSH service is active")
    output, _ = run(client, "systemctl is-active ssh")
    if output == "active":
        r.passed()
    else:
        r.failed(f"Expected 'active' got '{output}'")
    results.append(r)

    # ── test 2 ───────────────────────────────────────────────
    r = Result("SSH listening on port 22")
    output, _ = run(client, "ss -tlnp | grep ':22'")
    if ":22" in output:
        r.passed()
    else:
        r.failed("Port 22 not open")
    results.append(r)

    # ── test 3 ───────────────────────────────────────────────
    r = Result("sshd process running in memory")
    output, _ = run(client, "pgrep -a sshd")
    if "sshd" in output:
        r.passed()
    else:
        r.failed("sshd process not found")
    results.append(r)

    return results
