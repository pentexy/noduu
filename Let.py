from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
import random
import asyncio
from datetime import datetime
import json
import subprocess
import os
import sys


#================================================================================================================================#

# ===================
# Dynamic Config Section
# ===================
DBNAME = "RankFather"
TOKEN = "8260087085:AAEWb6nrIsVR14gVQpAvamkT55Lp9LqBS0k"
NAME   = "riorandi"
CONFIG_FILE = "riorandi_config.json"
# Allow overriding by passing a config path as the first CLI argument, i.e.:
#   python bot.py configs/another_bot.json
if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
    CONFIG_FILE = sys.argv[1]

def load_bot_config():
    """Load TOKEN, DBNAME and NAME from a local json file if present."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
        except (json.JSONDecodeError, OSError):
            cfg = {}
    else:
        cfg = {}

    globals().update({
        "DBNAME": cfg.get("DBNAME", DBNAME),
        "TOKEN":  cfg.get("TOKEN", TOKEN),
        "NAME":   cfg.get("NAME", NAME),
    })

# Load configuration before creating DB / bot client
load_bot_config()

OWNER_ID = 7072373613

DB = "riorandi"

# LOG_FILE will be set after config is loaded
LOG_FILE = f"{NAME}.txt"


#================================================================================================================================#

client = AsyncIOMotorClient(DB)
db = client[DBNAME]
users_collection = db["users"]
settings_collection = db["settings"]

# Create the bot client – raise an error if TOKEN or NAME are still empty so the
# owner knows to set them via the config command.
if not TOKEN or not NAME:
    raise ValueError("TOKEN and NAME must be provided. Use /setbotconfig or create bot_config.json to set them.")

app = Client(NAME, api_id=20028561, api_hash="0f3793daaf4d3905e55b0e44d8719cad",
            bot_token=TOKEN)


DEFAULT_START_MESSAGE = """
Hello {user_mention}! 👋

📊 $BLUM Tokenomics is live!

Total supply: 1,000,000,000 $BLUM
20% is reserved for the community – from early supporters to traders and Memepad explorers. No team or investor unlocks at launch.

Full breakdown ⤵️
www.blum.io/post/blum-tokenomics

🫂 Community – 20% of total supply
– 50% is allocated to the pre-launch airdrop (Drop game, referrals, Memepad users, and other activities)
– 50% is reserved for post-launch rewards
30% of the pre-launch airdrop unlocks at TGE, with the remaining 70% vesting linearly over 6 months.

🌱 Ecosystem Growth – 20% of total supply
This fuels liquidity, developer incentives, product integrations, and strategic expansion – including token liquidity across exchanges to support healthy market activity.
– 19% unlocks at TGE
– 81% vests over 48 months

🏦 Treasury – 28.08% of total supply
Used to fund product development, legal, security, operations, and reserves. Structured as a long-term buffer to ensure protocol sustainability.
– 10% of the treasury pool unlocks at TGE
– 90% vests linearly over 48 months

👷 Contributors – 16.11% of total supply
For the people behind the product, aligned with long-term execution. Contributors earn their allocation by actively building and maintaining the protocol.
– 12-month cliff, then 24-month linear vesting
– No unlock at TGE

🤝 Strategic Investors – 15.81% of total supply
Allocated to infrastructure partners and investors who contribute to ecosystem growth. Structured to discourage short-term speculation & reward long-term commitment.
– 9-month cliff, then 18-month linear vesting
– No unlock at TGE

"""

DEFAULT_START_PHOTO = None
DEFAULT_START_BUTTONS = [
    [{"text": "🌱 Blum", "url": "https://t.me/Blum"}],
    [{"text": "👷 Durov", "url": "https://t.me/Durov"}]
]

async def send_startup_message():
    """Send startup success message to owner"""
    try:
        startup_msg = f"""
🚀 **Bot Started Successfully!**

✅ **Status:** Online and Ready
🗄️ **Database Code:** `{DBNAME}`

Your bot is now running and ready to serve users!
"""
        await app.send_message(OWNER_ID, startup_msg)
        print(f"✅ Startup message sent to owner. DB Code: {DBNAME}")
    except Exception as e:
        print(f"❌ Failed to send startup message: {e}")

async def get_start_settings():
    """Get start command settings from database"""
    settings = await settings_collection.find_one({"type": "start_settings"})
    if not settings:
        # Create default settings
        default_settings = {
            "type": "start_settings",
            "message": DEFAULT_START_MESSAGE,
            "photo": DEFAULT_START_PHOTO,
            "buttons": DEFAULT_START_BUTTONS
        }
        await settings_collection.insert_one(default_settings)
        return default_settings
    return settings

async def save_user(user_id, username, first_name, last_name=None):
    """Save user information to database"""
    user_data = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "joined_date": datetime.now(),
        "last_seen": datetime.now()
    }
    
    # Update if exists, insert if not
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": user_data},
        upsert=True
    )

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    try:
        user = message.from_user
    
        # Save user to database
        await save_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Get start settings
        settings = await get_start_settings()
        
        # Format message with user mention
        formatted_message = settings["message"].format(
            user_mention=user.mention,
            user_name=user.first_name,
            username=user.username or "User"
        )
        
        # Create inline keyboard if buttons exist
        keyboard = None
        if settings.get("buttons"):
            keyboard_rows = []
            for row in settings["buttons"]:
                button_row = []
                for btn in row:
                    # Only URL buttons are supported
                    button_row.append(InlineKeyboardButton(btn["text"], url=btn["url"]))
                keyboard_rows.append(button_row)
            keyboard = InlineKeyboardMarkup(keyboard_rows)
        
        # Send message with or without photo
        if settings.get("photo"):
            await message.reply_photo(
                photo=settings["photo"],
                caption=formatted_message,
                reply_markup=keyboard
            )
        else:
            await message.reply_text(
                text=formatted_message,
                reply_markup=keyboard
            )
    except Exception as e:
        print(f"❌ Failed to start: {e}")

@app.on_message(filters.command("setstartmsg") & filters.user(OWNER_ID))
async def set_start_message(client: Client, message: Message):
    """Allow owner to customize start message"""
    try :
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:** `/setstartmsg <your_message>`\n\n"
                "**Available placeholders:**\n"
                "• `{user_mention}` - User's mention\n"
                "• `{user_name}` - User's first name\n"
                "• `{username}` - User's username\n\n"
                "**Example:** `/setstartmsg Hello {user_mention}! Welcome to our bot! 🎉`"
            )
            return
        
        new_message = message.text.split(None, 1)[1]
        
        await settings_collection.update_one(
            {"type": "start_settings"},
            {"$set": {"message": new_message}},
            upsert=True
        )
        
        await message.reply_text("✅ Start message updated successfully!")
        
    except Exception as e:
        print(f"❌ Failed to set start message: {e}")

@app.on_message(filters.command("setstartphoto") & filters.user(OWNER_ID))
async def set_start_photo(client: Client, message: Message):
    """Allow owner to set start photo"""
    try :
        if message.reply_to_message and message.reply_to_message.photo:
            photo_file_id = message.reply_to_message.photo.file_id
            
            await settings_collection.update_one(
                {"type": "start_settings"},
                {"$set": {"photo": photo_file_id}},
                upsert=True
            )
            
            await message.reply_text("✅ Start photo updated successfully!")
        else:
            await message.reply_text("❌ Please reply to a photo to set it as start photo!")
    
    except Exception as e:
        print(f"❌ Failed to set start photo: {e}")

@app.on_message(filters.command("removestartphoto") & filters.user(OWNER_ID))
async def remove_start_photo(client: Client, message: Message):
    """Remove start photo"""
    try :
        await settings_collection.update_one(
            {"type": "start_settings"},
            {"$set": {"photo": None}},
            upsert=True
        )
        
        await message.reply_text("✅ Start photo removed successfully!")

    except Exception as e:
        print(f"❌ Failed to remove start photo: {e}")

@app.on_message(filters.command("setstartbuttons") & filters.user(OWNER_ID))
async def set_start_buttons(client: Client, message: Message):
    try:
        """Allow owner to customize start URL buttons only"""
        help_text = """
