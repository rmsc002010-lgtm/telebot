#!/usr/bin/env python3

import asyncio
import os
import time
from datetime import datetime

import httpx


# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROUP_ID = int(
    os.getenv("GROUP_ID", "-1004415108815").strip()
)
ZEBRA_MAUTH_TOKEN = os.getenv(
    "ZEBRA_MAUTH_TOKEN", ""
).strip()

NUMBER_BOT_URL = "https://t.me/testjonson2_bot"
MAIN_CHANNEL_URL = "https://t.me/otpmastersgrp"

ZEBRA_BASE_URL = "https://api.zebrasms.com/api/v1"

GETUPDATE_URL = (
    f"{ZEBRA_BASE_URL}/publicapi/getupdate"
)

LIVEACCESS_URL = (
    f"{ZEBRA_BASE_URL}/publicapi/liveaccess"
)

POLL_SECONDS = 5
TIMEOUT_SECONDS = 20
RANGE_REFRESH_SECONDS = 60
MAX_SEEN = 5000


# =========================================================
# HELPERS
# =========================================================

def format_time(value):

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


def clean_number(value):

    if value in (None, ""):
        return ""

    return str(value).strip()


def digits_only(value):

    if value in (None, ""):
        return ""

    return "".join(
        ch for ch in str(value)
        if ch.isdigit()
    )


def normalize_range(value):

    if value in (None, ""):
        return ""

    value = str(value).strip().upper()

    result = []

    for ch in value:

        if ch.isdigit() or ch == "X":
            result.append(ch)

    return "".join(result)


def fallback_range(number):

    number = digits_only(number)

    if len(number) < 8:
        return None

    return number[:8] + "XXX"


# =========================================================
# IMPORTANT:
# NEW UPDATE DETECTION
# =========================================================

def get_row_identifier(row):

    """
    Create a stable identifier without reading SMS/message.

    We prefer Zebra's own ID fields.

    If unavailable, use all available delivery metadata.
    """

    if not isinstance(row, dict):
        return None

    # -----------------------------------------
    # Prefer unique API identifiers
    # -----------------------------------------

    for key in (
        "id",
        "_id",
        "idx",
        "uuid",
        "message_id",
        "update_id",
        "delivery_id",
    ):

        value = row.get(key)

        if value not in (None, ""):

            return (
                f"ID|{key}|{value}"
            )

    # -----------------------------------------
    # Timestamp-based identifier
    # -----------------------------------------

    at_ms = row.get("at_ms")

    if at_ms not in (None, ""):

        return "|".join([
            "TIME",
            str(at_ms),
            str(row.get("number", "")),
            str(row.get("sender", "")),
            str(row.get("country", "")),
            str(row.get("operator", "")),
        ])

    # -----------------------------------------
    # Timestamp alternatives
    # -----------------------------------------

    for key in (
        "timestamp",
        "created_at",
        "createdAt",
        "time",
    ):

        value = row.get(key)

        if value not in (None, ""):

            return "|".join([
                "TIME",
                key,
                str(value),
                str(row.get("number", "")),
                str(row.get("sender", "")),
            ])

    # -----------------------------------------
    # Last-resort metadata signature
    # -----------------------------------------

    return "|".join([
        "META",
        str(row.get("number", "")),
        str(row.get("sender", "")),
        str(row.get("country", "")),
        str(row.get("operator", "")),
    ])


def debug_row_fields(row):

    """
    Print ONLY field names and safe metadata.
    Never prints message/SMS content.
    """

    if not isinstance(row, dict):
        return

    safe_fields = {}

    for key, value in row.items():

        if key.lower() in {
            "message",
            "sms",
            "text",
            "body",
            "code",
            "otp",
        }:
            continue

        safe_fields[key] = value

    print(
        "[DEBUG] Row metadata:",
        safe_fields
    )


# =========================================================
# RANGE MATCHING
# =========================================================

def range_matches_number(
    range_value,
    number,
):

    range_value = normalize_range(
        range_value
    )

    number = digits_only(
        number
    )

    if not range_value or not number:
        return False

    prefix = range_value.split(
        "X",
        1
    )[0]

    if not prefix:
        return False

    return number.startswith(prefix)


def find_matching_range(
    active_ranges,
    number,
):

    matches = []

    for value in active_ranges:

        value = normalize_range(value)

        if not value:
            continue

        if range_matches_number(
            value,
            number,
        ):

            if value not in matches:
                matches.append(value)

    if matches:
        return matches[0]

    return fallback_range(number)


# =========================================================
# ZEBRA API
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
            "User-Agent": "ZebraSMS-Monitor/1.1",
        },
    )

    response.raise_for_status()

    payload = response.json()

    meta = payload.get(
        "meta",
        {}
    )

    if meta.get("code") != 0:

        raise RuntimeError(
            "Zebra API error "
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
        {}
    )

    if not isinstance(data, dict):
        return []

    rows = data.get(
        "rows",
        []
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
        {}
    )

    if not isinstance(data, dict):
        return []

    rows = data.get(
        "rows",
        []
    )

    if not isinstance(rows, list):
        return []

    all_ranges = []

    for item in rows:

        if not isinstance(item, dict):
            continue

        ranges = item.get(
            "ranges",
            []
        )

        if not isinstance(ranges, list):
            continue

        for value in ranges:

            value = normalize_range(value)

            if (
                value
                and value not in all_ranges
            ):
                all_ranges.append(value)

    return all_ranges


# =========================================================
# TELEGRAM
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
# SEND UPDATE
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

    display_range = find_matching_range(
        active_ranges,
        display_number,
    )

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

    if display_range:

        lines.append(
            f"📊 Range: `{display_range}`"
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
        f"⏰ Time: {format_time(at_ms)}",
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
        f"range={display_range!r}"
    )


# =========================================================
# STARTUP
# =========================================================

async def startup_checks(client):

    me = await telegram_call(
        client,
        "getMe"
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
            "chat_id": GROUP_ID
        }
    )

    print(
        f"[Telegram] Group: "
        f"id={chat.get('id')} "
        f"type={chat.get('type')} "
        f"title={chat.get('title', '')!r}"
    )


# =========================================================
# MAIN
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

        await startup_checks(
            client
        )

        # -----------------------------------------
        # Load ranges
        # -----------------------------------------

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

            active_ranges = []

        last_range_refresh = (
            time.monotonic()
        )

        # -----------------------------------------
        # Initial rows
        #
        # Mark existing rows as seen.
        # Do NOT send them.
        # -----------------------------------------

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
                get_row_identifier(row)
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

        # -----------------------------------------
        # Polling
        # -----------------------------------------

        while True:

            try:

                # ---------------------------------
                # Refresh ranges
                # ---------------------------------

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

                # ---------------------------------
                # Fetch updates
                # ---------------------------------

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
                        get_row_identifier(row)
                    )

                    if not signature:
                        continue

                    if signature in seen_updates:
                        continue

                    # New update found
                    seen_updates.add(
                        signature
                    )

                    print(
                        "[NEW UPDATE] "
                        f"{signature}"
                    )

                    # Print safe fields once
                    debug_row_fields(
                        row
                    )

                    new_rows.append(
                        row
                    )

                # ---------------------------------
                # Memory limit
                # ---------------------------------

                if len(seen_updates) > MAX_SEEN:

                    seen_updates = set(
                        list(seen_updates)[
                            -2500:
                        ]
                    )

                # ---------------------------------
                # Send new updates
                # ---------------------------------

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
# ENTRY POINT
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
