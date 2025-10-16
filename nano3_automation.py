#!/usr/bin/env python3

import os
import requests
import schedule
import time
from datetime import datetime
import random
import socket
import json
import pytz
import re
import hashlib


# ============ CONFIGURATION ============

# Miner IP address
MINER_IP = "192.168.1.76"
MINER_IP = "192.168.1.162

# Login credentials for power mode control (WebUI)
USERNAME = "georgibtc1111"
PASSWORD = "123"

# Timezone Configuration (e.g., 'America/New_York', 'Europe/Berlin')
YOUR_TIMEZONE = "Europe/Ljubljana"   # Replace with your timezone (list: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)
tz = pytz.timezone(YOUR_TIMEZONE)

# Power Modes (mapping to internal numbers)
POWER_MODES = {
    "Low": "0",
    "Medium": "1",
    "High": "2"
}

# Request settings
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0"

# Miner socket API (default port for CGMiner API)
CGMINER_API_PORT = 4018

# Path to the stats file (in the project directory where this script lives)
STATS_FILE = os.path.join(os.path.dirname(__file__), "miner_status.json")


# ============ UTILITY FUNCTIONS ============

def random_delay():
    """Wait a random delay (between 1-3 seconds) to simulate human behavior."""
    delay = random.uniform(1, 3)
    print(f"[{datetime.now(tz)}] Waiting {delay:.2f} seconds...")
    time.sleep(delay)


def get_actual_mode(session):
    """Check current power mode."""
    url = f"http://{MINER_IP}/updatecgconf.cgi"
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    m = re.search(r'"mode"\s*:\s*"(\d)"', resp.text)
    if m:
        return m.group(1)
    else:
        print("[DEBUG] Could not detect mode from response.")
        print(resp.text)
        return None


def query_cgminer(command):
    """
    Query cgminer socket API.
    Commands: "summary", "stats"
    """
    HOST = MINER_IP
    PORT = CGMINER_API_PORT

    payload = json.dumps({"command": command}) + '\n'

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((HOST, PORT))
            s.sendall(payload.encode('utf-8'))
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk

        response = data.decode('utf-8').strip('\x00').replace('\x00', '')
        result = json.loads(response)
        return result

    except Exception as e:
        print(f"[ERROR] Failed to query cgminer {command}: {e}")
        return None


def write_status_json(current_mode, summary, stats, filename=STATS_FILE):
    """Write miner status to JSON file (overwrite mode)."""
    status = {
        "Mode": current_mode,
        "Summary": summary,
        "Stats": stats
    }
    with open(filename, "w") as f:
        json.dump(status, f, indent=2)
    print(f"[{datetime.now(tz)}] Status saved to {filename}")


# ============ MAIN ACTIONS ============

