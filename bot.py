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


def mask_number(number):
    """Mask phone number for Telegram display."""

    if not number:
        return None

    number = str(number).strip()

    if len(number) <= 6:
        return "****"

    return number[:4] + "****" + number[-2:]


def update_signature(row):
    """
    Build a stable identifier for a getupdate row.

    IMPORTANT:
    We deliberately do NOT use the message/code field.
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
    """
    Call Zebra Developer API.

    Documentation specifies:
        MAuth: <API KEY>
    """

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

    # Zebra API uses meta.code rather than HTTP 200 alone.
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


async def fetch_live_ranges(client, sender=None):
    """
    Optional live range lookup.

    This only reads range metadata.
    """

    params = {}

    if sender:
        params["sender"] = sender

    payload = await zebra_get(
        client,
        LIVEACCESS_URL,
        params=params,
    )

    data = payload.get("data", {})

    if not isinstance(data, dict):
        return []

    rows = data.get("rows", [])

    if not isinstance(rows, list):
        return []

    return rows


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

async def send_update(client, row):
    """
    Send NON-SENSITIVE getupdate metadata.

    The API response may contain a 'message' field,
    but this function deliberately NEVER reads it.
    """

    if not isinstance(row, dict):
        return

    sender = row.get("sender")
    country = row.get("country")
    operator = row.get("operator")
    number = row.get("number")
    at_ms = row.get("at_ms")

    display_time = format_time(at_ms)
    display_number = mask_number(number)

    lines = [
        "🟢 NEW DELIVERY UPDATE",
        "",
        f"⏰ Time: {display_time}",
    ]

    if sender:
        lines.append(f"📨 Sender: {sender}")

    if display_number:
        lines.append(f"📱 Number: {display_number}")

    if country:
        lines.append(f"🌍 Country: {country}")

    if operator:
        lines.append(f"📡 Operator: {operator}")

    # Intentionally NO SMS/message/OTP content.

    text = "\n".join(lines)

    result = await telegram_call(
        client,
        "sendMessage",
        {
            "chat_id": GROUP_ID,
            "text": text,
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
        f"country={country!r} "
        f"operator={operator!r}"
    )


# =========================================================
# Startup
# =========================================================

async def startup_checks(client):
    """Check Telegram credentials and target group."""

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
    print(f"Group ID: {GROUP_ID}")
    print(f"Poll interval: {POLL_SECONDS}s")
    print("Format: JSON")
    print("OTP/SMS message content: NOT READ")
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

        seen_updates = set()

        while True:

            try:
                rows = await fetch_updates(client)

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"getupdate rows={len(rows)}"
                )

                new_rows = []

                for row in rows:

                    signature = update_signature(row)

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

            await asyncio.sleep(POLL_SECONDS)


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Stopped.")
