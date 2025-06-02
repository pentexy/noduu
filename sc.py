import asyncio
from pyrogram import Client, filters
from pyrogram.raw.functions.contacts import Search
import os

API_ID = 26416419  # Replace with your API ID
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"  # Replace with your API Hash
OWNER_ID = 6748827895  # Replace with your Telegram user ID

lock_keyword = None
bot_username = None
search_task_started = False

app = Client("user_session", api_id=API_ID, api_hash=API_HASH)


async def periodic_search():
    global lock_keyword, bot_username, search_task_started
    while True:
        if lock_keyword and bot_username:
            print(f"[SEARCHING] For keyword: {lock_keyword}")
            try:
                result = await app.invoke(Search(q=lock_keyword, limit=20))
                for user in result.users:
                    if user.username and user.username.lower() == bot_username.lower():
                        print(f"[FOUND] Bot @{bot_username} is ranked!")
                        for _ in range(10):
                            await app.send_message(OWNER_ID, "your bot is now ranked sir !! Congratulations 🎉!")
                        lock_keyword = None
                        bot_username = None
                        break
            except Exception as e:
                print(f"[ERROR] During periodic search: {e}")
        await asyncio.sleep(1800)  # 30 minutes


@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("lock", prefixes="."))
async def lock_command(client, message):
    global lock_keyword, bot_username, search_task_started
    try:
        lock_keyword = message.text.split(" ", 1)[1].strip()
        await message.reply("Enter bot username (without @):")
        print(f"[LOCKED] Keyword set: {lock_keyword}")

        response = await app.listen(OWNER_ID)
        bot_username = response.text.strip().lstrip("@")
        await message.reply(f"Tracking @{bot_username} for keyword '{lock_keyword}'...")

        if not search_task_started:
            search_task_started = True
            asyncio.create_task(periodic_search())

    except IndexError:
        await message.reply("Usage: .lock <keyword>")


@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("t", prefixes="."))
async def temp_search_command(client, message):
    try:
        keyword = message.text.split(" ", 1)[1].strip()
        result = await app.invoke(Search(q=keyword, limit=3))
        reply = "**Top 3 results:**\n"
        for user in result.users:
            name = (user.first_name or "") + " " + (user.last_name or "")
            uname = f"@{user.username}" if user.username else "(no username)"
            reply += f"- {name.strip()} | {uname}\n"
        await message.reply(reply)
    except Exception as e:
        await message.reply(f"Error: {e}")
        print(f"[ERROR] Instant search: {e}")


async def main():
    await app.start()
    print("[✅  LOGGED IN]")
    app.idle()

if __name__ == "__main__":
    asyncio.run(main())
