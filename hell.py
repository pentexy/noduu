import asyncio, logging, json, os, random
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputPeerChannel, InputReportReasonSpam, InputReportReasonOther

# === CONFIG ===
BOT_TOKEN = "8185730588:AAHkdJRV9ghuRb7M10sGnL5_8wW2SAypuuo"
OWNER_ID = 7072373613
MAX_TELEGRAMS = 10
DATA_FILE = "data/accounts.json"

# === INIT ===
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

# === FILE SETUP ===
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
        [InlineKeyboardButton(text="🚩 Report a Post", callback_data="report_post")],
    ])

# === TEMP STATE ===
temp_sessions = {}
is_reporting = False

# === BOT HANDLERS ===
@router.message(F.text == "/start")
async def start_cmd(msg: types.Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.answer("⛔️ Unauthorized.")
    await msg.answer("👑 Welcome, Owner. Choose an action:", reply_markup=main_menu_kb())

@router.callback_query(F.data == "add_telegram")
async def handle_add_telegram(call: CallbackQuery):
    accs = load_accounts()
    if len(accs["telegrams"]) >= MAX_TELEGRAMS:
        await call.message.answer("🚫 Max Telegram accounts reached!")
    else:
        await call.message.answer("📨 Send in this format:\n<code>+phone:api_id:api_hash</code>", parse_mode="HTML")
    await call.answer()

@router.message(F.text.regexp(r"\+\d+:\d+:.+"))
async def receive_telegram_cred(msg: types.Message):
    if msg.from_user.id in temp_sessions:
        return await msg.answer("⏳ Complete OTP verification first.")
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
        await msg.answer("📲 OTP sent. Reply with the 5-6 digit code.")
    except Exception as e:
        await msg.answer(f"❌ Failed: {e}")

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
        await msg.answer("✅ Telegram account saved!")
        logging.info(f"[LOGIN] {temp['phone']}")
        await temp["client"].disconnect()
    except Exception as e:
        await msg.answer(f"❌ OTP failed: {e}")
    finally:
        temp_sessions.pop(msg.from_user.id, None)

# === REPORTING SYSTEM ===
@router.callback_query(F.data == "report_post")
async def ask_post_url(call: CallbackQuery):
    global is_reporting
    if is_reporting:
        await call.message.answer("⏳ Reporting already running.")
    else:
        await call.message.answer("🔗 Send the post link (channel/message):\nExample:\nhttps://t.me/channel/123")
    await call.answer()

@router.message(F.text.regexp(r"https://t\.me/.+"))
async def handle_report_url(msg: types.Message):
    global is_reporting
    if is_reporting:
        return
    is_reporting = True
    link = msg.text.strip()
    accs = load_accounts()["telegrams"]
    if not accs:
        is_reporting = False
        return await msg.answer("❌ No Telegram accounts logged in.")

    for index, acc in enumerate(accs):
        try:
            client = TelegramClient(StringSession(acc["session"]), int(acc["api_id"]), acc["api_hash"])
            await client.connect()
            entity = await client.get_entity(link)
            reasons = [
                InputReportReasonSpam(),
                InputReportReasonOther()
            ]
            reason = random.choice(reasons)
            await client(ReportRequest(peer=entity, id=[], reason=reason, message="Abusive content."))
            await msg.answer(f"✅ Report #{index+1} sent from account.")
            await client.disconnect()
            await asyncio.sleep(random.uniform(1.5, 3.5))
        except Exception as e:
            await msg.answer(f"⚠️ Failed report #{index+1}: {e}")
            logging.error(f"[REPORT FAIL] #{index+1} - {e}")
    is_reporting = False
    await msg.answer("🏁 Reporting finished.")

# === RUN ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="reporter.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(main())
