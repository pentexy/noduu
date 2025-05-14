import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)
from pyrogram.errors import PeerIdInvalid, UserNotParticipant
from aiohttp import ClientSession

API_ID = 123456  # Your API ID
API_HASH = "your_api_hash"
BOT_TOKEN = "your_main_bot_token"

app = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_sessions = {}  # user_id: managed_bot_client


# Start Command
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    await message.reply_text("Send me your bot token to connect.")


# Handle Bot Token
@app.on_message(filters.private & filters.text & ~filters.command("start"))
async def receive_token(client: Client, message: Message):
    user_id = message.from_user.id
    token = message.text.strip()

    try:
        managed_bot = Client(
            f"user_bot_{user_id}", api_id=API_ID, api_hash=API_HASH, bot_token=token
        )
        await managed_bot.start()
        me = await managed_bot.get_me()
        user_sessions[user_id] = managed_bot

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


# Callback for DP
@app.on_callback_query(filters.regex("change_dp"))
async def change_dp(_, query: CallbackQuery):
    await query.message.edit_text(
        "Send a new photo to set as profile picture or use the button below to remove it.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Remove Current DP", callback_data="remove_dp")]]
        ),
    )
    return


# Remove DP
@app.on_callback_query(filters.regex("remove_dp"))
async def remove_dp(_, query: CallbackQuery):
    user_id = query.from_user.id
    bot = user_sessions.get(user_id)
    if not bot:
        await query.answer("Session expired.", show_alert=True)
        return

    try:
        photos = await bot.get_profile_photos("me")
        for photo in photos:
            await bot.delete_profile_photos(photo.file_id)
        await query.message.edit_text("✅ Profile photo removed.")
    except Exception as e:
        await query.message.edit_text(f"Error: {e}")


# Handle Photo Upload
@app.on_message(filters.private & filters.photo)
async def set_dp(_, message: Message):
    user_id = message.from_user.id
    bot = user_sessions.get(user_id)
    if not bot:
        await message.reply_text("❌ No connected bot.")
        return

    try:
        file = await message.download()
        await bot.set_profile_photo(file)
        await message.reply_text("✅ Profile photo updated.")
    except Exception as e:
        await message.reply_text(f"❌ Failed: {e}")


# Name, Bio, Description Handlers
@app.on_callback_query(filters.regex("change_(name|desc|bio)"))
async def ask_text_input(_, query: CallbackQuery):
    action = query.data.split("_")[1]
    field_map = {"name": "new name", "desc": "new description", "bio": "new bio"}
    await query.message.edit_text(f"Send the {field_map[action]} to update.")
    user_sessions[query.from_user.id].action = action


@app.on_message(filters.private & filters.text)
async def set_profile_fields(_, message: Message):
    user_id = message.from_user.id
    bot = user_sessions.get(user_id)

    if not bot or not hasattr(bot, "action"):
        return

    action = bot.action
    value = message.text

    try:
        if action == "name":
            await bot.update_profile(first_name=value)
            await message.reply_text("✅ Name updated.")
        elif action == "bio":
            await bot.set_about(value)
            await message.reply_text("✅ Bio updated.")
        elif action == "desc":
            await bot.set_description(value)
            await message.reply_text("✅ Description updated.")
        del bot.action
    except Exception as e:
        await message.reply_text(f"❌ Failed: {e}")


app.run()
