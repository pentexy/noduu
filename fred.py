from pyrogram import Client, filters

# Ask for configuration at runtime
API_ID = int(input("Enter your API ID: "))
API_HASH = input("Enter your API Hash: ")
BOT_TOKEN = input("Enter your Bot Token: ")
LOG_GROUP_ID = int(input("Enter your Log Group ID (with -100 if it's a supergroup): "))

bot = Client(
    "ForwardLoggerBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.all & ~filters.channel)
async def forward_all_messages(client, message):
    try:
        await message.forward(LOG_GROUP_ID)
    except Exception as e:
        print(f"Error while forwarding: {e}")

print("Bot is running...")
bot.run()
