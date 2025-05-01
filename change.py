import requests

BOT_TOKEN = "7841641161:AAGOGBmvkVQECpc5e6xpATEqKmKpF5IW8kU"
NEW_NAME = "Instagram Password WhatsApp Hacker"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyName"
payload = {
    "name": NEW_NAME
}

response = requests.post(url, json=payload)
print(response.json())
