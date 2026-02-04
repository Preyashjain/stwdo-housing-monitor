import requests
from bs4 import BeautifulSoup
import hashlib
import smtplib
import os
import sys

URL = "https://www.stwdo.de/en/living-houses-application/current-housing-offers"

def get_env(name, required=True, default=None):
    val = os.getenv(name, default)
    if required and not val:
        print(f"ERROR: Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return val


EMAIL_FROM = get_env("EMAIL_FROM")
EMAIL_TO = get_env("EMAIL_TO")
EMAIL_PASSWORD = get_env("EMAIL_PASSWORD")

def send_email(message):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(
                EMAIL_FROM,
                EMAIL_TO,
                f"Subject: Dortmund Housing Available!\n\n{message}"
            )
    except Exception as e:
        print(f"Failed to send email: {e}", file=sys.stderr)
        sys.exit(1)

try:
    response = requests.get(URL, timeout=20)
    response.raise_for_status()
except Exception as e:
    print(f"Failed to fetch URL {URL}: {e}", file=sys.stderr)
    sys.exit(1)

soup = BeautifulSoup(response.text, "html.parser")

offers_section = soup.select_one("#residential-offer-list")

if not offers_section:
    print("Offer list not found")
    sys.exit(0)

text = offers_section.get_text(separator=" ", strip=True)

if "Dortmund" not in text:
    print("No Dortmund offer yet")
    sys.exit(0)

current_hash = hashlib.md5(text.encode()).hexdigest()

try:
    with open("last_hash.txt", "r") as f:
        old_hash = f.read()
except FileNotFoundError:
    old_hash = ""

if current_hash != old_hash:
    send_email(
        "A housing offer for Dortmund has appeared.\n\n"
        "Check here:\n"
        "https://www.stwdo.de/en/living-houses-application/current-housing-offers"
    )
    with open("last_hash.txt", "w") as f:
        f.write(current_hash)
    print("Email sent")
else:
    print("No new change")