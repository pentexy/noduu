import asyncio, logging, json, os
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# === CONFIG ===
BOT_TOKEN = "8185730588:AAHkdJRV9ghuRb7M10sGnL5_8wW2SAypuuo"
OWNER_ID = 7072373613
MAX_TELEGRAMS = 10
DATA_FILE = "data/accounts.json"

# === INIT ===
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# === DATA ===
if not os.path.exists(DATA_FILE):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump({"telegrams": []}, f)

def load_accounts():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_accounts(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add Telegram Account", callback_data="add_telegram")],
    ])

# === TEMP SESSIONS ===
temp_sessions = {}

# === HANDLERS ===
@router.message(F.text == "/start")
async def start_cmd(msg: types.Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.answer("⛔️ You are not authorized to use this bot.")
    await msg.answer("Welcome, Owner! 👑\nChoose an action:", reply_markup=main_menu_kb())

@router.callback_query(F.data == "add_telegram")
async def handle_add_telegram(call: CallbackQuery):
    accs = load_accounts()
    if len(accs["telegrams"]) >= MAX_TELEGRAMS:
        await call.message.answer("🚫 Maximum Telegram accounts reached!")
    else:
        await call.message.answer("📨 Send Telegram credentials:\nFormat:\n<code>+phone:api_id:api_hash</code>", parse_mode="HTML")
    await call.answer()

@router.message(F.text.regexp(r"\+\d+:\d+:.+"))
async def receive_telegram_cred(msg: types.Message):
    if msg.from_user.id in temp_sessions:
        return await msg.answer("⏳ Please complete your current OTP verification first.")
    try:
        phone, api_id, api_hash = msg.text.strip().split(":")
        session = StringSession()
        client = TelegramClient(session, int(api_id), api_hash)
        await client.connect()
        await client.send_code_request(phone)
        temp_sessions[msg.from_user.id] = {
            "client": client,
            "session": session,
            "phone": phone,
            "api_id": api_id,
            "api_hash": api_hash
        }
        await msg.answer("📲 OTP sent to your Telegram app.\nPlease reply with the 5-6 digit code.")
    except Exception as e:
        await msg.answer(f"❌ Failed to send code: {e}")

@router.message(F.text.regexp(r"^\d{5,6}$"))
async def handle_telegram_otp(msg: types.Message):
    if msg.from_user.id not in temp_sessions:
        return
    temp = temp_sessions[msg.from_user.id]
    try:
        await temp["client"].sign_in(temp["phone"], msg.text.strip())
        session_str = temp["client"].session.save()
        accs = load_accounts()
        accs["telegrams"].append({
            "session": session_str,
            "api_id": temp["api_id"],
            "api_hash": temp["api_hash"]
        })
        save_accounts(accs)
        await msg.answer("✅ Telegram account logged in and saved!")
        logging.info(f"[TELEGRAM] Logged in: {temp['phone']}")
        await temp["client"].disconnect()
    except Exception as e:
        await msg.answer(f"❌ OTP failed: {e}")
    finally:
        temp_sessions.pop(msg.from_user.id, None)

# === RUN ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="telegram_reporter.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(main())
