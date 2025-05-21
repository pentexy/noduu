import asyncio
import random
import string
import threading
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import UpdateUsernameRequest
from telethon.errors import UsernameOccupiedError

API_ID = 26416419  # Replace with your API ID
API_HASH = 'c109c77f5823c847b1aeb7fbd4990cc4'

# Shared variables
change_interval = 1800  # Default 30 minutes
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
                print(f"[Timer Updated] Group username will change every {minutes} minutes.")
            except:
                print("Invalid format. Use: .settimer 30")

async def main():
    global trigger_now

    phone = input("Enter your phone number: ")
    client = TelegramClient('session', API_ID, API_HASH)
    await client.start(phone=phone)

    group_username = input("Enter public group username (without @): ")
    entity = await client.get_entity(group_username)

    threading.Thread(target=command_listener, daemon=True).start()

    while True:
        if trigger_now:
            trigger_now = False
        else:
            await asyncio.sleep(change_interval)

        new_username = generate_username()
        try:
            await client(UpdateUsernameRequest(channel=entity, username=new_username))
            print(f"[Changed] Group username updated to: {new_username}")
        except UsernameOccupiedError:
            print(f"[Error] Username {new_username} is taken. Trying again...")
        except Exception as e:
            print(f"[Error] {e}")

asyncio.run(main())
