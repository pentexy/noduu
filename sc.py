import asyncio
from telethon import TelegramClient, events, functions
import time

API_ID = 26416419  # <-- Replace with your API ID
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"  # <-- Replace with your API HASH
OWNER_ID = 6748827895  # <-- Replace with your Telegram numeric ID

client = TelegramClient("user_session", API_ID, API_HASH)

lock_keyword = None
bot_username = None
search_task_running = False


async def search_bot_periodically():
    global search_task_running
    while True:
        if lock_keyword and bot_username:
            print(f"[SEARCH] Searching keyword: {lock_keyword}")
            try:
                result = await client(functions.contacts.SearchRequest(
                    q=lock_keyword,
                    limit=20
                ))
                for user in result.users:
                    if user.username and user.username.lower() == bot_username.lower():
                        for _ in range(10):
                            await client.send_message(OWNER_ID, "your bot is now ranked sir !! Congratulations 🎉!")
                        lock_keyword = None
                        bot_username = None
                        print("[RANK DETECTED] Notification sent!")
                        break
            except Exception as e:
                print(f"[ERROR] During search: {e}")
        await asyncio.sleep(1800)  # Wait 30 mins


@client.on(events.NewMessage(from_users=OWNER_ID))
async def handle_commands(event):
    global lock_keyword, bot_username, search_task_running

    message = event.raw_text.strip()

    if message.startswith(".lock "):
        lock_keyword = message.split(" ", 1)[1].strip()
        await event.respond("Enter bot username:")
        print(f"[LOCK] Keyword set: {lock_keyword}")

        response = await client.wait_for(events.NewMessage(from_users=OWNER_ID))
        bot_username = response.raw_text.strip().lstrip("@")
        await event.respond(f"Monitoring started for @{bot_username} using keyword '{lock_keyword}'...")
        print(f"[BOT USERNAME] Tracking @{bot_username}")

        if not search_task_running:
            search_task_running = True
            asyncio.create_task(search_bot_periodically())

    elif message.startswith(".t "):
        temp_keyword = message.split(" ", 1)[1].strip()
        print(f"[TEMP SEARCH] Performing search for: {temp_keyword}")
        try:
            result = await client(functions.contacts.SearchRequest(q=temp_keyword, limit=3))
            if result.users:
                reply = "**Top 3 results:**\n"
                for user in result.users:
                    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                    username = f"@{user.username}" if user.username else "(no username)"
                    reply += f"- {name} | {username}\n"
                await event.respond(reply)
            else:
                await event.respond("No users found for that keyword.")
        except Exception as e:
            await event.respond(f"Error during search: {e}")
            print(f"[ERROR] Temp search: {e}")


async def main():
    await client.start()
    print("[LOGGED IN] Telegram session active.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
