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


# =========================================================
# Telegram
# =========================================================

NUMBER_BOT_URL = "https://t.me/testjonson2_bot"
MAIN_CHANNEL_URL = "https://t.me/otpmastersgrp"


# =========================================================
# Zebra Developer API
# =========================================================

ZEBRA_BASE_URL = "https://api.zebrasms.com/api/v1"

GETUPDATE_URL = (
    f"{ZEBRA_BASE_URL}/publicapi/getupdate"
)

LIVEACCESS_URL = (
    f"{ZEBRA_BASE_URL}/publicapi/liveaccess"
)


# =========================================================
# Settings
# =========================================================

POLL_SECONDS = 5
TIMEOUT_SECONDS = 20

# liveaccess refresh interval
RANGE_REFRESH_SECONDS = 60

# Keep this many signatures in memory
MAX_SEEN = 5000


# =========================================================
# Helpers
# =========================================================

def format_time(value):
    """Convert Zebra timestamp to readable local time."""

    if value in (None, ""):
        return datetime.now().strftime("%H:%M:%S")

    try:
        number = float(value)

        if number > 10_000_000_000:
            number /= 1000

        return datetime.fromtimestamp(number).strftime(
            "%H:%M:%S"
        )

    except Exception:
        return str(value)


def clean_number(number):
    """Return full phone number."""

    if number in (None, ""):
        return None

    return str(number).strip()


def normalize_number(number):
    """
    Normalize a phone number for matching.

    Keeps digits only.

    Example:
        +261388755361 -> 261388755361
    """

    if number in (None, ""):
        return ""

    return "".join(
        ch for ch in str(number)
        if ch.isdigit()
    )


def normalize_range(value):
    """
    Normalize range for matching.

    Keeps digits and XXX.

    Example:
        26138XXX -> 26138XXX
        +26138XXX -> 26138XXX
    """

    if value in (None, ""):
        return ""

    value = str(value).strip().upper()

    result = []

    for ch in value:

        if ch.isdigit():
            result.append(ch)

        elif ch == "X":
            result.append("X")

    return "".join(result)


def range_matches_number(
    range_value,
    number,
):
    """
    Check whether a range matches a number.

    Example:
        Range 26138XXX
        Number +261388755361

        => True
    """

    normalized_range = normalize_range(
        range_value
    )

    normalized_number = normalize_number(
        number
    )

    if not normalized_range:
        return False

    if not normalized_number:
        return False

    # Convert range prefix before XXX
    prefix = normalized_range.split("X", 1)[0]

    if not prefix:
        return False

    return normalized_number.startswith(prefix)


def fallback_range(
    number,
    prefix_len=8,
):
    """
    Create fallback range.

    Example:
        +225015151234
        -> 22501515XXX
    """

    normalized = normalize_number(number)

    if len(normalized) < prefix_len:
        return None

    return normalized[:prefix_len] + "XXX"


def find_matching_ranges(
    ranges,
    number,
):
    """
    Return ONLY ranges matching this number.
    """

    if not isinstance(ranges, list):
        return []

    matches = []

    for value in ranges:

        value = normalize_range(value)

        if not value:
            continue

        if range_matches_number(
            value,
            number,
        ):
            if value not in matches:
                matches.append(value)

    return matches


