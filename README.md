# FW QA Automation Framework

A Python-based test automation framework built to simulate
firmware QA workflows used in network hardware environments.
Tests are executed remotely over SSH against a Linux device,
mirroring real-world firmware validation practices.

---

## What This Framework Does

- Connects to a remote Linux device over SSH
- Runs automated test suites across multiple domains
- Logs every session to a timestamped log file
- Saves detailed JSON reports after every run
- Supports optional destructive tests via CLI flags

---

## Test Coverage

| Area        | Tests                                      | Type        |
| ----------- | ------------------------------------------ | ----------- |
| SSH Service | Active status, port 22, process in memory  | Functional  |
| Network     | Interface UP, gateway ping, DNS resolution | Functional  |
| Memory      | Free memory above threshold                | Performance |
| System Logs | No critical errors in last 100 lines       | Functional  |
| Reboot      | Device recovery, uptime, post-boot health  | Regression  |

---

## Project Structure

fw_qa_practice_only_python/

├── tests/

│ ├── test_ssh.py # SSH service health tests

│ ├── test_network.py # Network connectivity tests

│ └── test_reboot.py # Post-reboot validation tests

├── reports/ # Auto-generated JSON reports

├── logs/ # Auto-generated session logs

├── run_tests.py # Main runner and framework engine

├── config.py # All thresholds and settings

├── .env.example # Credential template (safe to share)

└── requirements.txt # Python dependencies

---

## How to Run

**Install dependencies**

```bash
pip3 install -r requirements.txt
```

**Set up credentials**

```bash
cp .env.example .env
nano .env  # fill in your device details
```

**Run full test suite**

```bash
python3 run_tests.py
```

**Run with reboot test**

```bash
python3 run_tests.py --reboot
```

---

## Sample Output

2026-06-13 23:00:49,092 INFO Log file created: logs/session_20260613_230049.log
2026-06-13 23:00:49,092 INFO Test suite started

==================================================
QA Test Suite
Device : 10.0.0.21
Time : 2026-06-13 23:00:49
==================================================
2026-06-13 23:00:49,093 INFO Connecting to 10.0.x.x...
2026-06-13 23:00:49,213 INFO Connected (version 2.0, client OpenSSH_9.6p1)
2026-06-13 23:00:49,301 INFO Authentication (publickey) failed.
2026-06-13 23:00:49,517 INFO Authentication (publickey) failed.
2026-06-13 23:00:49,662 INFO Authentication (password) successful!
2026-06-13 23:00:49,662 INFO Connected successfully
[ SSH Tests ]
2026-06-13 23:00:49,931 INFO PASS - SSH service is active
✅ PASS SSH service is active
2026-06-13 23:00:50,033 INFO PASS - SSH listening on port 22
✅ PASS SSH listening on port 22
2026-06-13 23:00:50,137 INFO PASS - sshd process running in memory
✅ PASS sshd process running in memory

[ Network Tests ]
2026-06-13 23:00:50,196 INFO PASS - Network interface is UP
✅ PASS Network interface is UP
2026-06-13 23:00:52,317 INFO PASS - Can reach gateway
✅ PASS Can reach gateway
2026-06-13 23:00:52,378 INFO PASS - Free memory above 100MB
✅ PASS Free memory above 100MB
2026-06-13 23:00:52,486 INFO PASS - No critical errors in system log
✅ PASS No critical errors in system log

[ Reboot Tests ]
2026-06-13 23:00:52,486 INFO Sending reboot command...
2026-06-13 23:01:02,584 INFO Waiting for device to come back online (max 60s)...
2026-06-13 23:01:07,589 INFO Device not ready yet, retrying in 5s...
2026-06-13 23:01:17,595 INFO Device not ready yet, retrying in 5s...
2026-06-13 23:01:27,600 INFO Device not ready yet, retrying in 5s...
2026-06-13 23:01:36,735 INFO Device not ready yet, retrying in 5s...
2026-06-13 23:01:41,885 INFO Connected (version 2.0, client OpenSSH_9.6p1)
2026-06-13 23:01:41,975 INFO Authentication (publickey) failed.
2026-06-13 23:01:42,184 INFO Authentication (publickey) failed.
2026-06-13 23:01:42,328 INFO Authentication (password) successful!
2026-06-13 23:01:42,328 INFO Device back online after 40s
2026-06-13 23:01:42,328 INFO PASS - Device comes back online after reboot
✅ PASS Device comes back online after reboot
2026-06-13 23:01:43,056 INFO PASS - SSH service active after reboot
✅ PASS SSH service active after reboot
2026-06-13 23:01:43,116 INFO PASS - Uptime confirms fresh reboot
✅ PASS Uptime confirms fresh reboot
2026-06-13 23:01:43,201 INFO PASS - No critical errors after reboot
✅ PASS No critical errors after reboot

==================================================
SUMMARY
Total : 11
Passed : 11
Failed : 0
==================================================

Report saved → reports/report_20260613_230143.json

---

## Bug Reports

### BUG-001 — Uptime test false failure

- **Test:** Uptime confirms fresh reboot
- **Finding:** Device uptime was 109225s (~30hrs)
- **Root cause:** Reboot requires passwordless sudo access
- **Fix:** Added NOPASSWD for reboot in sudoers
- **Status:** Resolved ✅

---

## Skills Demonstrated

- Python scripting and test automation without external frameworks
- SSH-based remote device testing using Paramiko
- Structured logging and JSON report generation
- Test design across functional, performance, and regression areas
- Bug investigation, root cause analysis, and documentation
- Secure credential handling with .env and .gitignore

---

## Environment

- Controller : any Linux/Mac/Windows laptop
- Device : Ubuntu Linux (acts as firmware device)
- Language : Python 3
- Protocol : SSH via Paramiko
