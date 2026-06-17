#!/usr/bin/env python3
"""
Daily Discord stats reporter for a running probe service.
Runs on the EC2/VPS where the probe is deployed.
Cron: 0 8 * * * /usr/bin/python3 /home/ubuntu/probe_report.py >> /home/ubuntu/stats.log 2>&1
"""

import subprocess, re, json, urllib.request, urllib.error
from datetime import datetime, timezone

WEBHOOK  = "https://discord.com/api/webhooks/[WEBHOOK_ID]/[WEBHOOK_TOKEN]"
LOG_FILE = "/home/ubuntu/probe.log"   # path to your probe's stdout log
SERVICE  = "probe"                    # systemd service name (e.g. "sherin-probe")


def service_status() -> str:
    r = subprocess.run(["systemctl", "is-active", SERVICE], capture_output=True, text=True)
    return r.stdout.strip()


def process_info() -> tuple[str, str, str, str]:
    r = subprocess.run(
        ["systemctl", "show", SERVICE,
         "--property=MainPID,ExecMainStartTimestamp"],
        capture_output=True, text=True
    )
    info = dict(line.split("=", 1) for line in r.stdout.strip().splitlines() if "=" in line)
    pid = info.get("MainPID", "0")
    cpu = ram = uptime = "N/A"
    if pid and pid != "0":
        try:
            with open(f"/proc/{pid}/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        ram = f"{int(line.split()[1]) // 1024} MB"
                        break
            ps = subprocess.run(["ps", "-p", pid, "-o", "pcpu="], capture_output=True, text=True)
            cpu = ps.stdout.strip() + "%"
        except Exception:
            pass
    ts = info.get("ExecMainStartTimestamp", "")
    m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", ts)
    if m:
        start = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        d = datetime.now(timezone.utc) - start
        h, rem = divmod(int(d.total_seconds()), 3600)
        uptime = f"{h}h {rem // 60}min"
    return pid, cpu, ram, uptime


def parse_log() -> tuple[int, int, int, int, int, float]:
    success = csrf = rejected = 0
    try:
        r = subprocess.run(["grep", "-Fc", "[+] SUCCESS", LOG_FILE], capture_output=True, text=True)
        success = int(r.stdout.strip()) if r.returncode == 0 else 0
    except Exception:
        pass
    try:
        r2 = subprocess.run(["grep", "-cP", r"status.*419|419.*status", LOG_FILE], capture_output=True, text=True)
        csrf = int(r2.stdout.strip()) if r2.returncode == 0 else 0
    except Exception:
        pass
    try:
        r3 = subprocess.run(["grep", "-cP", r"status.*429|429.*status", LOG_FILE], capture_output=True, text=True)
        rejected = int(r3.stdout.strip()) if r3.returncode == 0 else 0
    except Exception:
        pass
    try:
        r4 = subprocess.run(["grep", "-cP", r"^\[\d+\]", LOG_FILE], capture_output=True, text=True)
        total = int(r4.stdout.strip()) if r4.returncode == 0 else (success + csrf + rejected)
    except Exception:
        total = success + csrf + rejected
    other = max(0, total - success - csrf - rejected)
    rate = (success / total * 100) if total > 0 else 0
    return total, success, rejected, csrf, other, rate


def send_webhook(payload: dict) -> int:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        WEBHOOK, data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (https://discord.com, 10)",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        print(f"  Discord error: {e.read().decode()}")
        return e.code


def main():
    status = service_status()
    pid, cpu, ram, uptime = process_info()
    total, success, rejected, csrf, errors, rate = parse_log()
    running = (status == "active")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    proc_block = (
        f"PID    : {pid}\n"
        f"CPU    : {cpu}\n"
        f"RAM    : {ram}\n"
        f"Uptime : {uptime}"
    )
    stats_block = (
        f"Total attempts : {total:,}\n"
        f"SUCCESS        : {success:,}  OK\n"
        f"Rejected (429) : {rejected:,}  zero rate limiting\n"
        f"CSRF 419       : {csrf:,}\n"
        f"Other/errors   : {errors:,}\n"
        f"{'='*32}\n"
        f"Success rate   : {rate:.1f}%"
    )

    title = ("RUNNING" if running else "STOPPED") + " -- Probe Daily Report"
    desc  = f"Service: {SERVICE}.service | Status: {'RUNNING' if running else 'STOPPED'}"

    embed = {
        "title": title,
        "description": desc,
        "color": 0x00cc44 if running else 0xff3333,
        "fields": [
            {"name": "Process Info",       "value": f"```\n{proc_block}\n```", "inline": False},
            {"name": "Registration Stats", "value": f"```\n{stats_block}\n```", "inline": False},
        ],
        "footer": {"text": f"Daily 8:00 AM UTC | {now}"},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    code = send_webhook({"embeds": [embed]})
    print(f"[{now}] Discord HTTP {code} | total={total:,} success={success:,} rate={rate:.1f}%")


if __name__ == "__main__":
    main()
