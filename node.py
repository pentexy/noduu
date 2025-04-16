from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
BOT_TOKEN = "6400675462:AAFlUPT3-RlVZ33MCqduP_6MaaSsx00e5Ak"

FORWARD_COMMANDS = ["/top", "/convert", "/ath", "/crypto", "/ton", "/ltc"]
TARGET_BOT = "NodesGGbot"

# User session
user = Client(
    name="nodes_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string="BQFLWaIAJzdQC557pnlTMHJihwctmm0Vu2BQdk-uuiMrxOueke0PMPo6LAN1f-jBBoj9wTRuJMCnWX9vhKmw0myxQYbBrGt1nCEV5wV7qyOCvkYFPUfa_goOiKQ1MoU1rIMvbKWWyVrBMs2OaZToTfJXRCx4m7Gdq9zAeFJq6IWzDAgHWmOkvEOdnb-5pnhounisIFQl1Ar55yowIv5c_mFiqz-p0y24Bmqt8MJsAFOnkm7vnvJ7ZBbmu7rMdO130DDov7ZS78s0_yWf7KL-q01y5qdr5IEerrZSk8f0DgvWd5OAD9-xgujzQ-gAClxvfqRdnCWDH-NaHyA-OPHO26C13mzTKQAAAAGK6vkyAA"
)

# Bot session
bot = Client("nodes_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@bot.on_message(filters.command(FORWARD_COMMANDS) & filters.private)
async def forward_command(client, message: Message):
    cmd = message.text
    user_msg = await message.reply("⏳ Getting data from Node Network...")

    async with user:
        try:
            # Ensure user session has access to the TARGET_BOT chat
            await user.get_chat(TARGET_BOT)

            # Send the command to @NodesGGbot
            await user.send_message(TARGET_BOT, cmd)

            # Wait for 5 seconds before fetching the most recent message (assuming reply will come in that time)
            await asyncio.sleep(5)

            # Fetch the most recent message from @NodesGGbot
            history = await user.get_chat_history(TARGET_BOT, limit=1)
            response = history[0] if history else None

            if response:
                text = response.text or response.caption or "⚠️ Empty response"
                await user_msg.edit(f"**NodeX Response:**\n\n{text}")
            else:
                await user_msg.edit("⚠️ No response from NodesGGbot.")

        except asyncio.TimeoutError:
            await user_msg.edit("⚠️ No response from NodesGGbot in time.")
        except Exception as e:
            await user_msg.edit(f"❌ Error: `{str(e)}`")


user.start()
bot.run()
