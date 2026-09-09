#!/usr/bin/env python3

import asyncio
import hashlib
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
    "ZEBRA_MAUTH_TOKEN",
    ""
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
# SECURITY
# =========================================================

SENSITIVE_FIELDS = {
    "message",
    "sms",
    "text",
    "body",
    "content",
    "code",
    "otp",
    "verification_code",
}


# =========================================================
# BASIC HELPERS
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
# SAFE METADATA
# =========================================================

def get_safe_metadata(row):

    if not isinstance(row, dict):
        return {}

    safe = {}

    for key, value in row.items():

        key_lower = str(key).lower()

        if key_lower in SENSITIVE_FIELDS:
            continue

        safe[key] = value

    return safe


def safe_metadata_fingerprint(row):

    safe = get_safe_metadata(row)

    if not safe:
        return None

    parts = []

    for key in sorted(
        safe.keys(),
        key=lambda x: str(x).lower()
    ):

        value = safe[key]

        parts.append(
            f"{str(key)}={repr(value)}"
        )

    raw = "|".join(parts)

    digest = hashlib.sha256(
        raw.encode(
            "utf-8",
            errors="replace"
        )
    ).hexdigest()

    return f"SAFE|{digest}"


# =========================================================
# UPDATE IDENTIFIER
# =========================================================

def get_row_identifier(row):

    if not isinstance(row, dict):
        return None

    # Zebra unique delivery identifier.
    # idx is intentionally first because the API response
    # observed in the browser contains this field.

    for key in (
        "idx",
        "id",
        "_id",
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

    # Zebra timestamp fallback

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

    # Other timestamps

    for key in (
        "timestamp",
        "created_at",
        "createdAt",
        "time",
        "date",
        "datetime",
    ):

        value = row.get(key)

        if value not in (None, ""):

            return "|".join([
                "TIME",
                key,
                str(value),
                str(row.get("number", "")),
                str(row.get("sender", "")),
                str(row.get("country", "")),
                str(row.get("operator", "")),
            ])

    # Last safe fallback

    fingerprint = safe_metadata_fingerprint(row)

    if fingerprint:
        return fingerprint

    return None


# =========================================================
# DEBUG
# =========================================================

def debug_row_fields(row, index=None):

    if not isinstance(row, dict):
        return

    safe = get_safe_metadata(row)

    prefix = "[DEBUG]"

    if index is not None:
        prefix += f" Row {index}"

    print(
        f"{prefix} safe fields:"
    )

    if not safe:

        print(
            "    <no safe metadata>"
        )

        return

    for key in sorted(
        safe.keys(),
        key=lambda x: str(x).lower()
    ):

        print(
            f"    {key}: {safe[key]!r}"
        )


def debug_safe_keys(rows):

    if not rows:
        print(
            "[DEBUG] No rows available for key inspection."
        )
        return

    row = rows[0]

    if not isinstance(row, dict):
        print(
            "[DEBUG] First row is not an object."
        )
        return

    safe_keys = []

    for key in row.keys():

        if str(key).lower() in SENSITIVE_FIELDS:
            continue

        safe_keys.append(str(key))

    safe_keys.sort(
        key=lambda x: x.lower()
    )

    print(
        "[Zebra] Safe row keys: "
        + ", ".join(safe_keys)
    )

    print(
        "[Zebra] idx present: "
        + str("idx" in row)
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

    return number.startswith(
        prefix
    )


def find_matching_range(
    active_ranges,
    number,
):

    matches = []

    for value in active_ranges:

        value = normalize_range(
            value
        )

        if not value:
            continue

        if range_matches_number(
            value,
            number,
        ):

            if value not in matches:
                matches.append(value)

    if matches:

        matches.sort(
            key=lambda x: len(
                x.split("X", 1)[0]
            ),
            reverse=True,
        )

        return matches[0]

    return fallback_range(
        number
    )


# =========================================================
# ZEBRA API
# =========================================================

async def zebra_get(
    client,
    url,
    params=None,
):

    headers = {
        "MAuth": ZEBRA_MAUTH_TOKEN,
        "Accept": "application/json",
        "User-Agent": "ZebraSMS-Monitor/1.3",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    response = await client.get(
        url,
        params=params,
        headers=headers,
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(
        payload,
        dict
    ):

        raise RuntimeError(
            "Zebra API returned invalid JSON"
        )

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

    if not isinstance(
        data,
        dict
    ):
        return []

    rows = data.get(
        "rows",
        []
    )

    if not isinstance(
        rows,
        list
    ):
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

    if not isinstance(
        data,
        dict
    ):
        return []

    rows = data.get(
        "rows",
        []
    )

    if not isinstance(
        rows,
        list
    ):
        return []

    all_ranges = []

    for item in rows:

        if not isinstance(
            item,
            dict
        ):
            continue

        ranges = item.get(
            "ranges",
            []
        )

        if not isinstance(
            ranges,
            list
        ):
            continue

        for value in ranges:

            value = normalize_range(
                value
            )

            if (
                value
                and value not in all_ranges
            ):

                all_ranges.append(
                    value
                )

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

    return data.get(
        "result"
    )


# =========================================================
# SEND TELEGRAM UPDATE
# =========================================================

async def send_update(
    client,
    row,
    active_ranges,
):

    if not isinstance(
        row,
        dict
    ):
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
                ],
            },
        },
    )

    message_id = None

    if isinstance(
        result,
        dict
    ):

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
# STARTUP CHECKS
# =========================================================