🔘 **Set Start URL Buttons**

**Format:** `/setstartbuttons ButtonText:https://example.com`

**Examples:**
• Single row: `/setstartbuttons Website:https://example.com`
• Multiple buttons: `/setstartbuttons Website:https://example.com Telegram:https://t.me/username`
• Multiple rows: `/setstartbuttons Website:https://example.com|Telegram:https://t.me/username Support:https://t.me/support`

**Use `|` to separate rows**
**Use `:` to separate button text and URL**

**To remove all buttons:** `/setstartbuttons none`
"""
        
        if len(message.command) < 2:
            await message.reply_text(help_text)
            return
        
        buttons_text = message.text.split(None, 1)[1]
        
        if buttons_text.lower() == "none":
            await settings_collection.update_one(
                {"type": "start_settings"},
                {"$set": {"buttons": []}},
                upsert=True
            )
            await message.reply_text("✅ Start buttons removed successfully!")
            return
        
        try:
            # Parse buttons
            rows = buttons_text.split("|")
            buttons = []
            
            for row in rows:
                button_row = []
                button_pairs = row.strip().split()
                
                for pair in button_pairs:
                    # Split only on the first colon to handle URLs properly
                    parts = pair.split(":", 1)
                    if len(parts) == 2:
                        text = parts[0]
                        url = parts[1]
                        
                        # Basic URL validation
                        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("tg://")):
                            raise ValueError(f"Invalid URL format: {url}. URL must start with http://, https://, or tg://")
                        
                        button_row.append({"text": text, "url": url})
                    else:
                        raise ValueError(f"Invalid button format: {pair}. Use ButtonText:URL format")
                
                if button_row:
                    buttons.append(button_row)
            
            await settings_collection.update_one(
                {"type": "start_settings"},
                {"$set": {"buttons": buttons}},
                upsert=True
            )
            
            # Show success message with preview
            preview_text = "✅ Start buttons updated successfully!\n\n**Preview:**\n"
            for i, row in enumerate(buttons, 1):
                preview_text += f"Row {i}: "
                for btn in row:
                    preview_text += f"[{btn['text']}]({btn['url']}) "
                preview_text += "\n"
            
            await message.reply_text(preview_text)
            
        except Exception as parse_error:
            await message.reply_text(f"❌ Invalid format! Error: {str(parse_error)}\n\n{help_text}")

    except Exception as e:
        print(f"❌ Failed to set start buttons: {e}")
        await message.reply_text("❌ An error occurred while setting buttons. Please try again.")
        
@app.on_message(filters.command("previewstart") & filters.user(OWNER_ID))
async def preview_start(client: Client, message: Message):
    try :
    
        """Preview current start message settings"""
        settings = await get_start_settings()
        
        # Format message with owner's info as preview
        formatted_message = settings["message"].format(
            user_mention=message.from_user.mention,
            user_name=message.from_user.first_name,
            username=message.from_user.username or "User"
        )
        
        # Create inline keyboard if buttons exist
        keyboard = None
        if settings.get("buttons"):
            keyboard_rows = []
            for row in settings["buttons"]:
                button_row = []
                for btn in row:
                    if btn.get("url"):
                        # URL button
                        button_row.append(InlineKeyboardButton(btn["text"], url=btn["url"]))
                    else:
                        # Callback button
                        button_row.append(InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"]))
                keyboard_rows.append(button_row)
            keyboard = InlineKeyboardMarkup(keyboard_rows)
        
        # Send preview
        preview_text = "🔍 **Start Message Preview:**\n\n" + formatted_message
        
        if settings.get("photo"):
            await message.reply_photo(
                photo=settings["photo"],
                caption=preview_text,
                reply_markup=keyboard
            )
        else:
            await message.reply_text(
                text=preview_text,
                reply_markup=keyboard
            )
    except Exception as e:
        print(f"❌ Failed to preview start: {e}")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client: Client, message: Message):
    try :
    
    
        """Broadcast message to all users with entity support"""
        if not message.reply_to_message:
            await message.reply_text("❌ Please reply to a message to broadcast it!")
            return
        
        users = await users_collection.find({}).to_list(length=None)
        total_users = len(users)
        
        if total_users == 0:
            await message.reply_text("❌ No users found in database!")
            return
        
        status_msg = await message.reply_text(f"📡 Broadcasting to {total_users} users...")
        
        success_count = 0
        failed_count = 0
        
        broadcast_msg = message.reply_to_message
        
        for user in users:
            try:
                if broadcast_msg.photo:
                    await app.send_photo(
                        chat_id=user["user_id"],
                        photo=broadcast_msg.photo.file_id,
                        caption=broadcast_msg.caption,
                        caption_entities=broadcast_msg.caption_entities
                    )
                elif broadcast_msg.video:
                    await app.send_video(
                        chat_id=user["user_id"],
                        video=broadcast_msg.video.file_id,
                        caption=broadcast_msg.caption,
                        caption_entities=broadcast_msg.caption_entities
                    )
                elif broadcast_msg.document:
                    await app.send_document(
                        chat_id=user["user_id"],
                        document=broadcast_msg.document.file_id,
                        caption=broadcast_msg.caption,
                        caption_entities=broadcast_msg.caption_entities
                    )
                elif broadcast_msg.audio:
                    await app.send_audio(
                        chat_id=user["user_id"],
                        audio=broadcast_msg.audio.file_id,
                        caption=broadcast_msg.caption,
                        caption_entities=broadcast_msg.caption_entities
                    )
                elif broadcast_msg.voice:
                    await app.send_voice(
                        chat_id=user["user_id"],
                        voice=broadcast_msg.voice.file_id,
                        caption=broadcast_msg.caption,
                        caption_entities=broadcast_msg.caption_entities
                    )
                elif broadcast_msg.sticker:
                    await app.send_sticker(
                        chat_id=user["user_id"],
                        sticker=broadcast_msg.sticker.file_id
                    )
                elif broadcast_msg.animation:
                    await app.send_animation(
                        chat_id=user["user_id"],
                        animation=broadcast_msg.animation.file_id,
                        caption=broadcast_msg.caption,
                        caption_entities=broadcast_msg.caption_entities
                    )
                else:
                    await app.send_message(
                        chat_id=user["user_id"],
                        text=broadcast_msg.text,
                        entities=broadcast_msg.entities
                    )
                success_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to send to {user['user_id']}: {e}")
            
            # Small delay to avoid flooding
            await asyncio.sleep(0.1)
        
        await status_msg.edit_text(
            f"✅ **Broadcast Completed!**\n\n"
            f"📊 **Statistics:**\n"
            f"• Total Users: `{total_users}`\n"
            f"• Successfully Sent: `{success_count}`\n"
            f"• Failed: `{failed_count}`"
        )
    
    except Exception as e:
        print(f"❌ Failed to broadcast: {e}")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client: Client, message: Message):
    try :
    
    
        """Show bot statistics"""
        total_users = await users_collection.count_documents({})
        
        # Get recent users (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_users = await users_collection.count_documents({"joined_date": {"$gte": week_ago}})
        
        # Get today's users
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_users = await users_collection.count_documents({"joined_date": {"$gte": today}})
        
        stats_text = f"""
    📊 **Bot Statistics**
    
    👥 **Users:**
    • Total Users: `{total_users}`
    • New Users (Today): `{today_users}`
    • New Users (7 Days): `{recent_users}`
    
    🗄️ **Database:**
    • Database Code: `{DBNAME}`
    
    📅 **Last Updated:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
    """
        
        await message.reply_text(stats_text)
    
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")

@app.on_message(filters.command("getusers") & filters.user(OWNER_ID))
async def get_users(client: Client, message: Message):
    try :
    
    
        """Get list of all users"""
        users = await users_collection.find({}).to_list(length=100)  # Limit to 100 for performance
        
        if not users:
            await message.reply_text("❌ No users found!")
            return
        
        users_text = "👥 **Bot Users:**\n\n"
        for i, user in enumerate(users, 1):
            username = f"@{user['username']}" if user.get('username') else "No username"
            users_text += f"{i}. {user['first_name']} ({username}) - `{user['user_id']}`\n"
            
            if len(users_text) > 3500:  # Telegram message limit
                break
        
        if len(users) > 100:
            users_text += f"\n... and {len(users) - 100} more users"
        
        await message.reply_text(users_text)
    
    except Exception as e:
        print(f"❌ Failed to get users: {e}")

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Show help message"""
    if message.from_user.id == OWNER_ID:
        help_text = """
🤖 **Bot Commands**

**Owner Commands:**
• `/setstartmsg <message>` - Set custom start message
• `/setstartphoto` - Set start photo (reply to image)
• `/removestartphoto` - Remove start photo
• `/setstartbuttons <buttons>` - Set custom start buttons (supports URL)
• `/previewstart` - Preview current start settings
• `/broadcast` - Broadcast message (reply to message)
• `/stats` - Show bot statistics
• `/getusers` - Get list of users
• `/help` - Show this help

**User Commands:**
• `/start` - Start the bot
• `/help` - Show help
"""
    else:
        help_text = """
🤖 **Bot Commands**

• `/start` - Start the bot
• `/help` - Show this help

Need more help? Contact the bot owner!
"""
    
    try :
        await message.reply_text(help_text)
    except Exception as e:
        print(f"❌ Failed to send help message: {e}")

