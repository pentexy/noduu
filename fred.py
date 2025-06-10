import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

API_ID = 26416419  # Your API ID here
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
BOT_TOKEN = "7751342718:AAEkyzlvQ790jnLTsL1NvHYMBQqE9GTUAes"

app = Client("manager", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE) as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user_id = str(message.from_user.id)
    db = load_db()
    bots = db.get(user_id, {}).get("bots", {})

    if not bots:
        await message.reply("👋 Welcome! Send your bot token to connect your first bot.")
    else:
        buttons = [
            [InlineKeyboardButton(f"💼 Manage @{u}", callback_data=f"manage|{t}")]
            for t, u in bots.items()
        ]
        buttons.append([InlineKeyboardButton("➕ Add Another Bot", callback_data="add_bot")])
        buttons.append([InlineKeyboardButton("❌ Remove a Bot", callback_data="remove_bot")])

        await message.reply("🤖 **Your Bots:**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="markdown")

@app.on_message(filters.private & ~filters.command(["start", "remove"]))
async def token_handler(client, message: Message):
    user_id = str(message.from_user.id)
    token = message.text.strip()
    try:
        temp = Client(name="temp", bot_token=token)
        await temp.start()
        me = await temp.get_me()
        await temp.stop()

        db = load_db()
        db.setdefault(user_id, {"bots": {}})
        db[user_id]["bots"][token] = me.username
        save_db(db)

        await message.reply(f"✅ Successfully connected to **@{me.username}**!", parse_mode="markdown")
    except Exception as e:
        await message.reply("❌ Invalid token or failed to connect.")

@app.on_callback_query(filters.regex("^add_bot$"))
async def add_bot_cb(client, callback_query: CallbackQuery):
    await callback_query.message.edit("🔐 Send your new bot token to connect.")

@app.on_callback_query(filters.regex("^manage\\|(.*)$"))
async def manage_menu(client, callback_query: CallbackQuery):
    token = callback_query.data.split("|")[1]
    username = "@" + load_db()[str(callback_query.from_user.id)]["bots"][token]
    buttons = [
        [InlineKeyboardButton("✏️ Name", callback_data=f"name|{token}")],
        [InlineKeyboardButton("🧬 Bio", callback_data=f"bio|{token}")],
        [InlineKeyboardButton("📝 Description", callback_data=f"description|{token}")],
        [InlineKeyboardButton("🖼 Change DP", callback_data=f"dp|{token}")],
        [InlineKeyboardButton("⬅️ Back", callback_data="start")]
    ]
    await callback_query.message.edit(f"🔧 Managing {username}", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("^remove_bot$"))
async def remove_menu(client, callback_query: CallbackQuery):
    user_id = str(callback_query.from_user.id)
    db = load_db()
    buttons = [
        [InlineKeyboardButton(f"🗑 @{u}", callback_data=f"del|{t}")]
        for t, u in db.get(user_id, {}).get("bots", {}).items()
    ]
    buttons.append([InlineKeyboardButton("⬅️ Cancel", callback_data="start")])
    await callback_query.message.edit("❌ Select a bot to remove:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("^del\\|(.*)$"))
async def delete_bot(client, callback_query: CallbackQuery):
    user_id = str(callback_query.from_user.id)
    token = callback_query.data.split("|")[1]
    db = load_db()
    botname = db[user_id]["bots"].pop(token, None)
    save_db(db)
    await callback_query.message.edit(f"✅ Bot @{botname} removed.")

@app.on_callback_query(filters.regex("^(name|bio|description|dp)\\|(.*)$"))
async def handle_change(client, callback_query: CallbackQuery):
    action, token = callback_query.data.split("|")
    state_db[callback_query.from_user.id] = (action, token)
    if action == "dp":
        await callback_query.message.edit("🖼 Reply to this with the new profile picture.")
    else:
        await callback_query.message.edit(f"✏️ Send the new {action}.")

state_db = {}

@app.on_message(filters.private & filters.reply)
async def process_reply(client, message: Message):
    user_id = message.from_user.id
    if user_id not in state_db:
        return

    action, token = state_db.pop(user_id)
    try:
        temp = Client(name="temp2", bot_token=token)
        await temp.start()

        if action == "dp" and message.photo:
            file_path = await message.download()
            await temp.set_profile_photo(file_path)
            os.remove(file_path)
            await message.reply("✅ DP updated!")
        else:
            text = message.text
            if action == "name":
                await temp.set_my_name(name=text)
            elif action == "bio":
                await temp.set_my_short_description(short_description=text)
            elif action == "description":
                await temp.set_my_description(description=text)
            await message.reply(f"✅ {action.capitalize()} updated!")

        await temp.stop()
    except Exception as e:
        await message.reply("❌ Failed to update. Make sure input is valid.")

app.run()
