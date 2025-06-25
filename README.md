
# Avalon Nano 3 Home Miner Automation Script

## What This Script Does

This Python script is designed to automate **Canaan Avalon Miner** management with the following features:

- **Power Mode Management:**  
  Change the miner's power mode (`Low`, `Medium`, `High`) according to a customizable weekly schedule.

- **Miner Status Logging:**  
  Fetches real-time performance data including hashrates, temperatures, hardware errors, fan speed, and more.

- **Reliable Data Fetching:**  
  Uses the native **CGMiner API (port 4028)** for fetching miner statistics, which is significantly more stable than scraping the Web UI.

- **JSON Logging:**  
  Saves the miner's current mode, summary, and stats to a file called `miner_status.json` (overwrites each time with the latest snapshot).

- **Fully Offline Local Solution:**  
  No cloud, no external servers — runs directly on your Raspberry Pi or any local machine on the same network.

---

## How It Works — Step by Step

### 1 **Login & Power Mode Control**
- Logs into the miner's Web interface (`http://[MINER_IP]/login.cgi`).
- Changes the miner's power mode (`Low`, `Medium`, `High`) by sending a form POST request to `modeconf.cgi`.
- Verifies that the power mode was correctly set by fetching `updatecgconf.cgi`.

### 2️ **Miner Data Fetch (Summary + Stats)**
- Connects directly to the miner's **CGMiner socket API (port 4028)**.
- Fetches:
  - **Summary:** Hash rates, uptime, errors, best share, work utility, etc.
  - **Stats:** Temperatures, fan speed, PSU info, chip status, and detailed internal hardware data.

### 3️ **Logging to JSON**
- Combines power mode, summary, and stats into a single JSON file.
- Overwrites the file `miner_status.json` with each new fetch.

### 4 **Automated Scheduler**
- Power modes are scheduled via a weekly schedule (editable in the script).
- Miner stats are fetched every **5 minutes** by default and can be used for further usage like sending data via Telegram bot or DMing yourself on Nostr.

---

##  Requirements

-  Python 3.x
-  Pip packages:
  - `requests`
  - `schedule`
  - `pytz`

### Install dependencies:


`pip install requests schedule pytz`

---

## How to Set Up

### 1. Clone or Copy the Script

Save the provided script as `miner_automation.py` (or any filename you like).

---

### 2. Configure Your Settings

Edit the following section at the top of the script:

```python
# Miner Configuration
MINER_IP = "192.168.0.103"      # Replace with your miner's IP
USERNAME = "root"              # Login username (default: root)
PASSWORD = "root"              # Login password (default: root)

# Timezone
YOUR_TIMEZONE = "Europe/Monaco"  # Replace with your timezone (list: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)
```

---

### 3. Configure Power Mode Schedule

Example block inside the script:

```python
weekly_schedule = {
    "monday": [("00:00", "Low")],
    "tuesday": [("00:00", "Low")],
    "wednesday": [("00:00", "Low")],
    "thursday": [("00:00", "Low")],
    "friday": [("00:00", "Low")],
    "saturday": [("00:00", "Medium")],
    "sunday": [("00:00", "Medium")]
}
```

- You can add multiple entries per day like this:

```python
"monday": [
    ("00:00", "Low"),
    ("08:00", "Medium"),
    ("20:00", "High")
]
```

Time format is 24-hour (`HH:MM`).

---

### 4. Run the Script

Run it in your terminal:

```bash
python3 miner_automation.py
```

### Output:

- The script prints logs like:

```plaintext
[2025-06-25 18:30:00] Waiting 2.34 seconds...
Login Status: 200
Successfully changed to Medium mode
Fetching miner status...
Status saved to miner_status.json
```

- `miner_status.json` is created/updated with contents like:

```json
{
  "Mode": "Medium",
  "Summary": { ... },
  "Stats": { ... }
}
```

---

### 5. Run It Automatically on Boot (Optional)

Example using `cron`:

```bash
crontab -e
```

Add:

```bash
@reboot /usr/bin/python3 /path/to/miner_automation.py
```

Or use `tmux` / `screen` / `systemd` for a persistent session.

---

## File Structure Example

```
miner_automation.py
miner_status.json  <-- output file
README.md
```

---

## Advanced Configuration (Optional)

- Change the logging interval by modifying:

```python
schedule.every(10).minutes.do(fetch_and_log_cgminer)
```

- Change power modes anytime even multiple times per day by editing `weekly_schedule`.

---

## Notes

- This script **does NOT rely on the miner's web interface logs.**
- It uses the **native CGMiner API** via port `4028`.
- Ensure that port `4028` is open on your miner (most Canaan Avalon miners have it enabled by default).
- If the port is blocked, the script won't be able to fetch stats.

---

##  Future Improvements (Optional Ideas)

- Implement Nostr or Telegram notifications.
- Maybe even plot charts with hash rates and temperature trends.
- Add error recovery with retries and alerts.

---

## Credits

- Built for Avalon Miner users who are tired of waiting for Canaan devs to update nano3 home miners with scheduler.
- Designed to run efficiently on Raspberry Pi or any Linux machine.

---

## License

Free for personal use only.

---

## Support or Ideas?

Open an issue, suggest an idea, message me here or find me on [Nostr](https://njump.me/npub1qqqqqqz7nhdqz3uuwmzlflxt46lyu7zkuqhcapddhgz66c4ddynswreecw)!

---

## ⚡ Support This Project

If this project helps you, consider supporting development:

- **Bitcoin (On-chain):**  
  `bc1q2ytw4gwrkw5jg6ekutcwrgw8x5nlkahyk54l5e`

- **⚡ Lightning:**  
  `one@satoshi.si` -> (points to longer string le...19@walletofsatoshi.com)

Thank you! 🙏
