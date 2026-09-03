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
import base64
import json
import os
import re
import time
from datetime import datetime, timezone

import httpx


# =========================
# CONFIG
# =========================
BOT_TOKEN = "8852330034:AAG-VW3qO9EuaPMcf54dtD_fpiNkTOkfKYI"
GROUP_ID = -1004415108815

MAUTH_TOKEN = os.getenv("ZEBRA_MAUTH_TOKEN", "").strip()
CONSOLE_URL = "https://zebrasms.com/api/v1/console"

POLL_SECONDS = 5
REQUEST_TIMEOUT = 20

# If True, the first scan is only used as a baseline and is NOT posted.
# This prevents the group from being flooded with old/current console rows
# when the monitor starts.
SKIP_INITIAL_ANNOUNCEMENT = False


HEADERS = {
    "MAuth": MAUTH_TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/cbor, application/json, text/plain, */*",
}

RANGE_RE = re.compile(r"^\d+X+$")


class CborDecodeError(Exception):
    pass


def _cbor_uint(data, pos, additional):
    if additional < 24:
        return additional, pos
    nbytes = {24: 1, 25: 2, 26: 4, 27: 8}.get(additional)
    if nbytes is None or pos + nbytes > len(data):
        raise CborDecodeError("Unsupported/invalid CBOR integer")
    return int.from_bytes(data[pos:pos+nbytes], "big"), pos + nbytes


def _decode_cbor_one(data, pos=0):
    if pos >= len(data):
        raise CborDecodeError("Unexpected end of CBOR")
    initial = data[pos]
    pos += 1
    major = initial >> 5
    additional = initial & 31

    if major in (0, 1):
        value, pos = _cbor_uint(data, pos, additional)
        return (value if major == 0 else -1 - value), pos

    if major in (2, 3):
        length, pos = _cbor_uint(data, pos, additional)
        if pos + length > len(data):
            raise CborDecodeError("Truncated CBOR string")
        raw = data[pos:pos+length]
        pos += length
        return (raw if major == 2 else raw.decode("utf-8", errors="replace")), pos

    if major == 4:
        length, pos = _cbor_uint(data, pos, additional)
        arr = []
        for _ in range(length):
            value, pos = _decode_cbor_one(data, pos)
            arr.append(value)
        return arr, pos

    if major == 5:
        length, pos = _cbor_uint(data, pos, additional)
        obj = {}
        for _ in range(length):
            key, pos = _decode_cbor_one(data, pos)
            value, pos = _decode_cbor_one(data, pos)
            if isinstance(key, bytes):
                key = key.decode("utf-8", errors="replace")
            obj[key] = value
        return obj, pos

    if major == 7:
        if additional == 20:
            return False, pos
        if additional == 21:
            return True, pos
        if additional == 22:
            return None, pos
        if additional == 23:
            return None, pos
        if additional == 27:
            import struct
            if pos + 8 > len(data):
                raise CborDecodeError("Truncated CBOR float")
            return struct.unpack(">d", data[pos:pos+8])[0], pos + 8

    raise CborDecodeError(f"Unsupported CBOR major/additional: {major}/{additional}")


def decode_console_response(response):
    """Decode JSON or the CBOR response used by the Zebra Console."""
    raw = response.content
    content_type = response.headers.get("content-type", "").lower()

    # Some DevTools views expose CBOR as data:application/cbor;base64,...
    text = raw.decode("utf-8", errors="replace").strip()
    if text.startswith("data:application/cbor;base64,"):
        raw = base64.b64decode(text.split(",", 1)[1])
        content_type = "application/cbor"

    if "json" in content_type:
        return json.loads(raw.decode("utf-8"))

    if "cbor" in content_type or raw[:1] in (b"\x81", b"\x82", b"\x83", b"\x84", b"\x85", b"\x86", b"\x87", b"\x88", b"\x89", b"\x8a", b"\x8b", b"\x8c", b"\x8d", b"\x8e", b"\x8f", b"\xa1", b"\xa2", b"\xa3", b"\xa4", b"\xa5", b"\xa6", b"\xa7", b"\xa8", b"\xa9", b"\xaa", b"\xab", b"\xac", b"\xad", b"\xae", b"\xaf"):
        value, _ = _decode_cbor_one(raw)
        return value

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last chance: the body may still be a CBOR data URI.
        if text.startswith("data:") and ";base64," in text:
            raw = base64.b64decode(text.split(",", 1)[1])
            value, _ = _decode_cbor_one(raw)
            return value
        raise


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

    payload = decode_console_response(response)

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

    result = data.get("result") or {}
    chat = result.get("chat") or {}
    print(
        "[Telegram] API OK "
        f"message_id={result.get('message_id')} "
        f"chat_id={chat.get('id')} "
        f"chat_type={chat.get('type')} "
        f"chat_title={chat.get('title', '')!r}"
    )


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
    if not MAUTH_TOKEN:
        raise RuntimeError("Missing Railway variable: ZEBRA_MAUTH_TOKEN")

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
        # Verify the exact Telegram destination once at startup.
        try:
            me_resp = await client.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            )
            me_resp.raise_for_status()
            me_data = me_resp.json()
            me = me_data.get("result") or {}
            print(
                "[Telegram] Bot OK "
                f"username=@{me.get('username', '')} id={me.get('id')}"
            )

            chat_resp = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getChat",
                json={"chat_id": GROUP_ID},
            )
            chat_resp.raise_for_status()
            chat_data = chat_resp.json()
            if not chat_data.get("ok"):
                raise RuntimeError(f"Telegram getChat error: {chat_data}")

            chat = chat_data.get("result") or {}
            print(
                "[Telegram] Target chat OK "
                f"id={chat.get('id')} type={chat.get('type')} "
                f"title={chat.get('title', '')!r}"
            )
        except Exception as exc:
            print(f"[Telegram setup ERROR] {type(exc).__name__}: {exc}")

        while True:
            try:
                services = await fetch_console(client)
                current_ranges = flatten_ranges(services)

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"Console ranges: {sorted(current_ranges)}"
                )

                if first_scan:
                    first_scan = False
                    if current_ranges:
                        # Send the ranges that are visible in Console right now.
                        message = format_new_ranges(current_ranges, services)
                        await send_group_message(client, message)
                        print(f"[Telegram] Sent initial Console ranges: {sorted(current_ranges)}")
                    else:
                        print("[WARN] Console returned zero explicit masked ranges.")
                    seen_ranges = set(current_ranges)
                else:
                    new_ranges = current_ranges - seen_ranges

                    if new_ranges:
                        message = format_new_ranges(new_ranges, services)
                        await send_group_message(client, message)
                        print(f"[Telegram] Sent new ranges: {sorted(new_ranges)}")

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
