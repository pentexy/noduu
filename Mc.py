import asyncio
import os
import subprocess
import tempfile
import qrcode
from io import BytesIO
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiofiles

# Bot configuration
API_TOKEN = '8426732884:AAFhNDDLGkRFIm-HfJi4TnQh9v8VHFwr56E'
AUTHORIZED_USERS = [7339063037]  # Pre-authorized admin
ADMIN_USER_ID = 7339063037

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Server control functions
def start_server():
    try:
        # Start server in a screen session
        result = subprocess.run([
            'screen', '-dmS', 'minecraft', 
            'bash', '/home/ubuntu/mc/start.sh'
        ], capture_output=True, text=True, timeout=30)
        
        # Wait a bit for server to start
        time.sleep(10)
        return True, "Server started successfully"
        
    except subprocess.TimeoutExpired:
        return False, "Server start timed out"
    except Exception as e:
        return False, f"Error starting server: {str(e)}"

def stop_server():
    try:
        # Execute the stop script
        result = subprocess.run([
            'bash', '/home/ubuntu/mc/stop.sh'
        ], capture_output=True, text=True, timeout=30)
        
        return True, "Server stopped successfully"
        
    except subprocess.TimeoutExpired:
        return False, "Server stop timed out"
    except Exception as e:
        return False, f"Error stopping server: {str(e)}"

