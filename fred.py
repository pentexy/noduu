from pyrogram import Client, filters

# Fixed config
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
LOG_GROUP_ID = -1002682507946

# Ask only for the bot token at runtime
BOT_TOKEN = input("Enter your Bot Token: ")

bot = Client(
    "ForwardLoggerBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Forward only private messages from real (non-bot) users
@bot.on_message(filters.private & filters.incoming)
async def forward_private_user_messages(client, message):
    try:
        if message.from_user and not message.from_user.is_bot:
            await message.forward(LOG_GROUP_ID)
    except Exception as e:
        print(f"Error while forwarding: {e}")

print("Bot is running...")
bot.run()
