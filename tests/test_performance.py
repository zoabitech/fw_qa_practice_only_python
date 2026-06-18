import time
import logging

def performance_tests(client, Result, run):
    # this list will collect all our results
    results = []

    # ── TEST 1: How fast does the gateway answer? ─────────────

    r = Result("Ping latency under 10ms to gateway")

    # first find the gateway IP
    gateway, _ = run(client, "ip route | grep default | awk '{print $3}'")

    # ping it 10 times and get the timing results
    output, _  = run(client, f"ping -c 10 {gateway}")

    # the last line of ping looks like this:
    # rtt min/avg/max/mdev = 0.4/0.6/1.2/0.1 ms
    # we want the average (second number)
    try:
        last_line = output.strip().split("\n")[-1]
        avg_ms    = float(last_line.split("/")[4])

        logging.info(f"Average ping latency: {avg_ms}ms")

        if avg_ms < 10:
            r.passed()
        else:
            r.failed(f"Too slow! Average was {avg_ms}ms, max allowed is 10ms")

    except Exception as e:
        r.failed(f"Could not read ping result: '{output}' error: {e}")

    results.append(r)


    # ── TEST 2: How busy is the CPU? ──────────────────────────
    # CPU is the brain of the computer
    # if the brain is 95% busy, the device is struggling

    r = Result("CPU usage below 80%")

    output, _ = run(client,
        "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
    )

    try:
        cpu_usage = float(output.strip())
        logging.info(f"CPU usage: {cpu_usage}%")

        if cpu_usage < 80:
            r.passed()
        else:
            r.failed(f"CPU too busy! At {cpu_usage}%, max allowed is 80%")

    except Exception as e:
        r.failed(f"Could not read CPU usage: '{output}' error: {e}")

    results.append(r)


    # ── TEST 3: How full is the hard drive? ───────────────────
    # if it's 95% full you can barely fit anything new in
    # if the hard drive is full, the device can't save logs
    # and will start behaving very strangely

    r = Result("Disk usage below 90%")

    output, _ = run(client, "df / | tail -1 | awk '{print $5}'")

    try:
        # output looks like "45%" — remove the % sign
        disk_pct = int(output.replace("%", "").strip())
        logging.info(f"Disk usage: {disk_pct}%")

        if disk_pct < 90:
            r.passed()
        else:
            r.failed(f"Disk almost full! At {disk_pct}%, max allowed is 90%")

    except Exception as e:
        r.failed(f"Could not read disk usage: '{output}' error: {e}")

    results.append(r)


    # ── TEST 4: How fast does the device respond? ─────────────
    # this is like a reaction time test
    # we send a simple command and measure how long
    # it takes to get an answer back
    # if it takes more than 2 seconds something is very wrong

    r = Result("Device responds to commands within 2 seconds")

    start   = time.time()              # start the stopwatch
    run(client, "uname -a")           # send a simple command
    elapsed = time.time() - start     # stop the stopwatch

    logging.info(f"Command response time: {round(elapsed, 2)}s")

    if elapsed < 2:
        r.passed()
    else:
        r.failed(f"Device too slow! Took {round(elapsed,2)}s, max is 2s")

    results.append(r)


    # ── TEST 5: How much memory is free? ──────────────────────
    # memory (RAM) is like your desk workspace
    # devices need free memory to handle network traffic

    r = Result("Free memory above 100MB")

    output, _ = run(client, "free -m | awk '/^Mem:/{print $4}'")

    try:
        free_mb = int(output.strip())
        logging.info(f"Free memory: {free_mb}MB")

        if free_mb > 100:
            r.passed()
        else:
            r.failed(f"Not enough memory! Only {free_mb}MB free, need 100MB")

    except Exception as e:
        r.failed(f"Could not read memory: '{output}' error: {e}")

    results.append(r)

    return results