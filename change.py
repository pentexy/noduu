import requests

BOT_TOKEN = "8104232055:AAF9D9WGIn_wSN49lDMY63zy1PTSj7jNNJ8"
NEW_NAME = "Viral Mms videos Hindi"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyName"
payload = {
    "name": NEW_NAME
}

response = requests.post(url, json=payload)
print(response.json())
