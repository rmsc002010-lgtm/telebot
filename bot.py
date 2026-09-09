#!/usr/bin/env python3

import asyncio
import os
import time
from datetime import datetime

import httpx


# =========================================================
# Railway Environment Variables
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROUP_ID_RAW = os.getenv("GROUP_ID", "-1004415108815").strip()
ZEBRA_MAUTH_TOKEN = os.getenv("ZEBRA_MAUTH_TOKEN", "").strip()

GROUP_ID = int(GROUP_ID_RAW)

# Telegram buttons
NUMBER_BOT_URL = "https://t.me/testjonson2_bot"
MAIN_CHANNEL_URL = "https://t.me/otpmastersgrp"

# Zebra Developer API
ZEBRA_BASE_URL = "https://api.zebrasms.com/api/v1"

GETUPDATE_URL = f"{ZEBRA_BASE_URL}/publicapi/getupdate"
LIVEACCESS_URL = f"{ZEBRA_BASE_URL}/publicapi/liveaccess"

POLL_SECONDS = 5
TIMEOUT_SECONDS = 20

# Refresh live ranges every 60 seconds
RANGE_CACHE_SECONDS = 60


# =========================================================
# Helpers
# =========================================================

def format_time(value):
    """Convert Zebra timestamp to readable local time."""

    if value in (None, ""):
        return datetime.now().strftime("%H:%M:%S")

    try:
        number = float(value)

        # milliseconds -> seconds
        if number > 10_000_000_000:
            number /= 1000

        return datetime.fromtimestamp(number).strftime("%H:%M:%S")

    except Exception:
        return str(value)


def full_number(number):
    """Return the full number for display."""

    if number in (None, ""):
        return None

    return str(number).strip()


def fallback_range(number, prefix_len=8):
    """
    Create range from the first 8 digits.

    Example:
        225015151234 -> 22501515XXX
    """

    if not number:
        return None

    number = str(number).strip()

    if len(number) < prefix_len:
        return None

    return number[:prefix_len] + "XXX"


def normalize_sender(sender):
    if sender in (None, ""):
        return ""

    return str(sender).strip().lower()


def normalize_range(value):
    if value in (None, ""):
        return None

    return str(value).strip()


def update_signature(row):
    """
    Build a stable identifier for a getupdate row.

    Message content is deliberately not used.
    """

    if not isinstance(row, dict):
        return None

    for key in (
        "id",
        "_id",
        "idx",
        "at_ms",
        "timestamp",
    ):
        value = row.get(key)

        if value not in (None, ""):
            return f"{key}:{value}"

    return "|".join(
        str(row.get(key, ""))
        for key in (
            "number",
            "sender",
            "country",
            "operator",
            "at_ms",
        )
    )


# =========================================================
# Zebra API
# =========================================================

async def zebra_get(client, url, params=None):
    """Call Zebra Developer API."""

    response = await client.get(
        url,
        params=params,
        headers={
            "MAuth": ZEBRA_MAUTH_TOKEN,
            "Accept": "application/json",
            "User-Agent": "ZebraSMS-Monitor/1.0",
        },
    )

    response.raise_for_status()

    payload = response.json()

    meta = payload.get("meta", {})

    code = meta.get("code")

    if code != 0:
        error_message = meta.get("error")

        raise RuntimeError(
            f"Zebra API error code={code} "
            f"error={error_message!r}"
        )

    return payload


async def fetch_updates(client):
    """Get recent delivered updates."""

    payload = await zebra_get(
        client,
        GETUPDATE_URL,
    )

    data = payload.get("data", {})

    if not isinstance(data, dict):
        return []

    rows = data.get("rows", [])

    if not isinstance(rows, list):
        return []

    return rows


async def fetch_live_ranges(client):
    """
    Get active sender/range metadata.

    Returns:
        {
            "sender": ["range1", "range2"]
        }
    """

    payload = await zebra_get(
        client,
        LIVEACCESS_URL,
    )

    data = payload.get("data", {})

    if not isinstance(data, dict):
        return {}

    rows = data.get("rows", [])

    if not isinstance(rows, list):
        return {}

    sender_ranges = {}

    for item in rows:

        if not isinstance(item, dict):
            continue

        sender = normalize_sender(
            item.get("sender")
        )

        if not sender:
            continue

        ranges = item.get("ranges", [])

        if not isinstance(ranges, list):
            ranges = []

        clean_ranges = []

        for value in ranges:

            value = normalize_range(value)

            if value and value not in clean_ranges:
                clean_ranges.append(value)

        sender_ranges[sender] = clean_ranges

    return sender_ranges


# =========================================================
# Telegram
# =========================================================

async def telegram_call(client, method, payload=None):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/{method}"
    )

    if payload is None:
        response = await client.get(url)
    else:
        response = await client.post(
            url,
            json=payload,
        )

    response.raise_for_status()

    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(
            f"Telegram {method} failed: {data}"
        )

    return data.get("result")


# =========================================================
# Telegram message
# =========================================================

