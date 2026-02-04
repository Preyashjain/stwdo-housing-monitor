import requests
from bs4 import BeautifulSoup
import hashlib
import smtplib
import os

URL = "https://www.stwdo.de/en/living-houses-application/current-housing-offers"

EMAIL_FROM = os.environ["preyashjain916@gmail.com"]
EMAIL_TO = os.environ["preyashjain916@gmail.com"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

def send_email(message):
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(
            EMAIL_FROM,
            EMAIL_TO,
            f"Subject: Dortmund Housing Available!\n\n{message}"
        )

response = requests.get(URL, timeout=20)
soup = BeautifulSoup(response.text, "html.parser")

offers_section = soup.select_one("#residential-offer-list")

if not offers_section:
    print("Offer list not found")
    exit()

text = offers_section.get_text(separator=" ", strip=True)

if "Dortmund" not in text:
    print("No Dortmund offer yet")
    exit()

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