async def main():
    """Main function to start the bot"""
    await app.start()
    print(f"🤖 Bot started successfully!")
    print(f"🗄️ Database Code: {DBNAME}")
    
    # Send startup message to owner
    try :
        await send_startup_message()
    except Exception as e:
        print(f"❌ Failed to send startup message: {e}")
    
    await idle()
    await app.stop()

@app.on_message(filters.incoming & filters.private, group=2)
async def incoming(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        # Log message to file
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            log_entry = (
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"User ID: {message.from_user.id}\n"
                f"Username: @{message.from_user.username}\n"
                f"First Name: {message.from_user.first_name}\n"
                f"Message: {message.text or '[Non-text message]'}\n"
                "------------------------------\n"
            )
            f.write(log_entry)

@app.on_message(filters.command("get") & filters.user(OWNER_ID))
async def get_log_file(client: Client, message: Message):

    try:
        await message.reply_document(document=LOG_FILE, caption="📄 Private message log")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.incoming & filters.private & ~filters.command(["start" , "help"]) & ~filters.user(OWNER_ID) , group=5)
async def incoming(client: Client, message: Message):
    
    TEXT = [
        ("𝖡𝖾𝗅𝗂𝖾𝗏𝖾 𝗂𝗇 𝗒𝗈𝗎𝗋𝗌𝖾𝗅𝖿. 𝖭𝗈𝗍 𝗂𝗇 𝗍𝗁𝖾 𝗒𝗈𝗎 𝗐𝗁𝗈 𝖻𝖾𝗅𝗂𝖾𝗏𝖾𝗌 𝗂𝗇 𝗆𝖾. 𝖭𝗈𝗍 𝗍𝗁𝖾 𝗆𝖾 𝗐𝗁𝗈 𝖻𝖾𝗅𝗂𝖾𝗏𝖾𝗌 𝗂𝗇 𝗒𝗈𝗎. 𝖡𝖾𝗅𝗂𝖾𝗏𝖾 𝗂𝗇 𝗍𝗁𝖾 𝗒𝗈𝗎 𝗐𝗁𝗈 𝖻𝖾𝗅𝗂𝖾𝗏𝖾𝗌 𝗂𝗇 𝗒𝗈𝗎𝗋𝗌𝖾𝗅𝖿.", "𝖪𝖺𝗆𝗂𝗇𝖺", "𝖳𝖾𝗇𝗀𝖾𝗇 𝖳𝗈𝗉𝗉𝖺 𝖦𝗎𝗋𝗋𝖾𝗇 𝖫𝖺𝗀𝖺𝗇𝗇"),
        ("𝖨𝗍'𝗌 𝗇𝗈𝗍 𝗍𝗁𝖾 𝖿𝖺𝖼𝖾 𝗍𝗁𝖺𝗍 𝗆𝖺𝗄𝖾𝗌 𝗌𝗈𝗆𝖾𝗈𝗇𝖾 𝖺 𝗆𝗈𝗇𝗌𝗍𝖾𝗋, 𝗂𝗍'𝗌 𝗍𝗁𝖾 𝖼𝗁𝗈𝗂𝖼𝖾𝗌 𝗍𝗁𝖾𝗒 𝗆𝖺𝗄𝖾 𝗐𝗂𝗍𝗁 𝗍𝗁𝖾𝗂𝗋 𝗅𝗂𝗏𝖾𝗌.", "𝖭𝖺𝗋𝗎𝗍𝗈 𝖴𝗓𝗎𝗆𝖺𝗄𝗂", "𝖭𝖺𝗋𝗎𝗍𝗈"),
        ("𝖳𝗁𝖾 𝗈𝗇𝗅𝗒 𝗍𝗁𝗂𝗇𝗀 𝗍𝗁𝖺𝗍 𝖼𝖺𝗇 𝖽𝖾𝖿𝖾𝖺𝗍 𝗉𝗈𝗐𝖾𝗋 𝗂𝗌 𝗆𝗈𝗋𝖾 𝗉𝗈𝗐𝖾𝗋. 𝖳𝗁𝖺𝗍 𝗂𝗌 𝗍𝗁𝖾 𝗈𝗇𝖾 𝖼𝗈𝗇𝗌𝗍𝖺𝗇𝗍 𝗂𝗇 𝗍𝗁𝗂𝗌 𝗎𝗇𝗂𝗏𝖾𝗋𝗌𝖾. 𝖧𝗈𝗐𝖾𝗏𝖾𝗋, 𝗍𝗁𝖾𝗋𝖾 𝗂𝗌 𝗇𝗈 𝗉𝗈𝗂𝗇𝗍 𝗂𝗇 𝗉𝗈𝗐𝖾𝗋 𝗂𝖿 𝗂𝗍 𝖼𝗈𝗇𝗌𝗎𝗆𝖾𝗌 𝗂𝗍𝗌𝖾𝗅𝖿.", "𝖨𝗍𝖺𝖼𝗁𝗂 𝖴𝖼𝗁𝗂𝗁𝖺", "𝖭𝖺𝗋𝗎𝗍𝗈"),
        ("𝖭𝗈 𝗈𝗇𝖾 𝗄𝗇𝗈𝗐𝗌 𝗐𝗁𝖺𝗍 𝗍𝗁𝖾 𝖿𝗎𝗍𝗎𝗋𝖾 𝗁𝗈𝗅𝖽𝗌. 𝖳𝗁𝖺𝗍'𝗌 𝗐𝗁𝗒 𝗂𝗍𝗌 𝗉𝗈𝗍𝖾𝗇𝗍𝗂𝖺𝗅 𝗂𝗌 𝗂𝗇𝖿𝗂𝗇𝗂𝗍𝖾.", "𝖱𝗂𝗇𝗍𝖺𝗋𝗈𝗎 𝖮𝗄𝖺𝖻𝖾", "𝖲𝗍𝖾𝗂𝗇𝗌;𝖦𝖺𝗍𝖾"),
        ("𝖣𝗈𝗇'𝗍 𝖿𝗈𝗋𝗀𝖾𝗍. 𝖠𝗅𝗐𝖺𝗒𝗌, 𝗌𝗈𝗆𝖾𝗐𝗁𝖾𝗋𝖾, 𝗌𝗈𝗆𝖾𝗈𝗇𝖾 𝗂𝗌 𝖿𝗂𝗀𝗁𝗍𝗂𝗇𝗀 𝖿𝗈𝗋 𝗒𝗈𝗎. 𝖠𝗌 𝗅𝗈𝗇𝗀 𝖺𝗌 𝗒𝗈𝗎 𝗋𝖾𝗆𝖾𝗆𝖻𝖾𝗋 𝗁𝖾𝗋, 𝗒𝗈𝗎 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖺𝗅𝗈𝗇𝖾.", "𝖬𝖺𝖽𝗈𝗄𝖺 𝖪𝖺𝗇𝖺𝗆𝖾", "𝖯𝗎𝖾𝗅𝗅𝖺 𝖬𝖺𝗀𝗂 𝖬𝖺𝖽𝗈𝗄𝖺 𝖬𝖺𝗀𝗂𝖼𝖺"),
        ("𝖳𝗁𝖾 𝗈𝗇𝗅𝗒 𝗍𝗁𝗂𝗇𝗀 𝗐𝖾'𝗋𝖾 𝖺𝗅𝗅𝗈𝗐𝖾𝖽 𝗍𝗈 𝖽𝗈 𝗂𝗌 𝗍𝗈 𝖻𝖾𝗅𝗂𝖾𝗏𝖾 𝗍𝗁𝖺𝗍 𝗐𝖾 𝗐𝗈𝗇'𝗍 𝗋𝖾𝗀𝗋𝖾𝗍 𝗍𝗁𝖾 𝖼𝗁𝗈𝗂𝖼𝖾 𝗐𝖾 𝗆𝖺𝖽𝖾.", "𝖫𝖾𝗏𝗂 𝖠𝖼𝗄𝖾𝗋𝗆𝖺𝗇", "𝖠𝗍𝗍𝖺𝖼𝗄 𝗈𝗇 𝖳𝗂𝗍𝖺𝗇"),
        ("𝖶𝗁𝖺𝗍𝖾𝗏𝖾𝗋 𝗒𝗈𝗎 𝖽𝗈, 𝖾𝗇𝗃𝗈𝗒 𝗂𝗍 𝗍𝗈 𝗍𝗁𝖾 𝖿𝗎𝗅𝗅𝖾𝗌𝗍. 𝖳𝗁𝖺𝗍 𝗂𝗌 𝗍𝗁𝖾 𝗌𝖾𝖼𝗋𝖾𝗍 𝗈𝖿 𝗅𝗂𝖿𝖾.", "𝖱𝗂𝖽𝖾𝗋 (𝖨𝗌𝗄𝖺𝗇𝖽𝖺𝗋)", "𝖥𝖺𝗍𝖾/𝖹𝖾𝗋𝗈"),
        ("𝖨𝖿 𝗒𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗍𝖺𝗄𝖾 𝗋𝗂𝗌𝗄𝗌, 𝗒𝗈𝗎 𝖼𝖺𝗇'𝗍 𝖼𝗋𝖾𝖺𝗍𝖾 𝖺 𝖿𝗎𝗍𝗎𝗋𝖾.", "𝖬𝗈𝗇𝗄𝖾𝗒 𝖣. 𝖫𝗎𝖿𝖿𝗒", "𝖮𝗇𝖾 𝖯𝗂𝖾𝖼𝖾"),
        ("𝖨𝗇 𝗈𝗋𝖽𝖾𝗋 𝗍𝗈 𝗀𝗋𝗈𝗐, 𝗒𝗈𝗎 𝗆𝗎𝗌𝗍 𝖿𝖺𝖼𝖾 𝗍𝗁𝖾 𝗉𝖺𝗂𝗇 𝗈𝖿 𝗍𝗁𝖾 𝗉𝖺𝗌𝗍. 𝖠𝖼𝖼𝖾𝗉𝗍 𝗂𝗍 𝖺𝗇𝖽 𝗆𝗈𝗏𝖾 𝖿𝗈𝗋𝗐𝖺𝗋𝖽.", "𝖤𝗋𝗓𝖺 𝖲𝖼𝖺𝗋𝗅𝖾𝗍", "𝖥𝖺𝗂𝗋𝗒 𝖳𝖺𝗂𝗅"),
        ("𝖲𝗈𝗆𝖾𝗍𝗂𝗆𝖾𝗌 𝗍𝗁𝖾 𝗍𝗁𝗂𝗇𝗀𝗌 𝗍𝗁𝖺𝗍 𝗆𝖺𝗍𝗍𝖾𝗋 𝗍𝗁𝖾 𝗆𝗈𝗌𝗍 𝖺𝗋𝖾 𝗋𝗂𝗀𝗁𝗍 𝗂𝗇 𝖿𝗋𝗈𝗇𝗍 𝗈𝖿 𝗒𝗈𝗎.", "𝖠𝗌𝗎𝗇𝖺 𝖸𝗎𝗎𝗄𝗂", "𝖲𝗐𝗈𝗋𝖽 𝖠𝗋𝗍 𝖮𝗇𝗅𝗂𝗇𝖾"),
        ("𝖳𝗁𝖾 𝗐𝗈𝗋𝗅𝖽’𝗌 𝗇𝗈𝗍 𝗉𝖾𝗋𝖿𝖾𝖼𝗍, 𝖻𝗎𝗍 𝗂𝗍’𝗌 𝗍𝗁𝖾𝗋𝖾 𝖿𝗈𝗋 𝗎𝗌 𝗍𝗋𝗒𝗂𝗇𝗀 𝗍𝗁𝖾 𝖻𝖾𝗌𝗍 𝗂𝗍 𝖼𝖺𝗇. 𝖳𝗁𝖺𝗍’𝗌 𝗐𝗁𝖺𝗍 𝗆𝖺𝗄𝖾𝗌 𝗂𝗍 𝗌𝗈 𝖽𝖺𝗆𝗇 𝖻𝖾𝖺𝗎𝗍𝗂𝖿𝗎𝗅.", "𝖱𝗈𝗒 𝖬𝗎𝗌𝗍𝖺𝗇𝗀", "𝖥𝗎𝗅𝗅𝗆𝖾𝗍𝖺𝗅 𝖠𝗅𝖼𝗁𝖾𝗆𝗂𝗌𝗍: 𝖡𝗋𝗈𝗍𝗁𝖾𝗋𝗁𝗈𝗈𝖽"),
        ("𝖨𝖿 𝗇𝗈𝖻𝗈𝖽𝗒 𝖼𝖺𝗋𝖾𝗌 𝗍𝗈 𝖺𝖼𝖼𝖾𝗉𝗍 𝗒𝗈𝗎 𝖺𝗇𝖽 𝗐𝖺𝗇𝗍𝗌 𝗒𝗈𝗎 𝗂𝗇 𝗍𝗁𝗂𝗌 𝗐𝗈𝗋𝗅𝖽, 𝖺𝖼𝖼𝖾𝗉𝗍 𝗒𝗈𝗎𝗋𝗌𝖾𝗅𝖿 𝖺𝗇𝖽 𝗒𝗈𝗎 𝗐𝗂𝗅𝗅 𝗌𝖾𝖾 𝗍𝗁𝖺𝗍 𝗒𝗈𝗎 𝖽𝗈𝗇’𝗍 𝗇𝖾𝖾𝖽 𝗍𝗁𝖾𝗆 𝖺𝗇𝖽 𝗍𝗁𝖾𝗂𝗋 𝗌𝖾𝗅𝖿𝗂𝗌𝗁 𝗂𝖽𝖾𝖺𝗌.", "𝖦𝗂𝗇𝗍𝗈𝗄𝗂 𝖲𝖺𝗄𝖺𝗍𝖺", "𝖦𝗂𝗇𝗍𝖺𝗆𝖺"),
        ("𝖶𝗁𝖺𝗍𝖾𝗏𝖾𝗋 𝗒𝗈𝗎 𝖽𝗈, 𝗒𝗈𝗎 𝗌𝗁𝗈𝗎𝗅𝖽 𝖽𝗈 𝗂𝗍 𝗐𝗂𝗍𝗁 𝖺𝗅𝗅 𝗒𝗈𝗎𝗋 𝗁𝖾𝖺𝗋𝗍.", "𝖲𝖺𝖻𝖾𝗋 (𝖠𝗋𝗍𝗈𝗋𝗂𝖺 𝖯𝖾𝗇𝖽𝗋𝖺𝗀𝗈𝗇)", "𝖥𝖺𝗍𝖾/𝗌𝗍𝖺𝗒 𝗇𝗂𝗀𝗁𝗍: 𝖴𝗇𝗅𝗂𝗆𝗂𝗍𝖾𝖽 𝖡𝗅𝖺𝖽𝖾 𝖶𝗈𝗋𝗄𝗌"),
        ("𝖤𝗏𝖾𝗇 𝗂𝖿 𝗍𝗁𝗂𝗇𝗀𝗌 𝖺𝗋𝖾 𝗉𝖺𝗂𝗇𝖿𝗎𝗅 𝖺𝗇𝖽 𝗍𝗈𝗎𝗀𝗁, 𝗉𝖾𝗈𝗉𝗅𝖾 𝗌𝗁𝗈𝗎𝗅𝖽 𝖺𝗉𝗉𝗋𝖾𝖼𝗂𝖺𝗍𝖾 𝗐𝗁𝖺𝗍 𝗂𝗍 𝗆𝖾𝖺𝗇𝗌 𝗍𝗈 𝖻𝖾 𝖺𝗅𝗂𝗏𝖾 𝖺𝗍 𝖺𝗅𝗅.", "𝖸𝖺𝗍𝗈", "𝖭𝗈𝗋𝖺𝗀𝖺𝗆𝗂"),
        ("𝖨'𝖽 𝗋𝖺𝗍𝗁𝖾𝗋 𝖽𝗂𝖾 𝗈𝗇 𝗆𝗒 𝖿𝖾𝖾𝗍 𝗍𝗁𝖺𝗇 𝗅𝗂𝗏𝖾 𝗈𝗇 𝗆𝗒 𝗄𝗇𝖾𝖾𝗌.", "𝖤𝗋𝖾𝗇 𝖸𝖾𝖺𝗀𝖾𝗋", "𝖠𝗍𝗍𝖺𝖼𝗄 𝗈𝗇 𝖳𝗂𝗍𝖺𝗇"),
        ("𝖨 𝖽𝗈𝗇'𝗍 𝗐𝖺𝗇𝗍 𝗍𝗈 𝖼𝗈𝗇𝗊𝗎𝖾𝗋 𝖺𝗇𝗒𝗍𝗁𝗂𝗇𝗀. 𝖨 𝗃𝗎𝗌𝗍 𝗍𝗁𝗂𝗇𝗄 𝗍𝗁𝖾 𝗀𝗎𝗒 𝗐𝗂𝗍𝗁 𝗍𝗁𝖾 𝗆𝗈𝗌𝗍 𝖿𝗋𝖾𝖾𝖽𝗈𝗆 𝗂𝗇 𝗍𝗁𝗂𝗌 𝗐𝗁𝗈𝗅𝖾 𝗈𝖼𝖾𝖺𝗇... 𝗂𝗌 𝗍𝗁𝖾 𝖯𝗂𝗋𝖺𝗍𝖾 𝖪𝗂𝗇𝗀!", "𝖬𝗈𝗇𝗄𝖾𝗒 𝖣. 𝖫𝗎𝖿𝖿𝗒", "𝖮𝗇𝖾 𝖯𝗂𝖾𝖼𝖾"),
        ("𝖨𝗍'𝗌 𝗇𝗈𝗍 𝗍𝗁𝖾 𝗌𝗍𝗋𝖾𝗇𝗀𝗍𝗁 𝗈𝖿 𝖺 𝗁𝖾𝗋𝗈 𝗍𝗁𝖺𝗍 𝗆𝖺𝗍𝗍𝖾𝗋𝗌, 𝖻𝗎𝗍 𝗍𝗁𝖾 𝗌𝗍𝗋𝖾𝗇𝗀𝗍𝗁 𝗈𝖿 𝗍𝗁𝖾𝗂𝗋 𝗁𝖾𝖺𝗋𝗍.", "𝖭𝖺𝗍𝗌𝗎 𝖣𝗋𝖺𝗀𝗇𝖾𝖾𝗅", "𝖥𝖺𝗂𝗋𝗒 𝖳𝖺𝗂𝗅"),
        ("𝖳𝗁𝖾 𝗐𝗈𝗋𝗅𝖽 𝗂𝗌 𝗆𝖾𝗋𝖼𝗂𝗅𝖾𝗌𝗌, 𝖺𝗇𝖽 𝗂𝗍'𝗌 𝖺𝗅𝗌𝗈 𝗏𝖾𝗋𝗒 𝖻𝖾𝖺𝗎𝗍𝗂𝖿𝗎𝗅.", "𝖬𝗂𝗄𝖺𝗌𝖺 𝖠𝖼𝗄𝖾𝗋𝗆𝖺𝗇", "𝖠𝗍𝗍𝖺𝖼𝗄 𝗈𝗇 𝖳𝗂𝗍𝖺𝗇"),
        ("𝖭𝗈 𝗈𝗇𝖾 𝗄𝗇𝗈𝗐𝗌 𝗐𝗁𝖺𝗍 𝗍𝗁𝖾 𝖿𝗎𝗍𝗎𝗋𝖾 𝗁𝗈𝗅𝖽𝗌. 𝖳𝗁𝖺𝗍'𝗌 𝗐𝗁𝗒 𝗐𝖾 𝖼𝖺𝗇 𝗇𝖾𝗏𝖾𝗋 𝗌𝖺𝗒 𝗀𝗈𝗈𝖽𝖻𝗒𝖾.", "𝖨𝗌𝖺𝖺𝖼 𝖭𝖾𝗍𝖾𝗋𝗈", "𝖧𝗎𝗇𝗍𝖾𝗋 𝗑 𝖧𝗎𝗇𝗍𝖾𝗋"),
        ("𝖨𝖿 𝗒𝗈𝗎 𝗐𝖺𝗇𝗇𝖺 𝗆𝖺𝗄𝖾 𝗉𝖾𝗈𝗉𝗅𝖾 𝖽𝗋𝖾𝖺𝗆, 𝗒𝗈𝗎'𝗏𝖾 𝗀𝗈𝗍𝗍𝖺 𝗌𝗍𝖺𝗋𝗍 𝖻𝗒 𝖻𝖾𝗅𝗂𝖾𝗏𝗂𝗇𝗀 𝗂𝗇 𝗍𝗁𝖺𝗍 𝖽𝗋𝖾𝖺𝗆 𝗒𝗈𝗎𝗋𝗌𝖾𝗅𝖿!", "𝖲𝗁𝗈𝗒𝗈 𝖧𝗂𝗇𝖺𝗍𝖺", "𝖧𝖺𝗂𝗄𝗒𝗎𝗎!!"),
        ("𝖡𝖾𝗂𝗇𝗀 𝗐𝖾𝖺𝗄 𝗂𝗌 𝗇𝗈𝗍𝗁𝗂𝗇𝗀 𝗍𝗈 𝖻𝖾 𝖺𝗌𝗁𝖺𝗆𝖾𝖽 𝗈𝖿. 𝖲𝗍𝖺𝗒𝗂𝗇𝗀 𝗐𝖾𝖺𝗄 𝗂𝗌.", "𝖨𝗓𝗎𝗄𝗎 𝖬𝗂𝖽𝗈𝗋𝗂𝗒𝖺", "𝖬𝗒 𝖧𝖾𝗋𝗈 𝖠𝖼𝖺𝖽𝖾𝗆𝗂𝖺"),
        ("𝖤𝗏𝖾𝗇 𝗂𝖿 𝗒𝗈𝗎’𝗋𝖾 𝗐𝖾𝖺𝗄, 𝗍𝗁𝖾𝗋𝖾 𝖺𝗋𝖾 𝗆𝗂𝗋𝖺𝖼𝗅𝖾𝗌 𝗒𝗈𝗎 𝖼𝖺𝗇 𝗌𝖾𝗂𝗓𝖾 𝗐𝗂𝗍𝗁 𝗒𝗈𝗎𝗋 𝗁𝖺𝗇𝖽𝗌 𝗂𝖿 𝗒𝗈𝗎 𝖿𝗂𝗀𝗁𝗍 𝗈𝗇 𝗍𝗈 𝗍𝗁𝖾 𝗏𝖾𝗋𝗒 𝖾𝗇𝖽.", "𝖦𝗈𝗇 𝖥𝗋𝖾𝖾𝖼𝗌𝗌", "𝖧𝗎𝗇𝗍𝖾𝗋 𝗑 𝖧𝗎𝗇𝗍𝖾𝗋"),
        ("𝖳𝗁𝖾𝗋𝖾 𝖺𝗋𝖾 𝗇𝗈 𝗌𝗁𝗈𝗋𝗍𝖼𝗎𝗍𝗌 𝗂𝗇 𝗅𝗂𝖿𝖾. 𝖳𝗈 𝗐𝗂𝗇, 𝗒𝗈𝗎 𝗁𝖺𝗏𝖾 𝗍𝗈 𝗐𝗈𝗋𝗄 𝗁𝖺𝗋𝖽, 𝖿𝖺𝖼𝖾 𝗒𝗈𝗎𝗋 𝖽𝖾𝗆𝗈𝗇𝗌, 𝖺𝗇𝖽 𝗇𝖾𝗏𝖾𝗋 𝗀𝗂𝗏𝖾 𝗎𝗉.", "𝖸𝖺𝗆𝗂 𝖲𝗎𝗄𝖾𝗁𝗂𝗋𝗈", "𝖡𝗅𝖺𝖼𝗄 𝖢𝗅𝗈𝗏𝖾𝗋"),
        ("𝖳𝗋𝗎𝖾 𝗌𝗍𝗋𝖾𝗇𝗀𝗍𝗁 𝖼𝗈𝗆𝖾𝗌 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝗁𝖾𝖺𝗋𝗍, 𝗇𝗈𝗍 𝗃𝗎𝗌𝗍 𝖻𝗋𝗎𝗍𝖾 𝖿𝗈𝗋𝖼𝖾.", "𝖤𝖽𝗐𝖺𝗋𝖽 𝖤𝗅𝗋𝗂𝖼", "𝖥𝗎𝗅𝗅𝗆𝖾𝗍𝖺𝗅 𝖠𝗅𝖼𝗁𝖾𝗆𝗂𝗌𝗍"),
        ("𝖳𝗁𝖾 𝖿𝖾𝖺𝗋 𝗈𝖿 𝖽𝖾𝖺𝗍𝗁 𝖿𝗈𝗅𝗅𝗈𝗐𝗌 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝖿𝖾𝖺𝗋 𝗈𝖿 𝗅𝗂𝖿𝖾. 𝖠 𝗆𝖺𝗇 𝗐𝗁𝗈 𝗅𝗂𝗏𝖾𝗌 𝖿𝗎𝗅𝗅𝗒 𝗂𝗌 𝗉𝗋𝖾𝗉𝖺𝗋𝖾𝖽 𝗍𝗈 𝖽𝗂𝖾 𝖺𝗍 𝖺𝗇𝗒 𝗍𝗂𝗆𝖾.", "𝖲𝗁𝗂𝗇𝗈𝖻𝗎 𝖲𝖾𝗇𝗌𝗎𝗂", "𝖸𝗎 𝖸𝗎 𝖧𝖺𝗄𝗎𝗌𝗁𝗈"),
        ("𝖨𝗇 𝗍𝗁𝗂𝗌 𝗐𝗈𝗋𝗅𝖽, 𝗐𝗁𝖾𝗋𝖾𝗏𝖾𝗋 𝗍𝗁𝖾𝗋𝖾 𝗂𝗌 𝗅𝗂𝗀𝗁𝗍 – 𝗍𝗁𝖾𝗋𝖾 𝖺𝗋𝖾 𝖺𝗅𝗌𝗈 𝗌𝗁𝖺𝖽𝗈𝗐𝗌. 𝖠𝗌 𝗅𝗈𝗇𝗀 𝖺𝗌 𝗍𝗁𝖾 𝖼𝗈𝗇𝖼𝖾𝗉𝗍 𝗈𝖿 𝗐𝗂𝗇𝗇𝖾𝗋𝗌 𝖾𝗑𝗂𝗌𝗍𝗌, 𝗍𝗁𝖾𝗋𝖾 𝗆𝗎𝗌𝗍 𝖺𝗅𝗌𝗈 𝖻𝖾 𝗅𝗈𝗌𝖾𝗋𝗌.", "𝖫𝖾𝗅𝗈𝗎𝖼𝗁 𝗏𝗂 𝖡𝗋𝗂𝗍𝖺𝗇𝗇𝗂𝖺", "𝖢𝗈𝖽𝖾 𝖦𝖾𝖺𝗌𝗌"),
        ("𝖨’𝖽 𝗋𝖺𝗍𝗁𝖾𝗋 𝗍𝗋𝗎𝗌𝗍 𝖺𝗇𝖽 𝗋𝖾𝗀𝗋𝖾𝗍 𝗍𝗁𝖺𝗇 𝖽𝗈𝗎𝖻𝗍 𝖺𝗇𝖽 𝗋𝖾𝗀𝗋𝖾𝗍.", "𝖪𝗂𝗋𝗂𝗍𝗌𝗎𝗀𝗎 𝖤𝗆𝗂𝗒𝖺", "𝖥𝖺𝗍𝖾/𝖹𝖾𝗋𝗈"),
        ("𝖸𝗈𝗎 𝗌𝗁𝗈𝗎𝗅𝖽 𝗇𝖾𝗏𝖾𝗋 𝗀𝗂𝗏𝖾 𝗎𝗉 𝗈𝗇 𝗅𝗂𝖿𝖾, 𝗇𝗈 𝗆𝖺𝗍𝗍𝖾𝗋 𝗁𝗈𝗐 𝗒𝗈𝗎 𝖿𝖾𝖾𝗅. 𝖭𝗈 𝗆𝖺𝗍𝗍𝖾𝗋 𝗁𝗈𝗐 𝗁𝖺𝗋𝖽 𝗍𝗁𝗂𝗇𝗀𝗌 𝗀𝖾𝗍, 𝗒𝗈𝗎 𝗁𝖺𝗏𝖾 𝗍𝗈 𝗁𝗈𝗅𝖽 𝗈𝗇 𝗍𝗈 𝗒𝗈𝗎𝗋 𝗅𝗂𝖿𝖾, 𝗇𝗈 𝗆𝖺𝗍𝗍𝖾𝗋 𝗐𝗁𝖺𝗍.", "𝖬𝗂𝗌𝖺𝗄𝗂 𝖳𝖺𝗄𝖺𝗁𝖺𝗌𝗁𝗂", "𝖩𝗎𝗇𝗃𝗈𝗎 𝖱𝗈𝗆𝖺𝗇𝗍𝗂𝖼𝖺"),
        ("𝖳𝗁𝖾 𝗍𝗋𝗎𝖾 𝗆𝖾𝖺𝗌𝗎𝗋𝖾 𝗈𝖿 𝖺 𝗌𝗁𝗂𝗇𝗈𝖻𝗂 𝗂𝗌 𝗇𝗈𝗍 𝗁𝗈𝗐 𝗁𝖾 𝗅𝗂𝗏𝖾𝗌 𝖻𝗎𝗍 𝗁𝗈𝗐 𝗁𝖾 𝖽𝗂𝖾𝗌. 𝖨𝗍'𝗌 𝗇𝗈𝗍 𝗐𝗁𝖺𝗍 𝗍𝗁𝖾𝗒 𝖽𝗈 𝗂𝗇 𝗅𝗂𝖿𝖾, 𝖻𝗎𝗍 𝗐𝗁𝖺𝗍 𝗍𝗁𝖾𝗒 𝖽𝗂𝖽 𝖻𝖾𝖿𝗈𝗋𝖾 𝖽𝗒𝗂𝗇𝗀 𝗍𝗁𝖺𝗍 𝗉𝗋𝗈𝗏𝖾𝗌 𝗍𝗁𝖾𝗂𝗋 𝗐𝗈𝗋𝗍𝗁.", "𝖩𝗂𝗋𝖺𝗂𝗒𝖺", "𝖭𝖺𝗋𝗎𝗍𝗈"),
    ]

    if message.from_user.id != OWNER_ID:
        await message.reply_text(random.choice(TEXT))
    else :
        return