def login_and_set_power_mode(mode):
    """
    Login to miner WebUI (with hashed password!) and set the power mode.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Connection": "keep-alive",
    })

    try:
        random_delay()

        # --- [1] HASH THE PASSWORD AS JAVASCRIPT DOES ---
        # 1. sha256 hash of PASSWORD (hex digest, lower case)
        # 2. Take first 24 characters
        # 3. Prefix with "ff0000ff"
        hashpasswd = hashlib.sha256(PASSWORD.encode('utf-8')).hexdigest()[:24]
        hashpasswd = "ff0000ff" + hashpasswd

        # --- [2] SET THE 'auth' COOKIE ---
        session.cookies.set("auth", hashpasswd)


        # --- [3] LOGIN WITH HASHED PASSWORD ---
        login_url = f"http://{MINER_IP}/login.cgi"
        login_data = {
            "username": USERNAME,
            "passwd": hashpasswd, # <<< NOT the plain password!
            "loginbtn": "Login"
        }
        resp = session.post(login_url, data=login_data, timeout=REQUEST_TIMEOUT)

        print(f"Login Status: {resp.status_code}")
        print('Session cookies after login:', session.cookies)
        # OPTIONALLY: print the login response text for debugging!
        # print(resp.text)

        # --- [4] SET THE POWER MODE ---
        modeconf_url = f"http://{MINER_IP}/modeconf.cgi"
        modeconf_url = f"http://{MINER_IP}/modeconf.cgi"
        config_data = {
            "mode": POWER_MODES[mode],
            "confirm1btn": "Confirm"
        }
        change_resp = session.post(modeconf_url, data=config_data, timeout=REQUEST_TIMEOUT)
        print(f"Change Status: {change_resp.status_code}")

        time.sleep(3)  # Small wait

         # --- [5] CHECK RESULT ---
        actual_mode = get_actual_mode(session)
        print(f"Actual Mode after change: {actual_mode}")

        if actual_mode == POWER_MODES[mode]:
            print(f"[{datetime.now(tz)}] Successfully changed to {mode} mode")
            # Fetch cgminer data
            summary = query_cgminer("summary")
            stats = query_cgminer("stats")
            write_status_json(mode, summary, stats)
        else:
            print("[ERROR] Mode change failed!")

    except Exception as e:
        print(f"[ERROR] Mode change error: {e}")


def fetch_and_log_cgminer():
    """
    Fetch cgminer summary and stats without changing power mode.
    """
    try:
        print(f"[{datetime.now(tz)}] Fetching miner status...")

        summary = query_cgminer("summary")
        stats = query_cgminer("stats")

        if summary and stats:
            write_status_json("NoChange", summary, stats)
        else:
            print("[ERROR] Failed to fetch summary or stats.")

    except Exception as e:
        print(f"[ERROR] Fetch error: {e}")


# ============ SCHEDULER SETUP ============

# Define your weekly schedule (Day → List of (Time, Mode))
weekly_schedule = {
    "monday": [
        ("00:00", "Medium"),  # 12 AM - 7 AM: Medium
        ("07:00", "Low"),     # 7 AM - 14 PM: Low (Peak)
        ("14:00", "Medium"),  # 14 PM - 16 PM: Medium
        ("16:00", "Low"),     # 16 PM - 20 PM: Low (Peak)
        ("20:00", "Medium")   # 20 PM - 12 AM: Medium
    ],
    "tuesday": [
        ("00:00", "Medium"),
        ("07:00", "Low"),
        ("14:00", "Medium"),
        ("16:00", "Low"),
        ("20:10", "Medium")
    ],
    "wednesday": [
        ("00:00", "Medium"),
        ("07:00", "Low"),
        ("14:00", "Medium"),
        ("16:00", "Low"),
        ("20:00", "Medium")
    ],
    "thursday": [
        ("00:00", "Medium"),
        ("07:00", "Low"),
        ("14:00", "Medium"),
        ("16:00", "Low"),
        ("20:00", "Medium")
    ],
    "friday": [
        ("00:00", "Medium"),
        ("07:00", "Low"),
        ("14:00", "Medium"),
        ("16:00", "Low"),
        ("20:00", "Medium")
    ],
    "saturday": [
        ("00:00", "Medium"),  # All day Medium on weekends
    ],
    "sunday": [
        ("00:00", "Medium"),  # All day Medium on weekends
    ]
}


def setup_scheduler():
    """Set up weekly power mode schedule."""
    for day, time_slots in weekly_schedule.items():
        for time_slot, mode in time_slots:
            schedule_day = getattr(schedule.every(), day)
            schedule_day.at(time_slot).do(
                lambda mode=mode: login_and_set_power_mode(mode)
            )
            print(f"Scheduled {day} at {time_slot} ({YOUR_TIMEZONE}) → {mode} mode")


# Set power mode change schedule
setup_scheduler()

# Fetch cgminer summary and stats every 5 minutes
schedule.every(5).minutes.do(fetch_and_log_cgminer)
print("Scheduled cgminer logging every 10 minutes.")

# Run forever
print(f"Starting miner scheduler (Timezone: {YOUR_TIMEZONE}). Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)
