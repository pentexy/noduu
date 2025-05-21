import asyncio
import random
import string
import threading
from pyrogram import Client
from pyrogram.errors import UsernameInvalid, UsernameOccupied, RPCError
from pyrogram import __version__, enums
from pyrogram.session import Session

API_ID = 26416419
API_HASH = 'c109c77f5823c847b1aeb7fbd4990cc4'

change_interval = 1800  # 30 minutes default
trigger_now = False

def generate_username():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def command_listener():
    global change_interval, trigger_now
    while True:
        cmd = input().strip()
        if cmd == ".change":
            trigger_now = True
        elif cmd.startswith(".settimer "):
            try:
                minutes = int(cmd.split()[1])
                change_interval = minutes * 60
                print(f"[Timer Updated] Username will change every {minutes} minutes.")
            except:
                print("Invalid format. Use: .settimer 30")

async def change_username(app, chat_id):
    while True:
        global trigger_now
        if trigger_now:
            trigger_now = False
        else:
            await asyncio.sleep(change_interval)

        new_username = generate_username()
        try:
            await app.set_chat_username(chat_id, new_username)
            print(f"[Changed] Username updated to: {new_username}")
        except UsernameOccupied:
            print(f"[Error] Username {new_username} is already taken.")
        except UsernameInvalid:
            print(f"[Error] Username {new_username} is invalid.")
        except RPCError as e:
            print(f"[Error] {e}")

async def main():
    phone_number = input("Enter your phone number: ")
    
Session.app_version = "9.6.1"
Session.device_model = "iPhone 14 Pro"
Session.system_version = "iOS 16.6"

app = Client(
    "pyrogram_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=phone_number
)

    await app.start()
    group_username = input("Enter public group username (without @): ")
    
    try:
        chat = await app.get_chat(group_username)
    except Exception as e:
        print(f"[Error] Cannot find group: {e}")
        return

    chat_id = chat.id
    threading.Thread(target=command_listener, daemon=True).start()
    await change_username(app, chat_id)

asyncio.run(main())