@app.on_message(filters.command("spawnbot") & filters.user(OWNER_ID))
async def spawn_bot(client: Client, message: Message):
    """Spawn a NEW bot process with the given TOKEN / NAME / DBNAME while keeping this one running.

    Usage:
        /spawnbot TOKEN=123:ABC NAME=MyNewBot DBNAME=newdb
    """
    if len(message.command) < 2:
        await message.reply_text("Usage: /spawnbot key=value ...\nRequired: TOKEN, NAME. Optional: DBNAME")
        return

    required = {"TOKEN", "NAME"}
    allowed = {"TOKEN", "DBNAME", "NAME"}
    cfg = {}
    for pair in message.text.split()[1:]:
        if "=" not in pair:
            await message.reply_text(f"Invalid segment `{pair}`. Use key=value format.")
            return
        k, v = pair.split("=", 1)
        k = k.upper()
        if k not in allowed:
            await message.reply_text(f"Invalid key `{k}`. Allowed: TOKEN, DBNAME, NAME")
            return
        cfg[k] = v

    if not required.issubset(cfg):
        await message.reply_text("TOKEN and NAME are required.")
        return

    # Create configs directory if needed
    configs_dir = "bot_configs"
    os.makedirs(configs_dir, exist_ok=True)
    config_path = os.path.join(configs_dir, f"{cfg['NAME']}.json")

    try:
        with open(config_path, "w") as f:
            json.dump(cfg, f, indent=2)
    except OSError as e:
        await message.reply_text(f"❌ Failed to write config: {e}")
        return

    try:
        subprocess.Popen([sys.executable, sys.argv[0], config_path])
    except Exception as e:
        await message.reply_text(f"❌ Failed to spawn bot: {e}")
        return

    await message.reply_text(f"✅ Bot process started for {cfg['NAME']}.")


