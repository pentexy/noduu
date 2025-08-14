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
TOKEN = "8182599533:AAFTTkD6Ag3j4XeegkYtPi2YObX4_lHfPuk"
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

OWNER_ID = 7690821053

DB = "riorandi"

# LOG_FILE will be set after config is loaded
LOG_FILE = f"{NAME}.txt"


#================================================================================================================================#

client = AsyncIOMotorClient("mongodb+srv://Axxa:Axxay@cluster0.veadsay.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
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

    TEXT = ("none")
    

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
