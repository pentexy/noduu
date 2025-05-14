import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
BOT_TOKEN = "7940510400:AAGgBrIQYJaTR2T1DfCBo3S4XD6nMSXeWpE"

app = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_sessions = {}  # user_id: {"bot": Client, "action": None}


@app.on_message(filters.command("start") & filters.private)
async def start_cmd(_, message: Message):
    await message.reply_text("Send me your bot token to connect.")


@app.on_message(filters.private & filters.photo)
async def handle_photo(_, message: Message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session or "bot" not in session:
        await message.reply_text("❌ No connected bot.")
        return

    try:
        file = await message.download()
        await session["bot"].set_profile_photo(file)
        await message.reply_text("✅ Profile photo updated.")
    except Exception as e:
        await message.reply_text(f"❌ Failed: {e}")


@app.on_message(filters.private & filters.text & ~filters.command("start"))
async def handle_text(_, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    session = user_sessions.get(user_id)

    # Step 1: If no session, treat input as bot token
    if not session:
        try:
            managed_bot = Client(
                f"user_bot_{user_id}", api_id=API_ID, api_hash=API_HASH, bot_token=text
            )
            await managed_bot.start()
            me = await managed_bot.get_me()

            user_sessions[user_id] = {"bot": managed_bot, "action": None}

            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Change DP", callback_data="change_dp")],
                    [InlineKeyboardButton("Change Name", callback_data="change_name")],
                    [InlineKeyboardButton("Change Description", callback_data="change_desc")],
                    [InlineKeyboardButton("Change Bio", callback_data="change_bio")],
                ]
            )

            await message.reply_text(
                f"✅ You have connected with @{me.username}",
                reply_markup=buttons,
            )
        except Exception as e:
            await message.reply_text(f"❌ Failed to connect: `{e}`")
        return

    # Step 2: If session exists, handle profile updates
    action = session.get("action")
    bot = session.get("bot")

    if not action:
        return  # No action to perform

    try:
        if action == "name":
            await bot.update_profile(first_name=text)
            await message.reply_text("✅ Name updated.")
        elif action == "bio":
            await bot.set_about(text)
            await message.reply_text("✅ Bio updated.")
        elif action == "desc":
            await bot.set_description(text)
            await message.reply_text("✅ Description updated.")
        session["action"] = None
    except Exception as e:
        await message.reply_text(f"❌ Failed: {e}")


@app.on_callback_query(filters.regex("change_(name|desc|bio)"))
async def change_field(_, query: CallbackQuery):
    user_id = query.from_user.id
    action = query.data.split("_")[1]

    session = user_sessions.get(user_id)
    if not session or "bot" not in session:
        await query.answer("Session expired.", show_alert=True)
        return

    session["action"] = action
    field_map = {"name": "new name", "desc": "new description", "bio": "new bio"}
    await query.message.edit_text(f"Send the {field_map[action]} to update.")


@app.on_callback_query(filters.regex("change_dp"))
async def change_dp(_, query: CallbackQuery):
    await query.message.edit_text(
        "Send a new photo to set as profile picture or use the button below to remove it.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Remove Current DP", callback_data="remove_dp")]]
        ),
    )


@app.on_callback_query(filters.regex("remove_dp"))
async def remove_dp(_, query: CallbackQuery):
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    if not session or "bot" not in session:
        await query.answer("Session expired.", show_alert=True)
        return

    bot = session["bot"]
    try:
        photos = await bot.get_profile_photos("me")
        for photo in photos:
            await bot.delete_profile_photos(photo.file_id)
        await query.message.edit_text("✅ Profile photo removed.")
    except Exception as e:
        await query.message.edit_text(f"❌ Failed: {e}")


app.run()
