import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"

BOT_TOKEN = "7794088421:AAEr9pgZ-yrWlvWZJWverKGclA7ys8UIpmE"  # Bot token
OWNER_ID = 6748827895  # Your Telegram numeric ID (bot owner)

# Globals to track current locked keyword and bot username
lock_keyword = None
bot_username = None
search_task = None

# Initialize clients
user_client = Client("user_session", api_id=API_ID, api_hash=API_HASH)
bot_client = Client("bot_session", bot_token=BOT_TOKEN)

async def search_bot_periodically():
    global lock_keyword, bot_username
    while lock_keyword and bot_username:
        try:
            print(f"[SEARCH] Searching keyword '{lock_keyword}' for bot @{bot_username}")
            # Search global users by keyword
            result = await user_client.search_global(lock_keyword, limit=20)

            found = False
            for user in result:
                if user.username and user.username.lower() == bot_username.lower():
                    # Send congratulation messages via bot to owner
                    for _ in range(10):
                        try:
                            await bot_client.send_message(OWNER_ID, "Your bot is now ranked sir!! Congratulations 🎉!")
                        except FloodWait as e:
                            print(f"[FLOOD WAIT] Sleeping for {e.x} seconds.")
                            await asyncio.sleep(e.x)
                    print("[RANK DETECTED] Notification sent!")
                    found = True
                    break

            if found:
                # Reset after notification
                lock_keyword = None
                bot_username = None
                break  # stop searching until new command

        except Exception as e:
            print(f"[ERROR] Search error: {e}")

        await asyncio.sleep(1800)  # 30 minutes


@bot_client.on_message(filters.private & filters.user(OWNER_ID))
async def bot_command_handler(client, message):
    global lock_keyword, bot_username, search_task

    text = message.text.strip()

    if text.startswith(".lock "):
        lock_keyword = text.split(" ", 1)[1].strip()
        await message.reply("Enter bot username (without @):")

        # Wait next message from owner for bot username
        response = await bot_client.listen_private(chat_id=OWNER_ID, timeout=60)
        if not response or not response.text:
            await message.reply("Timeout or invalid input. Please try again.")
            lock_keyword = None
            return

        bot_username = response.text.strip().lstrip("@")
        await message.reply(f"Monitoring started for @{bot_username} using keyword '{lock_keyword}'.")

        # Start periodic search task if not running
        if search_task is None or search_task.done():
            search_task = asyncio.create_task(search_bot_periodically())

    elif text.startswith(".t "):
        temp_keyword = text.split(" ", 1)[1].strip()
        await message.reply(f"Searching top 3 results for '{temp_keyword}' ...")
        try:
            results = await user_client.search_global(temp_keyword, limit=3)
            if results:
                reply_text = "**Top 3 results:**\n"
                for user in results:
                    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                    username = f"@{user.username}" if user.username else "(no username)"
                    reply_text += f"- {name} | {username}\n"
                await message.reply(reply_text)
            else:
                await message.reply("No users found for that keyword.")
        except Exception as e:
            await message.reply(f"Error during search: {e}")


async def main():
    print("Starting clients...")
    await user_client.start()
    print("[USER ACCOUNT] Logged in successfully.")
    await bot_client.start()
    print("[BOT ACCOUNT] Logged in successfully.")
    await bot_client.send_message(OWNER_ID, "✅ I'm started sir!")

    print("Clients started, waiting for commands...")
    # Keep running until stopped
    await asyncio.gather(user_client.idle(), bot_client.idle())


if __name__ == "__main__":
    asyncio.run(main())
