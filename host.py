import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"
main_bot_token = "7904916101:AAHgWzRQ062QFMzL3UTDsCcq512DmCWB7Vw"

# ====== ALLOWED USERS ======
allowed_users = {7913490752}

main_app = Client("controller_bot", api_id=api_id, api_hash=api_hash, bot_token=main_bot_token)

hosted_bots = {}
owners = {}
users_db = {}
custom_replies = {}
broadcast_msgs = {}
trigger_temp = {}

# =========== MAIN BOT HANDLERS ===========

@main_app.on_message(filters.command("start") & filters.private)
async def start_main(client, message):
    if message.from_user.id not in allowed_users:
        await message.reply_text("❌ You are not authorized to use this bot.")
        return
    await message.reply_text("**please enter your bot token sir !**", parse_mode="markdown")

@main_app.on_message(filters.command("add") & filters.private)
async def add_user(client, message):
    if message.from_user.id not in allowed_users:
        await message.reply_text("❌ You are not authorized to use this command.")
        return
    try:
        new_user = int(message.text.split()[1])
        allowed_users.add(new_user)
        await message.reply_text(f"✅ User {new_user} added successfully.")
    except:
        await message.reply_text("⚠️ Usage: /add {user_id}")

@main_app.on_message(filters.private & ~filters.command(["start", "add"]))
async def handle_token(client, message):
    if message.from_user.id not in allowed_users:
        await message.reply_text("❌ You are not authorized to use this bot.")
        return

    token = message.text.strip()
    owner_id = message.from_user.id

    owners[token] = owner_id
    users_db[token] = set()
    custom_replies[token] = {}
    broadcast_msgs[token] = []
    trigger_temp[token] = None

    # Start hosted bot
    hosted_bots[token] = Client(f"hosted_bot_{token}", api_id=api_id, api_hash=api_hash, bot_token=token)
    await hosted_bots[token].start()

    # Register handlers dynamically for hosted bot
    register_hosted_bot_handlers(token)

    await message.reply_text(
        "<b>📢 TON Ecosystem Update: Social Media Rebranding</b>\n\n"
        "<blockquote>TON community has evolved from a builders’ hub into a global network of users, creators, and developers. "
        "To mirror this evolution, we’re streamlining our social media presence for clarity, communication, and consistency. "
        "Here’s what’s changing: @toncoin @telegram</blockquote>",
        parse_mode="html"
    )

# =========== HOSTED BOT HANDLERS ===========

def register_hosted_bot_handlers(token):
    bot = hosted_bots[token]

    @bot.on_message(filters.command("start") & filters.private)
    async def start_hosted(client, message):
        users_db[token].add(message.from_user.id)
        if message.from_user.id == owners[token]:
            await message.reply_text(
                f"<b>Yoo , {message.from_user.mention}</b>\n"
                "<blockquote>You Can Customize Your Bot From Here</blockquote>",
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Live Static ✨", callback_data=f"live_{token}")],
                        [InlineKeyboardButton("Broadcast 💗", callback_data=f"broadcast_{token}")],
                        [InlineKeyboardButton("Customize", callback_data=f"custom_{token}")]
                    ]
                )
            )
        else:
            await message.reply_text("Welcome!")

    @bot.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("live_")))
    async def live_static(client, callback_query):
        if callback_query.from_user.id != owners[token]:
            await callback_query.answer("Not allowed.")
            return
        await callback_query.message.edit_text(
            f"<b>Live Users Count:</b> <blockquote>{len(users_db[token])}</blockquote>",
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Refresh 🔄", callback_data=f"live_{token}")],
                    [InlineKeyboardButton("Back 🔙", callback_data=f"back_{token}")]
                ]
            )
        )

    @bot.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("back_")))
    async def back_home(client, callback_query):
        await start_hosted(client, callback_query.message)

    @bot.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("broadcast_")))
    async def broadcast_start(client, callback_query):
        if callback_query.from_user.id != owners[token]:
            await callback_query.answer("Not allowed.")
            return
        broadcast_msgs[token].clear()
        await callback_query.message.edit_text(
            "<b>Broadcast Mode</b>\n<blockquote>Send messages you want to broadcast. When ready, type /send</blockquote>",
            parse_mode="html"
        )

    @bot.on_message(filters.command("send") & filters.private)
    async def send_broadcast(client, message):
        if message.from_user.id != owners[token]:
            return
        for user_id in users_db[token]:
            try:
                for msg in broadcast_msgs[token]:
                    await bot.send_message(user_id, msg)
            except:
                pass
        await message.reply_text("<b>Broadcast sent!</b>", parse_mode="html")
        broadcast_msgs[token].clear()

    @bot.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("custom_")))
    async def customize_start(client, callback_query):
        if callback_query.from_user.id != owners[token]:
            await callback_query.answer("Not allowed.")
            return
        trigger_temp[token] = None
        await callback_query.message.edit_text(
            "<b>Customize Mode</b>\n<blockquote>Send a trigger message, then its reply. Example:\nhello\nhi there</blockquote>",
            parse_mode="html"
        )

    @bot.on_message(filters.private & ~filters.command(["start", "send"]))
    async def handle_custom_or_broadcast(client, message):
        users_db[token].add(message.from_user.id)

        if message.from_user.id == owners[token]:
            if trigger_temp[token] is None:
                trigger_temp[token] = message.text.strip()
                await message.reply_text(
                    f"<b>Trigger saved:</b> <blockquote>{trigger_temp[token]}</blockquote>\nSend the reply now.",
                    parse_mode="html"
                )
            else:
                custom_replies[token][trigger_temp[token]] = message.text.strip()
                await message.reply_text(
                    f"<b>Custom reply saved!</b>\n<blockquote>{trigger_temp[token]} ➔ {message.text.strip()}</blockquote>",
                    parse_mode="html"
                )
                trigger_temp[token] = None
            broadcast_msgs[token].append(message.text)
        else:
            reply = custom_replies[token].get(message.text.strip())
            if reply:
                await message.reply_text(reply)

# =========== RUN ===========

async def main():
    await main_app.start()
    print("✅ Main controller bot running only for authorized users...")
    await asyncio.Event().wait()

asyncio.run(main())