# ================= Existing owner commands =================

@app.on_message(filters.command("setbotconfig") & filters.user(OWNER_ID))
async def set_bot_config(client: Client, message: Message):
    """Owner-only: Update TOKEN, DBNAME, NAME then restart bot.

    Usage: /setbotconfig TOKEN=123:ABC DBNAME=mydb NAME=MyBot"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /setbotconfig key=value ...\nAllowed keys: TOKEN, DBNAME, NAME")
        return

    allowed = {"TOKEN", "DBNAME", "NAME"}
    updates = {}
    for pair in message.text.split()[1:]:
        if "=" not in pair:
            await message.reply_text(f"Invalid segment `{pair}`. Use key=value format.")
            return
        k, v = pair.split("=", 1)
        k = k.upper()
        if k not in allowed:
            await message.reply_text(f"Invalid key `{k}`. Allowed keys: TOKEN, DBNAME, NAME")
            return
        updates[k] = v

# Read existing config
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    cfg.update(updates)
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except OSError as e:
        await message.reply_text(f"❌ Failed to write config: {e}")
        return

    await message.reply_text("✅ Config updated, restarting bot...")
    await asyncio.sleep(2)
    os.execv(sys.executable, [sys.executable] + sys.argv)


# ✅ MAIN BOT STARTUP LOGIC (this must be OUTSIDE all functions)

async def main():
    await app.start()
    await send_startup_message()
    print("✅ Bot is running...")
    await idle()
    await app.stop()

# This should be at the BOTTOM of your Let.py file
if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        print(f"❌ An error occurred: {e}")
