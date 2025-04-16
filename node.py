from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

api_id = 21715362  # Your API ID from my.telegram.org
api_hash = "e9ee23b30cffbb5081c6318c3a555f5d"  # Your API hash from my.telegram.org
bot_token = "6400675462:AAFlUPT3-RlVZ33MCqduP_6MaaSsx00e5Ak"  # Your bot token from @BotFather
session_string = "BQFLWaIALVM4xN8QwHBFT-3adIY_viNV97B7vdfRy1GAeL6dWboR4YibYl1k1hHGaAJpjHuw26Dr2BjBtf7Gvgc15cGziWWnCEGPcpH4448i7yTZFg5SvOsm0F-Sf8c7boFhcnHhPHcmlG6qGkXeRS90W4vPwmpx1rpxID-QxILSPWYqHUUceUZhjUUPI1aIsTplq_QM70MlfYfVmgivcz_-CjDP3glQI3xxedaMDknNM06WFSDW5eeLDr-z_9bRwOdhY2yFH-eHxrd-LttlRy5WIMBPQo0ojX22i35OBRwzWiaVHrRa2c-TuGdOdto-ksNmB3RTt-1kWEYzm-QzQJmXngp_BwAAAAHJtXFRAA"  # Your session string

# Initialize the bot and userbot
bot = Client("bot", bot_token=bot_token)
userbot = Client("userbot", api_id=api_id, api_hash=api_hash, session_string=session_string)

# Handler for commands received by the bot
@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply("Hello! Send a command and I'll forward it to @NodesGGbot.")

@bot.on_message(filters.text & ~filters.command("start"))
async def forward_to_nodesggbot(client, message: Message):
    # Get the text command from the user
    user_command = message.text
    
    # Send the command to @NodesGGbot
    sent_message = await userbot.send_message("@NodesGGbot", user_command)
    
    # Wait for a response from @NodesGGbot
    @userbot.on_message(filters.chat("NodesGGbot") & filters.reply)
    async def handle_response(_, bot_msg):
        if bot_msg.reply_to_message.id == sent_message.id:
            # Forward the response (text or media) back to the user
            if bot_msg.text:
                await message.reply(bot_msg.text)
            if bot_msg.media:
                await bot_msg.copy(message.chat.id)
            return

# Run the bot and userbot
bot.run()
userbot.run()
