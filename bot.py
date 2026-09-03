#!/usr/bin/env python3
"""
Zebra SMS Console Range Monitor

Purpose:
- Reads ONLY the Zebra SMS /console feed.
- Extracts only explicit masked ranges such as 26134XXX.
- Sends NEWLY detected ranges to a Telegram group.
- Does NOT read /liveaccess.
- Does NOT read OTP/SMS messages or phone numbers.
- Does NOT generate or modify ranges.
- Uses Telegram Bot API sendMessage only, so it can run beside the main bot
  even though it uses the same bot token.

Install:
    pip install httpx

Run:
    python console_range_monitor.py
"""

import asyncio
import re
import time
from datetime import datetime, timezone

import httpx


# =========================
# CONFIG
# =========================
BOT_TOKEN = "8852330034:AAG-VW3qO9EuaPMcf54dtD_fpiNkTOkfKYI"
GROUP_ID = -1004415108815

PRIMARY_API_KEY = "6U3G3DDZ6GB"
CONSOLE_URL = "https://zebrasms.com/api/v1/console"

POLL_SECONDS = 5
REQUEST_TIMEOUT = 20

# If True, the first scan is only used as a baseline and is NOT posted.
# This prevents the group from being flooded with old/current console rows
# when the monitor starts.
SKIP_INITIAL_ANNOUNCEMENT = True


HEADERS = {
    "MAuth": PRIMARY_API_KEY,
    "Content-Type": "application/json",
}

RANGE_RE = re.compile(r"^\d+X+$")


def first_value(obj, keys):
    """Get the first non-empty value from a dictionary."""
    if not isinstance(obj, dict):
        return None

    for key in keys:
        value = obj.get(key)
        if value not in (None, "", [], {}):
            if isinstance(value, dict):
                nested = first_value(
                    value,
                    ("name", "id", "sid", "service", "platform", "value"),
                )
                if nested not in (None, ""):
                    return nested
            else:
                return value

    return None


def walk_console_records(obj):
    """
    Recursively find objects that contain an explicit range field.

    Important:
    We NEVER create a range from a number. The range must already exist
    explicitly in the Console response.
    """
    if isinstance(obj, list):
        for item in obj:
            yield from walk_console_records(item)

    elif isinstance(obj, dict):
        raw_range = first_value(
            obj,
            ("range", "range_id", "rangeId", "rid"),
        )

        if raw_range not in (None, ""):
            yield obj

        for value in obj.values():
            if isinstance(value, (dict, list)):
                yield from walk_console_records(value)


def extract_console_ranges(payload):
    """
    Return:
        {
            "Facebook": {"26134XXX", "26136XXX"},
            "Discord": {"26138XXX"}
        }

    Only explicit masked ranges present in /console are accepted.
    """
    # Zebra's Console response is structured as data.rows.
    records = []
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            records = data["rows"]
        elif isinstance(data, list):
            records = data
        else:
            root = data if data is not None else payload
            if isinstance(root, dict):
                for key in ("rows", "items", "hits", "logs", "records", "results", "console"):
                    value = root.get(key)
                    if isinstance(value, list):
                        records = value
                        break
                if not records:
                    records = [root]
            elif isinstance(root, list):
                records = root
    elif isinstance(payload, list):
        records = payload

    services = {}

    for record in walk_console_records(records):
        raw_range = first_value(
            record,
            ("range", "range_id", "rangeId", "rid"),
        )

        if raw_range is None:
            continue

        range_text = str(raw_range).strip().upper()

        # Strict: the API must explicitly provide a masked range.
        if not RANGE_RE.fullmatch(range_text):
            continue

        service = first_value(
            record,
            (
                "service",
                "service_name",
                "serviceName",
                "sid",
                "app",
                "application",
                "platform",
            ),
        )

        if isinstance(service, dict):
            service = first_value(
                service,
                ("name", "id", "sid", "service", "platform"),
            )

        service_text = str(service).strip() if service else "Console"

        services.setdefault(service_text, set()).add(range_text)

    return services


async def fetch_console(client):
    response = await client.get(CONSOLE_URL, headers=HEADERS)
    response.raise_for_status()

    payload = response.json()

    if isinstance(payload, dict):
        meta = payload.get("meta")
        if isinstance(meta, dict):
            code = meta.get("code")
            if code not in (None, 0, 200):
                raise RuntimeError(f"Console API returned meta.code={code}")

    return extract_console_ranges(payload)


def flatten_ranges(services):
    """Convert service->ranges to a single set of range strings."""
    result = set()
    for ranges in services.values():
        result.update(ranges)
    return result


async def send_group_message(client, text):
    """
    Uses Telegram Bot API directly.
    No polling/webhook is used, so this process can share the same token
    with the main bot as long as this monitor only sends messages.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = await client.post(
        url,
        json={
            "chat_id": GROUP_ID,
            "text": text,
            "disable_web_page_preview": True,
        },
    )
    response.raise_for_status()

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")


def format_new_ranges(new_ranges, services):
    """
    Build a compact notification containing only ranges newly seen in
    the current Console snapshot.
    """
    service_map = {}
    for service, ranges in services.items():
        for range_text in ranges:
            service_map.setdefault(range_text, []).append(service)

    lines = ["🦓 ZEBRA SMS — NEW CONSOLE RANGE", ""]

    for range_text in sorted(new_ranges):
        service_names = ", ".join(sorted(service_map.get(range_text, ["Console"])))
        lines.append(f"📌 {range_text}")
        lines.append(f"🛠 {service_names}")

    now = datetime.now().strftime("%H:%M:%S")
    lines.append("")
    lines.append(f"🕐 Detected: {now}")

    return "\n".join(lines)


async def main():
    print("Zebra SMS Console Range Monitor started.")
    print(f"Console: {CONSOLE_URL}")
    print(f"Group ID: {GROUP_ID}")
    print(f"Poll interval: {POLL_SECONDS}s")
    print("Source: ONLY /console")
    print("OTP/SMS content: NOT USED")

    seen_ranges = set()
    first_scan = True

    limits = httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5,
    )

    timeout = httpx.Timeout(
        connect=10,
        read=REQUEST_TIMEOUT,
        write=10,
        pool=10,
    )

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        while True:
            try:
                services = await fetch_console(client)
                current_ranges = flatten_ranges(services)

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"Console ranges: {sorted(current_ranges)}"
                )

                if first_scan and SKIP_INITIAL_ANNOUNCEMENT:
                    seen_ranges = set(current_ranges)
                    first_scan = False

                else:
                    first_scan = False
                    new_ranges = current_ranges - seen_ranges

                    if new_ranges:
                        message = format_new_ranges(new_ranges, services)
                        await send_group_message(client, message)

                        print(
                            f"[Telegram] Sent new ranges: "
                            f"{sorted(new_ranges)}"
                        )

                    # Keep the snapshot synchronized with Console.
                    seen_ranges = set(current_ranges)

            except Exception as exc:
                print(f"[ERROR] {type(exc).__name__}: {exc}")

            await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