async def send_update(
    client,
    row,
    sender_ranges,
):

    if not isinstance(row, dict):
        return

    sender = row.get("sender")
    country = row.get("country")
    operator = row.get("operator")
    number = row.get("number")
    at_ms = row.get("at_ms")

    display_time = format_time(at_ms)

    # FULL NUMBER
    display_number = full_number(number)

    # Sender based ranges from LIVEACCESS
    ranges = sender_ranges.get(
        normalize_sender(sender),
        [],
    )

    # If Zebra liveaccess has no matching range,
    # create a display range from first 8 digits.
    if not ranges:
        fallback = fallback_range(
            display_number,
            prefix_len=8,
        )

        if fallback:
            ranges = [fallback]

    lines = [
        "🟢 New Active Range",
        "",
    ]

    if sender:
        lines.append(
            f"⚙️ Service: {sender}"
        )

    if country:
        lines.append(
            f"🌍 Country: {country}"
        )

    if display_number:
        lines.append(
            f"📱 Number: `{display_number}`"
        )

    if ranges:

        lines.append("📊 Range:")

        for range_value in ranges:
            lines.append(
                f"`{range_value}`"
            )

    if operator:
        lines.append(
            f"📡 Operator: {operator}"
        )

    lines.extend([
        "",
        "📩 Full SMS ⤵️⤵️",
        "🔐 Message content hidden",
        "",
        f"⏰ Time: {display_time}",
    ])

    text = "\n".join(lines)

    result = await telegram_call(
        client,
        "sendMessage",
        {
            "chat_id": GROUP_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "🤖 Number Bot",
                            "url": NUMBER_BOT_URL,
                        },
                        {
                            "text": "📢 Main Channel",
                            "url": MAIN_CHANNEL_URL,
                        },
                    ]
                ]
            },
        },
    )

    message_id = (
        result.get("message_id")
        if isinstance(result, dict)
        else None
    )

    print(
        "[Telegram] sent "
        f"message_id={message_id} "
        f"sender={sender!r} "
        f"number={display_number!r} "
        f"ranges={ranges!r}"
    )


# =========================================================
# Startup
# =========================================================

async def startup_checks(client):

    me = await telegram_call(
        client,
        "getMe",
    )

    print(
        f"[Telegram] Bot: "
        f"@{me.get('username')} "
        f"id={me.get('id')}"
    )

    chat = await telegram_call(
        client,
        "getChat",
        {
            "chat_id": GROUP_ID,
        },
    )

    print(
        f"[Telegram] Group: "
        f"id={chat.get('id')} "
        f"type={chat.get('type')} "
        f"title={chat.get('title', '')!r}"
    )


# =========================================================
# Main
# =========================================================

async def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "Missing Railway variable: BOT_TOKEN"
        )

    if not ZEBRA_MAUTH_TOKEN:
        raise RuntimeError(
            "Missing Railway variable: ZEBRA_MAUTH_TOKEN"
        )

    print("=" * 60)
    print("Zebra SMS Developer API Monitor")
    print("=" * 60)

    print(f"API: {ZEBRA_BASE_URL}")
    print(f"GetUpdate: {GETUPDATE_URL}")
    print(f"LiveAccess: {LIVEACCESS_URL}")
    print(f"Group ID: {GROUP_ID}")
    print(f"Poll interval: {POLL_SECONDS}s")
    print("Range prefix: 8 digits + XXX")
    print("Message content: NOT READ")
    print("=" * 60)

    timeout = httpx.Timeout(
        connect=10,
        read=TIMEOUT_SECONDS,
        write=10,
        pool=10,
    )

    limits = httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
    ) as client:

        await startup_checks(client)

        # -------------------------------------------------
        # Initial live ranges
        # -------------------------------------------------

        sender_ranges = {}

        try:

            sender_ranges = await fetch_live_ranges(
                client
            )

            print(
                "[Zebra] Live ranges loaded: "
                f"{len(sender_ranges)} senders"
            )

        except Exception as exc:

            print(
                "[Zebra RANGE ERROR] "
                f"{type(exc).__name__}: {exc}"
            )

        last_range_refresh = time.monotonic()

        seen_updates = set()

        while True:

            try:

                # -----------------------------------------
                # Refresh live ranges every 60 seconds
                # -----------------------------------------

                now = time.monotonic()

                if (
                    now - last_range_refresh
                    >= RANGE_CACHE_SECONDS
                ):

                    try:

                        sender_ranges = (
                            await fetch_live_ranges(
                                client
                            )
                        )

                        last_range_refresh = now

                        print(
                            "[Zebra] Live ranges refreshed: "
                            f"{len(sender_ranges)} senders"
                        )

                    except Exception as exc:

                        print(
                            "[Zebra RANGE ERROR] "
                            f"{type(exc).__name__}: {exc}"
                        )

                # -----------------------------------------
                # Get updates
                # -----------------------------------------

                rows = await fetch_updates(
                    client
                )

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"getupdate rows={len(rows)}"
                )

                new_rows = []

                for row in rows:

                    signature = update_signature(
                        row
                    )

                    if not signature:
                        continue

                    if signature in seen_updates:
                        continue

                    seen_updates.add(signature)

                    new_rows.append(row)

                # Keep memory bounded.
                if len(seen_updates) > 5000:

                    seen_updates = set(
                        list(seen_updates)[-2500:]
                    )

                # Oldest -> newest
                for row in reversed(new_rows):

                    try:

                        await send_update(
                            client,
                            row,
                            sender_ranges,
                        )

                    except Exception as exc:

                        print(
                            "[Telegram ERROR] "
                            f"{type(exc).__name__}: {exc}"
                        )

            except httpx.HTTPStatusError as exc:

                print(
                    "[HTTP ERROR] "
                    f"status={exc.response.status_code} "
                    f"url={exc.request.url}"
                )

            except Exception as exc:

                print(
                    "[ERROR] "
                    f"{type(exc).__name__}: {exc}"
                )

            await asyncio.sleep(
                POLL_SECONDS
            )


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("Stopped.")
