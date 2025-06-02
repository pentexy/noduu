import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.contacts import Search

API_ID = 26416419  # Replace with your API ID
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"  # Replace with your API HASH
OWNER_ID = 6748827895  # Replace with your Telegram user ID

app = Client("user_session", api_id=API_ID, api_hash=API_HASH)

lock_keyword = None
bot_username = None
search_task_running = False


async def search_bot_periodically():
    global lock_keyword, bot_username, search_task_running

    while True:
        if lock_keyword and bot_username:
            print(f"[SEARCH] Searching keyword: {lock_keyword}")
            try:
                result = await app.invoke(Search(q=lock_keyword, limit=20))
                for user in result.users:
                    if user.username and user.username.lower() == bot_username.lower():
                        for _ in range(10):
                            await app.send_message(OWNER_ID, "🎉 Your bot is now ranked sir! Congratulations!")
                        print("[RANK DETECTED] Notification sent!")
                        lock_keyword = None
                        bot_username = None
                        break
            except Exception as e:
                print(f"[ERROR] During periodic search: {e}")
        await asyncio.sleep(1800)  # 30 minutes


@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("lock", prefixes="."))
async def lock_handler(client: Client, message: Message):
    global lock_keyword, bot_username, search_task_running

    if len(message.command) < 2:
        await message.reply("❗ Please provide a keyword.\nUsage: `.lock your_keyword`")
        return

    lock_keyword = message.command[1]
    await message.reply("🔍 Now send the bot username to track (without @):")

    try:
        response = await app.listen(OWNER_ID, timeout=60)
        bot_username = response.text.strip().lstrip("@")
        await message.reply(f"✅ Monitoring started for @{bot_username} with keyword '{lock_keyword}'")
        print(f"[LOCKED] Keyword: {lock_keyword}, Username: @{bot_username}")

        if not search_task_running:
            search_task_running = True
            asyncio.create_task(search_bot_periodically())

    except asyncio.TimeoutError:
        await message.reply("⏰ Timeout. Please try again using `.lock`")


@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("t", prefixes="."))
async def temp_search_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❗ Please provide a keyword.\nUsage: `.t your_keyword`")
        return

    temp_keyword = message.command[1]
    print(f"[TEMP SEARCH] Searching for: {temp_keyword}")
    try:
        result = await app.invoke(Search(q=temp_keyword, limit=3))
        if result.users:
            reply = "**🔍 Top 3 Results:**\n"
            for user in result.users:
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                username = f"@{user.username}" if user.username else "(no username)"
                reply += f"- {name} | {username}\n"
            await message.reply(reply)
        else:
            await message.reply("❌ No users found for that keyword.")
    except Exception as e:
        print(f"[ERROR] Temp search: {e}")
        await message.reply(f"Error during search: {e}")


@app.on_message(filters.private & filters.user(OWNER_ID))
async def catch_all(client: Client, message: Message):
    # For debugging unknown messages
    print(f"[RECEIVED] {message.text}")


async def main():
    await app.start()
    print("[✅ LOGGED IN]")
    await app.send_message(OWNER_ID, "✅ I'm started sir!")  # Auto notify
    await asyncio.Event().wait()  # Keep script running


if __name__ == "__main__":
    asyncio.run(main())