async def startup_checks(client):

    me = await telegram_call(
        client,
        "getMe"
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
            "chat_id": GROUP_ID
        },
    )

    print(
        "[Telegram] Group: "
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

    print(
        "Unique ID priority: idx"
    )

    print(
        "Cache bypass headers: ENABLED"
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
        # Telegram verification
        # -------------------------------------------------

        await startup_checks(
            client
        )

        # -------------------------------------------------
        # Initial ranges
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Initial update snapshot
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
                get_row_identifier(
                    row
                )
            )

            if signature:

                seen_updates.add(
                    signature
                )

        print(
            "[Zebra] Existing updates marked: "
            f"{len(seen_updates)}"
        )

        # -------------------------------------------------
        # SAFE DIAGNOSTICS
        # -------------------------------------------------

        print(
            "[Zebra] Safe metadata diagnostics:"
        )

        debug_safe_keys(
            initial_rows
        )

        if initial_rows:

            for index, row in enumerate(
                initial_rows[:3],
                start=1,
            ):

                debug_row_fields(
                    row,
                    index
                )

                print(
                    f"[DEBUG] Row {index} "
                    f"identifier="
                    f"{get_row_identifier(row)}"
                )

        else:

            print(
                "[DEBUG] No initial rows."
            )

        print(
            "[Zebra] Waiting for NEW deliveries..."
        )

        # -------------------------------------------------
        # Poll loop
        # -------------------------------------------------

        while True:

            try:

                # =========================================
                # Refresh ranges
                # =========================================

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

                # =========================================
                # Fetch updates
                # =========================================

                rows = await fetch_updates(
                    client
                )

                # Safe timestamp diagnostic

                newest_at_ms = None

                for row in rows:

                    if not isinstance(
                        row,
                        dict
                    ):
                        continue

                    value = row.get(
                        "at_ms"
                    )

                    if value in (
                        None,
                        "",
                    ):
                        continue

                    try:

                        value_num = float(
                            value
                        )

                        if (
                            newest_at_ms is None
                            or value_num > newest_at_ms
                        ):

                            newest_at_ms = (
                                value_num
                            )

                    except Exception:
                        pass

                # Count rows that contain idx.
                # We inspect only the field name/value,
                # never SMS content.

                idx_count = 0

                for row in rows:

                    if (
                        isinstance(row, dict)
                        and row.get("idx")
                        not in (None, "")
                    ):

                        idx_count += 1

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"getupdate rows={len(rows)} "
                    f"idx={idx_count} "
                    f"newest_at_ms={newest_at_ms}"
                )

                # =========================================
                # Detect new rows
                # =========================================

                new_rows = []

                for row in rows:

                    signature = (
                        get_row_identifier(
                            row
                        )
                    )

                    if not signature:
                        continue

                    if signature in seen_updates:
                        continue

                    # Mark immediately so the same delivery
                    # cannot be sent repeatedly.

                    seen_updates.add(
                        signature
                    )

                    print(
                        "[NEW UPDATE]"
                    )

                    print(
                        f"    identifier={signature}"
                    )

                    debug_row_fields(
                        row
                    )

                    new_rows.append(
                        row
                    )

                # =========================================
                # Limit memory
                # =========================================

                if len(seen_updates) > MAX_SEEN:

                    seen_updates = set(
                        list(seen_updates)[
                            -2500:
                        ]
                    )

                # =========================================
                # Send Telegram
                # =========================================

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

            except httpx.RequestError as exc:

                print(
                    "[NETWORK ERROR] "
                    f"{type(exc).__name__}: "
                    f"{exc}"
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
