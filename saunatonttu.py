#!/usr/bin/env python3
"""Saunatonttu: ilmoittaa kun pörssisähkö on tarpeeksi halpaa saunan lämmitykseen."""

import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

HELSINKI = ZoneInfo("Europe/Helsinki")

PRICE_API_URL = "https://api.porssisahko.net/v2/latest-prices.json"
PRICE_THRESHOLD_SNT = float(os.environ.get("PRICE_THRESHOLD_SNT", "10.0"))
WINDOW_START_HOUR = int(os.environ.get("WINDOW_START_HOUR", "18"))
WINDOW_END_HOUR = int(os.environ.get("WINDOW_END_HOUR", "21"))  # exclusive
RUN_HOUR_HELSINKI = int(os.environ.get("RUN_HOUR_HELSINKI", "12"))

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}" if NTFY_TOPIC else None

FORCE_RUN = os.environ.get("FORCE_RUN") == "1"


def fetch_todays_prices():
    response = requests.get(PRICE_API_URL, timeout=15)
    response.raise_for_status()
    data = response.json()

    today = datetime.now(HELSINKI).date()
    prices = []
    for entry in data["prices"]:
        start = datetime.fromisoformat(entry["startDate"]).astimezone(HELSINKI)
        # Nayta jakson loppu seuraavan jakson alkuna (raaka endDate on xx:14:59.999).
        end = start + timedelta(minutes=15)
        if start.date() == today and WINDOW_START_HOUR <= start.hour < WINDOW_END_HOUR:
            prices.append((start, end, entry["price"]))

    prices.sort(key=lambda item: item[0])
    return prices


def send_notification(message):
    if not NTFY_URL:
        print("NTFY_TOPIC-ymparistomuuttujaa ei ole asetettu, ohitetaan ilmoitus.")
        print(message)
        return

    response = requests.post(
        NTFY_URL,
        data=message.encode("utf-8"),
        headers={
            "Title": "Saunatonttu🧝🏼",
            "Tags": "fire",
        },
        timeout=15,
    )
    response.raise_for_status()


def main():
    now = datetime.now(HELSINKI)
    if not FORCE_RUN and now.hour != RUN_HOUR_HELSINKI:
        print(f"Kello on {now.hour} Suomen aikaa, ajoikkuna on {RUN_HOUR_HELSINKI}. Ei tehda mitaan.")
        return

    prices = fetch_todays_prices()
    if not prices:
        print("Hintatietoja ei loytynyt tarkasteltavalle aikavalille.")
        return

    cheap_slots = [(start, end, price) for start, end, price in prices if price < PRICE_THRESHOLD_SNT]

    summary = ", ".join(f"{start:%H:%M}-{end:%H:%M}: {price:.2f}" for start, end, price in prices)
    print(f"Tarkasteltu aikavali {WINDOW_START_HOUR}-{WINDOW_END_HOUR}, hinnat: {summary}")

    if not cheap_slots:
        print("Ei riittavan halpoja ajanjaksoja, ei ilmoitusta.")
        return

    lines = [f"klo {start:%H:%M}-{end:%H:%M}: {price:.2f} snt/kWh" for start, end, price in cheap_slots]
    message = (
        f"Sähkö alle {PRICE_THRESHOLD_SNT:.0f} snt/kWh tänään!\n" + "\n".join(lines) + "\nSaunan lämmitykseen sopiva ilta!"
    )
    send_notification(message)
    print("Ilmoitus lahetetty.")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        print(f"Virhe haettaessa dataa tai lahetettaessa ilmoitusta: {exc}", file=sys.stderr)
        sys.exit(1)