def get_players():
    # Implement your player list command
    try:
        # This is a placeholder - implement based on your server
        result = subprocess.run(['sudo', '-u', 'minecraft', 'mc-status', 'localhost', 'status'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, result.stdout
        return False, "Could not retrieve player list"
    except subprocess.TimeoutExpired:
        return False, "Timeout while fetching player list"

def create_backup():
    # Implement your backup creation command
    backup_dir = "/home/mc/backups"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/backup_{timestamp}.tar.gz"
    
    # Create backup (adjust paths as needed)
    result = subprocess.run([
        'tar', '-czf', backup_file, 
        '/home/minecraft/server/world',
        '/home/minecraft/server/world_nether',
        '/home/minecraft/server/world_the_end',
        '/home/minecraft/server/server.properties'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return True, backup_file
    return False, "Backup creation failed"

# Split large files into chunks
def split_file(file_path, max_size_mb=200):
    max_size = max_size_mb * 1024 * 1024  # Convert to bytes
    file_size = os.path.getsize(file_path)
    
    if file_size <= max_size:
        return [file_path]
    
    parts = []
    part_num = 1
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(max_size)
            if not chunk:
                break
                
            part_path = f"{file_path}.part{part_num}"
            with open(part_path, 'wb') as part_file:
                part_file.write(chunk)
                
            parts.append(part_path)
            part_num += 1
    
    return parts

# Generate QR code for login
def generate_qr_login(user_id):
    # Create a unique token for this login session
    token = f"MINECRAFT_BOT_LOGIN:{user_id}:{datetime.now().timestamp()}"
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes buffer
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return buf, token

# Format text with special font
def format_text(text):
    font_map = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 
        'y': 'ʏ', 'z': 'ᴢ', ' ': ' ', 
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', 
        '8': '8', '9': '9'
    }
    
    formatted = ''.join(font_map.get(c.lower(), c) for c in text)
    return formatted

# Create inline buttons
def create_inline_buttons():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="🟢 sᴛᴀʀᴛ", callback_data="start_server"),
        types.InlineKeyboardButton(text="🔴 sᴛᴏᴘ", callback_data="stop_server"),
        types.InlineKeyboardButton(text="👥 ᴘʟᴀʏᴇʀs", callback_data="list_players"),
        types.InlineKeyboardButton(text="💾 ʙᴀᴄᴋᴜᴘ", callback_data="create_backup"),
        types.InlineKeyboardButton(text="📊 sᴛᴀᴛs", callback_data="server_stats"),
        types.InlineKeyboardButton(text="🔄 ʀᴇsᴛᴀʀᴛ", callback_data="restart_server")
    )
    builder.adjust(2)  # 2 buttons per row
    return builder.as_markup()

# Animation helper
async def animate_message(message, base_text, edit_message=None):
    if edit_message is None:
        edit_message = message
    
    for i in range(1, 4):
        dots = "." * i
        await edit_message.edit_text(f"{base_text}{dots}")
        await asyncio.sleep(0.5)
    
    return edit_message

# Command handlers
@dp.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.answer("🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ. ᴘʟᴇᴀsᴇ sᴄᴀɴ ᴛʜᴇ ǫʀ ᴄᴏᴅᴇ ᴛᴏ ʟᴏɢɪɴ.")
        return
    
    await message.answer(
        format_text("minecraft server control panel"),
        reply_markup=create_inline_buttons()
    )

@dp.message(Command("add"))
async def cmd_add(message: Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴀᴅᴅ ᴜsᴇʀs.")
        return
    
    try:
        # Extract user ID from command
        args = message.text.split()
        if len(args) < 2:
            await message.answer("⚠️ ᴜsᴀɢᴇ: /add <ᴜsᴇʀ_ɪᴅ>")
            return
        
        user_id = int(args[1])
        if user_id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.append(user_id)
            await message.answer(f"✅ ᴜsᴇʀ {user_id} ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
        else:
            await message.answer(f"ℹ️ ᴜsᴇʀ {user_id} ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ.")
    except ValueError:
        await message.answer("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ. ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɴᴜᴍᴇʀɪᴄ ᴜsᴇʀ ɪᴅ.")

@dp.message(Command("login"))
async def cmd_login(message: Message):
    if message.from_user.id in AUTHORIZED_USERS:
        await message.answer("✅ ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ʟᴏɢɢᴇᴅ ɪɴ")
        return
    
    # Generate QR code
    qr_buffer, token = generate_qr_login(message.from_user.id)
    
    # Send QR code to user
    sent_message = await message.answer_photo(
        photo=types.BufferedInputFile(qr_buffer.getvalue(), filename="qrcode.png"),
        caption="🔐 sᴄᴀɴ ᴛʜɪs ǫʀ ᴄᴏᴅᴇ ᴛᴏ ʟᴏɢɪɴ\n\n" +
               "ᴛʜᴇ ǫʀ ᴄᴏᴅᴇ ʜᴀs ʙᴇᴇɴ sʜᴏᴡɴ ɪɴ ᴛʜᴇ sᴇʀᴠᴇʀ ᴛᴇʀᴍɪɴᴀʟ"
    )
    
    # Display QR code in terminal
    qr = qrcode.QRCode()
    qr.add_data(token)
    qr.print_ascii()
    
    print(f"\nLogin token: {token}")
    print("Waiting for QR code scan...")
    
    # Wait for admin to confirm the login
    await message.answer("⏳ ᴡᴀɪᴛɪɴɢ ғᴏʀ ᴀᴅᴍɪɴ ᴀᴘᴘʀᴏᴠᴀʟ...")
    
    # In a real implementation, you'd have the admin confirm via a button
    # For this example, we'll simulate approval after 30 seconds
    await asyncio.sleep(30)
    
    # Check if admin approved (in real implementation, this would be based on a button click)
    if message.from_user.id not in AUTHORIZED_USERS:
        # Simulate admin adding the user
        AUTHORIZED_USERS.append(message.from_user.id)
        await message.answer("✅ ʟᴏɢɪɴ sᴜᴄᴄᴇssғᴜʟ! ʏᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ sᴇʀᴠᴇʀ ᴄᴏɴᴛʀᴏʟs.")
        await sent_message.delete()

# Callback query handlers
@dp.callback_query(lambda c: c.data == "start_server")
async def start_server_callback(callback: CallbackQuery):
    if callback.from_user.id not in AUTHORIZED_USERS:
        await callback.answer("🚫 ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ")
        return
    
    msg = await callback.message.answer("🔄 sᴛᴀʀᴛɪɴɢ sᴇʀᴠᴇʀ")
    msg = await animate_message(callback.message, "🔄 sᴛᴀʀᴛɪɴɢ sᴇʀᴠᴇʀ", msg)
    
    success, output = start_server()
    
    if success:
        await msg.edit_text("✅ sᴇʀᴠᴇʀ sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
    else:
        await msg.edit_text(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴛᴀʀᴛ sᴇʀᴠᴇʀ:\n{output}")
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "stop_server")
async def stop_server_callback(callback: CallbackQuery):
    if callback.from_user.id not in AUTHORIZED_USERS:
        await callback.answer("🚫 ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ")
        return
    
    msg = await callback.message.answer("🔄 sᴛᴏᴘᴘɪɴɢ sᴇʀᴠᴇʀ")
    msg = await animate_message(callback.message, "🔄 sᴛᴏᴘᴘɪɴɢ sᴇʀᴠᴇʀ", msg)
    
    success, output = stop_server()
    
    if success:
        await msg.edit_text("✅ sᴇʀᴠᴇʀ sᴛᴏᴘᴘᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
    else:
        await msg.edit_text(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴛᴏᴘ sᴇʀᴠᴇʀ:\n{output}")
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "list_players")
async def list_players_callback(callback: CallbackQuery):
    if callback.from_user.id not in AUTHORIZED_USERS:
        await callback.answer("🚫 ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ")
        return
    
    msg = await callback.message.answer("🔄 ғᴇᴛᴄʜɪɴɢ ᴘʟᴀʏᴇʀ ʟɪsᴛ")
    msg = await animate_message(callback.message, "🔄 ғᴇᴛᴄʜɪɴɢ ᴘʟᴀʏᴇʀ ʟɪsᴛ", msg)
    
    success, output = get_players()
    
    if success:
        await msg.edit_text(f"👥 ᴘʟᴀʏᴇʀs ᴏɴʟɪɴᴇ:\n{output}")
    else:
        await msg.edit_text(f"❌ ᴜɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴘʟᴀʏᴇʀ ʟɪsᴛ:\n{output}")
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "server_stats")
async def server_stats_callback(callback: CallbackQuery):
    if callback.from_user.id not in AUTHORIZED_USERS:
        await callback.answer("🚫 ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ")
        return
    
    msg = await callback.message.answer("📊 ɢᴇᴛᴛɪɴɢ sᴇʀᴠᴇʀ sᴛᴀᴛs")
    msg = await animate_message(callback.message, "📊 ɢᴇᴛᴛɪɴɢ sᴇʀᴠᴇʀ sᴛᴀᴛs", msg)
    
    # Get server stats (placeholder implementation)
    try:
        # Get disk usage
        disk = subprocess.run(['df', '-h', '/home/minecraft'], capture_output=True, text=True)
        disk_output = disk.stdout if disk.returncode == 0 else "Unable to get disk usage"
        
        # Get memory usage
        memory = subprocess.run(['free', '-h'], capture_output=True, text=True)
        memory_output = memory.stdout if memory.returncode == 0 else "Unable to get memory usage"
        
        # Get CPU usage
        cpu = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
        cpu_output = cpu.stdout if cpu.returncode == 0 else "Unable to get CPU usage"
        
        stats_message = f"💾 ᴅɪsᴋ ᴜsᴀɢᴇ:\n{disk_output.splitlines()[1] if disk_output != 'Unable to get disk usage' else disk_output}\n\n"
        stats_message += f"🧠 ᴍᴇᴍᴏʀʏ ᴜsᴀɢᴇ:\n{memory_output.splitlines()[1] if memory_output != 'Unable to get memory usage' else memory_output}\n\n"
        stats_message += f"⚡ ᴄᴘᴜ ᴜsᴀɢᴇ:\n{cpu_output.splitlines()[0] if cpu_output != 'Unable to get CPU usage' else cpu_output}"
        
        await msg.edit_text(stats_message)
    except Exception as e:
        await msg.edit_text(f"❌ ᴇʀʀᴏʀ ɢᴇᴛᴛɪɴɢ sᴇʀᴠᴇʀ sᴛᴀᴛs: {str(e)}")
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "restart_server")
async def restart_server_callback(callback: CallbackQuery):
    if callback.from_user.id not in AUTHORIZED_USERS:
        await callback.answer("🚫 ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ")
        return
    
    msg = await callback.message.answer("🔄 ʀᴇsᴛᴀʀᴛɪɴɢ sᴇʀᴠᴇʀ")
    msg = await animate_message(callback.message, "🔄 ʀᴇsᴛᴀʀᴛɪɴɢ sᴇʀᴠᴇʀ", msg)
    
    # Stop server first
    success, output = stop_server()
    if not success:
        await msg.edit_text(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴛᴏᴘ sᴇʀᴠᴇʀ:\n{output}")
        await callback.answer()
        return
    
    # Start server
    success, output = start_server()
    if success:
        await msg.edit_text("✅ sᴇʀᴠᴇʀ ʀᴇsᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
    else:
        await msg.edit_text(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇsᴛᴀʀᴛ sᴇʀᴠᴇʀ:\n{output}")
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "create_backup")
async def create_backup_callback(callback: CallbackQuery):
    if callback.from_user.id not in AUTHORIZED_USERS:
        await callback.answer("🚫 ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ")
        return
    
    msg = await callback.message.answer("🔄 ᴄʀᴇᴀᴛɪɴɢ ʙᴀᴄᴋᴜᴘ")
    msg = await animate_message(callback.message, "🔄 ᴄʀᴇᴀᴛɪɴɢ ʙᴀᴄᴋᴜᴘ", msg)
    
    success, result = create_backup()
    
    if success:
        await msg.edit_text("📦 ʙᴀᴄᴋᴜᴘ ᴄʀᴇᴀᴛᴇᴅ. ɴᴏᴡ ᴜᴘʟᴏᴀᴅɪɴɢ...")
        
        # Split file if too large
        parts = split_file(result)
        
        for i, part in enumerate(parts):
            part_name = os.path.basename(part)
            if len(parts) > 1:
                part_text = f" 📦 #PART{i+1}"
            else:
                part_text = ""
            
            try:
                async with aiofiles.open(part, 'rb') as file:
                    file_data = await file.read()
                    await callback.message.answer_document(
                        document=types.BufferedInputFile(
                            file_data, 
                            filename=part_name
                        ),
                        caption=f"✅ ʙᴀᴄᴋᴜᴘ sᴜᴄᴄᴇssғᴜʟ{part_text}"
                    )
            
            except Exception as e:
                await callback.message.answer(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʙᴀᴄᴋᴜᴘ: {str(e)}")
            
            # Clean up part file
            if part != result:  # Don't delete the original backup yet
                os.unlink(part)
        
        # Clean up original backup file after sending
        os.unlink(result)
            
        await msg.delete()
    else:
        await msg.edit_text(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʙᴀᴄᴋᴜᴘ:\n{result}")
    
    await callback.answer()

# Scheduled backup task
async def scheduled_backup():
    while True:
        await asyncio.sleep(3 * 60 * 60)  # 3 hours
        
        if AUTHORIZED_USERS:
            # Create backup
            success, result = create_backup()
            
            if success:
                # Send notification to all authorized users
                for user_id in AUTHORIZED_USERS:
                    try:
                        await bot.send_message(
                            user_id, 
                            "🔄 ᴀᴜᴛᴏᴍᴀᴛɪᴄ ʙᴀᴄᴋᴜᴘ ɪɴ ᴘʀᴏɢʀᴇss..."
                        )
                    except:
                        continue  # Skip if user can't be reached
                
                # Split file if too large
                parts = split_file(result)
                
                for i, part in enumerate(parts):
                    part_name = os.path.basename(part)
                    if len(parts) > 1:
                        part_text = f" 📦 #PART{i+1}"
                    else:
                        part_text = ""
                    
                    try:
                        async with aiofiles.open(part, 'rb') as file:
                            file_data = await file.read()
                            for user_id in AUTHORIZED_USERS:
                                try:
                                    await bot.send_document(
                                        user_id,
                                        document=types.BufferedInputFile(
                                            file_data, 
                                            filename=part_name
                                        ),
                                        caption=f"✅ ᴀᴜᴛᴏ ʙᴀᴄᴋᴜᴘ sᴜᴄᴄᴇssғᴜʟ{part_text}"
                                    )
                                except:
                                    continue  # Skip if user can't be reached
                    
                    except Exception as e:
                        for user_id in AUTHORIZED_USERS:
                            try:
                                await bot.send_message(
                                    user_id,
                                    f"❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴀᴜᴛᴏ ʙᴀᴄᴋᴜᴘ: {str(e)}"
                                )
                            except:
                                continue
                    
                    # Clean up part file
                    if part != result:  # Don't delete the original backup yet
                        os.unlink(part)
                
                # Clean up original backup file after sending
                os.unlink(result)
            else:
                for user_id in AUTHORIZED_USERS:
                    try:
                        await bot.send_message(
                            user_id,
                            f"❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴀᴜᴛᴏ ʙᴀᴄᴋᴜᴘ:\n{result}"
                        )
                    except:
                        continue

# Inline query handler
@dp.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    if inline_query.from_user.id not in AUTHORIZED_USERS:
        return
    
    # Create inline query results
    results = [
        InlineQueryResultArticle(
            id="1",
            title="🟢 Start Server",
            input_message_content=InputTextMessageContent(
                message_text="Starting server..."
            ),
            description="Start the Minecraft server"
        ),
        InlineQueryResultArticle(
            id="2",
            title="🔴 Stop Server",
            input_message_content=InputTextMessageContent(
                message_text="Stopping server..."
            ),
            description="Stop the Minecraft server"
        ),
        InlineQueryResultArticle(
            id="3",
            title="💾 Create Backup",
            input_message_content=InputTextMessageContent(
                message_text="Creating backup..."
            ),
            description="Create a server backup"
        )
    ]
    
    await inline_query.answer(results, cache_time=1)

# Main function
async def main():
    # Start the scheduled backup task
    asyncio.create_task(scheduled_backup())
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