def update_signature(row):
    """
    Stable identifier for a getupdate row.

    Message content is deliberately NOT used.
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

async def zebra_get(
    client,
    url,
    params=None,
):

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

    meta = payload.get(
        "meta",
        {},
    )

    if meta.get("code") != 0:

        raise RuntimeError(
            "Zebra API error: "
            f"code={meta.get('code')} "
            f"error={meta.get('error')!r}"
        )

    return payload


async def fetch_updates(client):

    payload = await zebra_get(
        client,
        GETUPDATE_URL,
    )

    data = payload.get(
        "data",
        {},
    )

    if not isinstance(data, dict):
        return []

    rows = data.get(
        "rows",
        [],
    )

    if not isinstance(rows, list):
        return []

    return rows


async def fetch_live_ranges(client):

    payload = await zebra_get(
        client,
        LIVEACCESS_URL,
    )

    data = payload.get(
        "data",
        {},
    )

    if not isinstance(data, dict):
        return {}

    rows = data.get(
        "rows",
        [],
    )

    if not isinstance(rows, list):
        return {}

    all_ranges = []

    for item in rows:

        if not isinstance(item, dict):
            continue

        ranges = item.get(
            "ranges",
            [],
        )

        if not isinstance(ranges, list):
            continue

        for value in ranges:

            value = normalize_range(value)

            if value and value not in all_ranges:
                all_ranges.append(value)

    return all_ranges


# =========================================================
# Telegram API
# =========================================================

async def telegram_call(
    client,
    method,
    payload=None,
):

    url = (
        "https://api.telegram.org/"
        f"bot{BOT_TOKEN}/{method}"
    )

    if payload is None:

        response = await client.get(
            url
        )

    else:

        response = await client.post(
            url,
            json=payload,
        )

    response.raise_for_status()

    data = response.json()

    if not data.get("ok"):

        raise RuntimeError(
            f"Telegram {method} failed: "
            f"{data}"
        )

    return data.get("result")


# =========================================================
# Telegram Message
# =========================================================

async def send_update(
    client,
    row,
    active_ranges,
):

    if not isinstance(row, dict):
        return

    sender = row.get(
        "sender"
    )

    country = row.get(
        "country"
    )

    operator = row.get(
        "operator"
    )

    number = row.get(
        "number"
    )

    at_ms = row.get(
        "at_ms"
    )

    display_number = clean_number(
        number
    )

    display_time = format_time(
        at_ms
    )

    # -----------------------------------------------------
    # Find ONLY matching range
    # -----------------------------------------------------

    matching_ranges = find_matching_ranges(
        active_ranges,
        display_number,
    )

    # -----------------------------------------------------
    # Fallback if liveaccess doesn't have matching range
    # -----------------------------------------------------

    if not matching_ranges:

        fallback = fallback_range(
            display_number,
            prefix_len=8,
        )

        if fallback:
            matching_ranges = [
                fallback
            ]

    # -----------------------------------------------------
    # Build message
    # -----------------------------------------------------

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

    if matching_ranges:

        # Normally only one matching range
        # should exist for a number.

        lines.append(
            f"📊 Range: "
            f"`{matching_ranges[0]}`"
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

    text = "\n".join(
        lines
    )

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

    message_id = None

    if isinstance(result, dict):

        message_id = result.get(
            "message_id"
        )

    print(
        "[Telegram] sent "
        f"message_id={message_id} "
        f"sender={sender!r} "
        f"number={display_number!r} "
        f"range={matching_ranges[0] if matching_ranges else None!r}"
    )


# =========================================================
# Startup Checks
# =========================================================

async def startup_checks(client):

    me = await telegram_call(
        client,
        "getMe",
    )

    print(
        "[Telegram] Bot: "
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
        "[Telegram] Group: "
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
            "Missing Railway variable: "
            "ZEBRA_MAUTH_TOKEN"
        )

    print("=" * 60)
    print(
        "Zebra SMS Developer API Monitor"
    )
    print("=" * 60)

    print(
        f"API: {ZEBRA_BASE_URL}"
    )

    print(
        f"GetUpdate: {GETUPDATE_URL}"
    )

    print(
        f"LiveAccess: {LIVEACCESS_URL}"
    )

    print(
        f"Group ID: {GROUP_ID}"
    )

    print(
        f"Poll interval: {POLL_SECONDS}s"
    )

    print(
        "Range matching: ENABLED"
    )

    print(
        "Startup old updates: SKIP"
    )

    print(
        "Message content: NOT READ"
    )

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

        # -------------------------------------------------
        # Telegram checks
        # -------------------------------------------------

        await startup_checks(
            client
        )

        # -------------------------------------------------
        # Load current active ranges
        # -------------------------------------------------

        active_ranges = []

        try:

            active_ranges = (
                await fetch_live_ranges(
                    client
                )
            )

            print(
                "[Zebra] Active ranges loaded: "
                f"{len(active_ranges)}"
            )

        except Exception as exc:

            print(
                "[RANGE ERROR] "
                f"{type(exc).__name__}: {exc}"
            )

        last_range_refresh = (
            time.monotonic()
        )

        # -------------------------------------------------
        # IMPORTANT:
        #
        # First getupdate call contains old rows.
        # Mark them as seen but DO NOT send them.
        # -------------------------------------------------

        print(
            "[Zebra] Loading existing updates..."
        )

        try:

            initial_rows = (
                await fetch_updates(
                    client
                )
            )

        except Exception as exc:

            print(
                "[STARTUP ERROR] "
                f"{type(exc).__name__}: {exc}"
            )

            initial_rows = []

        seen_updates = set()

        for row in initial_rows:

            signature = (
                update_signature(row)
            )

            if signature:

                seen_updates.add(
                    signature
                )

        print(
            "[Zebra] Existing updates marked: "
            f"{len(seen_updates)}"
        )

        print(
            "[Zebra] Waiting for NEW deliveries..."
        )

        # -------------------------------------------------
        # Main polling loop
        # -------------------------------------------------

        while True:

            try:

                # -----------------------------------------
                # Refresh active ranges
                # -----------------------------------------

                now = time.monotonic()

                if (
                    now - last_range_refresh
                    >= RANGE_REFRESH_SECONDS
                ):

                    try:

                        active_ranges = (
                            await fetch_live_ranges(
                                client
                            )
                        )

                        last_range_refresh = now

                        print(
                            "[Zebra] Active ranges "
                            "refreshed: "
                            f"{len(active_ranges)}"
                        )

                    except Exception as exc:

                        print(
                            "[RANGE ERROR] "
                            f"{type(exc).__name__}: "
                            f"{exc}"
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

                    signature = (
                        update_signature(row)
                    )

                    if not signature:
                        continue

                    if signature in seen_updates:
                        continue

                    seen_updates.add(
                        signature
                    )

                    new_rows.append(
                        row
                    )

                # -----------------------------------------
                # Keep memory bounded
                # -----------------------------------------

                if len(seen_updates) > MAX_SEEN:

                    seen_updates = set(
                        list(seen_updates)[
                            -2500:
                        ]
                    )

                # -----------------------------------------
                # Send only NEW rows
                # -----------------------------------------

                for row in reversed(
                    new_rows
                ):

                    try:

                        await send_update(
                            client,
                            row,
                            active_ranges,
                        )

                    except Exception as exc:

                        print(
                            "[Telegram ERROR] "
                            f"{type(exc).__name__}: "
                            f"{exc}"
                        )

            except httpx.HTTPStatusError as exc:

                print(
                    "[HTTP ERROR] "
                    f"status="
                    f"{exc.response.status_code} "
                    f"url={exc.request.url}"
                )

            except Exception as exc:

                print(
                    "[ERROR] "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

            await asyncio.sleep(
                POLL_SECONDS
            )


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "Stopped."
        )
