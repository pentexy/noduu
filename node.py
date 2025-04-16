from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

API_ID = 26416419  # replace with your API ID
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"  # replace with your API hash
BOT_TOKEN = "6400675462:AAFlUPT3-RlVZ33MCqduP_6MaaSsx00e5Ak"  # replace with your bot token

FORWARD_COMMANDS = ["/top", "/convert", "/ath", "/crypto", "/ton", "/ltc"]
GROUP_ID = -1002575253805  # Replace with the correct group ID

# Use your provided session string
user = Client(
    name="nodes_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string="BQFLWaIAJzdQC557pnlTMHJihwctmm0Vu2BQdk-uuiMrxOueke0PMPo6LAN1f-jBBoj9wTRuJMCnWX9vhKmw0myxQYbBrGt1nCEV5wV7qyOCvkYFPUfa_goOiKQ1MoU1rIMvbKWWyVrBMs2OaZToTfJXRCx4m7Gdq9zAeFJq6IWzDAgHWmOkvEOdnb-5pnhounisIFQl1Ar55yowIv5c_mFiqz-p0y24Bmqt8MJsAFOnkm7vnvJ7ZBbmu7rMdO130DDov7ZS78s0_yWf7KL-q01y5qdr5IEerrZSk8f0DgvWd5OAD9-xgujzQ-gAClxvfqRdnCWDH-NaHyA-OPHO26C13mzTKQAAAAGK6vkyAA"
)

bot = Client("nodes_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command(FORWARD_COMMANDS) & filters.private)
async def forward_command(client, message: Message):
    cmd = message.text
    user_msg = await message.reply("⏳ Forwarding your command...")

    async with user:
        try:
            # Forward the command to the target group
            forwarded_msg = await user.send_message(GROUP_ID, cmd)

            # Wait for a response in the group, you may need to tweak the timeout as per your needs
            response = await user.listen(chat_id=GROUP_ID, timeout=10)

            # Forward the response to the user
            text = response.text or response.caption or "⚠️ No response from group."
            await user_msg.edit(f"**Group Response:**\n\n{text}")

        except asyncio.TimeoutError:
            await user_msg.edit("⚠️ No response from group in time.")
        except Exception as e:
            await user_msg.edit(f"❌ Error: `{str(e)}`")

user.start()
bot.run()
