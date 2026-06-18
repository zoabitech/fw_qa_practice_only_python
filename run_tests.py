import os
import json
import datetime
import paramiko
import logging
from dotenv import load_dotenv
from config import DEVICE, THRESHOLDS, LOG_ERROR_KEYWORDS
import sys
from tests.test_reboot import reboot_tests
from tests.test_performance import performance_tests
load_dotenv()


# setup logger
def setup_logger():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = f"logs/session_{timestamp}.log"

    logging.basicConfig(
        level   = logging.INFO,
        format  = "%(asctime)s  %(levelname)s  %(message)s",
        handlers= [
            logging.FileHandler(log_file),    # saves to file
            logging.StreamHandler()           # also prints to terminal
        ]
    )
    logging.info(f"Log file created: {log_file}")
    return log_file

# ── 1. connect to the device ──────────────────────────────────
def connect():
    logging.info(f"Connecting to {DEVICE['host']}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        DEVICE["host"],
        port    = DEVICE["port"],
        username= DEVICE["user"],
        password= DEVICE["pass"],
        timeout = 5
    )
    logging.info("Connected successfully")
    return client


# ── 2. run a command on the device ───────────────────────────

def run(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode().strip()
    error  = stderr.read().decode().strip()
    return output, error

# ── 3. result tracker ─────────────────────────────────────────

class Result:
    def __init__(self, name):
        self.name    = name
        self.status  = None
        self.message = ""

    def passed(self):
        self.status = "PASS"
        logging.info(f"PASS - {self.name}")
        print(f"  ✅ PASS  {self.name}")

    def failed(self, reason):
        self.status  = "FAIL"
        self.message = reason
        logging.error(f"FATAL - {self.name} - {reason}")
        print(f"  ❌ FAIL  {self.name}")
        print(f"           → {reason}")

# ── 4. save report ────────────────────────────────────────────

def save_report(results):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"reports/report_{timestamp}.json"

    data = {
        "timestamp" : datetime.datetime.now().isoformat(),
        "device"    : os.getenv("DEVICE_HOST"),
        "total"     : len(results),
        "passed"    : len([r for r in results if r.status == "PASS"]),
        "failed"    : len([r for r in results if r.status == "FAIL"]),
        "tests"     : [
            {
                "name"    : r.name,
                "status"  : r.status,
                "message" : r.message
            }
            for r in results
        ]
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n  Report saved → {filename}")

# ── 5. print summary ──────────────────────────────────────────

def print_summary(results):
    passed = [r for r in results if r.status == "PASS"]
    failed = [r for r in results if r.status == "FAIL"]

    print(f"\n{'='*50}")
    print(f"  SUMMARY")
    print(f"  Total  : {len(results)}")
    print(f"  Passed : {len(passed)}")
    print(f"  Failed : {len(failed)}")
    print(f"{'='*50}")

    if failed:
        print("\n  Failed tests:")
        for r in failed:
            print(f"  ✗  {r.name}")
            print(f"     {r.message}")

# ── 6. main runner ────────────────────────────────────────────

def main():

    log_file = setup_logger()
    logging.info("Test suite started")
    # import all your test files here
    from tests.test_ssh     import ssh_tests
    from tests.test_network import network_tests

    print(f"\n{'='*50}")
    print(f"  MOCK QA Test Suite")
    print(f"  Device  : {os.getenv('DEVICE_HOST')}")
    print(f"  Time    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    try:
        client = connect()
    except Exception as e:
        print(f"\n  FATAL: Could not connect — {e}")
        return

    all_results = []
    
    # run each test group
    print("  [ SSH Tests ]")
    all_results += ssh_tests(client, Result, run)

    print("\n  [ Network Tests ]")
    all_results += network_tests(client, Result, run)

    print("\n  [ Performance Tests ]")
    all_results += performance_tests(client, Result, run)

    # check if user passed --reboot flag
    run_reboot = "--reboot" in sys.argv

    if run_reboot:
        print("\n  [ Reboot Tests ]")
        reboot_results, client = reboot_tests(client, Result, run)
        all_results += reboot_results
    client.close()

    print_summary(all_results)
    save_report(all_results)

if __name__ == "__main__":
    main()
