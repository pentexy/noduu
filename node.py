from instagrapi import Client
from datetime import datetime, timedelta
import getpass
import time

# AFK storage
afk_data = {
    "status": False,
    "reason": None,
    "since": None
}

# Stats storage
start_time = datetime.now()
stats = {
    "messages": 0,
    "afk_replies": 0
}

cl = Client()

# Login
username = input("Enter Instagram Username: ")
password = getpass.getpass("Enter Password: ")

try:
    cl.login(username, password)
    me = cl.account_info()
    owner_id = me.pk
    owner_username = me.username
    print("✅ ʟᴏɢɪɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ.")
except Exception as e:
    print(f"❌ ʟᴏɢɪɴ ꜰᴀɪʟᴇᴅ: {e}")
    exit()

# Notify @uchiha.rar on start
try:
    uchiha_id = cl.user_id_from_username("uchiha.rar")
    cl.direct_send("ʏᴏᴜꜱᴇʀʙᴏᴛ ɪꜱ ꜱᴛᴀʀᴛᴇᴅ ᴀɴᴅ ʟɪᴠᴇ ✅", [uchiha_id])
    print("✅ ɴᴏᴛɪꜰɪᴇᴅ @uchiha.rar.")
except Exception as e:
    print(f"❌ ɴᴏᴛɪꜰʏ ꜰᴀɪʟᴇᴅ: {e}")

def format_afk_message():
    elapsed = datetime.now() - afk_data["since"]
    hours, rem = divmod(int(elapsed.total_seconds()), 3600)
    mins, secs = divmod(rem, 60)
    time_str = f"{hours}ʜ {mins}ᴍ {secs}ꜱ"
    return (
        "ᴍʏ ᴏᴡɴᴇʀ ɪꜱ ᴀꜰᴋ !\n"
        f"ʀᴇᴀꜱᴏɴ : {afk_data['reason']}\n"
        f"ᴏꜰꜰʟɪɴᴇ ᴘᴀʀᴀᴍᴇᴛᴇʀ : {time_str}"
    )

def get_uptime():
    uptime = datetime.now() - start_time
    return str(timedelta(seconds=int(uptime.total_seconds())))

def send_stats(thread_id):
    afk_status = "⟪ ᴏɴ ⟫" if afk_data["status"] else "⟪ ᴏꜰꜰ ⟫"
    message = (
        f"ʙᴏᴛ ꜱᴛᴀᴛꜱ:\n"
        f"⟶ ᴜᴘᴛɪᴍᴇ : {get_uptime()}\n"
        f"⟶ ᴍᴇꜱꜱᴀɢᴇꜱ ʀᴇᴄᴇɪᴠᴇᴅ : {stats['messages']}\n"
        f"⟶ ᴀꜰᴋ ʀᴇᴘʟɪᴇꜱ : {stats['afk_replies']}\n"
        f"⟶ ᴀꜰᴋ ꜱᴛᴀᴛᴜꜱ : {afk_status}\n"
        f"⟶ ᴏᴡɴᴇʀ : @{owner_username}"
    )
    try:
        cl.direct_answer(thread_id, message)
    except Exception as e:
        print(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇɴᴅ .ꜱᴛᴀᴛꜱ: {e}")

def check_and_handle_commands(thread, msg, sender_id):
    try:
        text = msg.text.strip() if msg.text else ""
        stats["messages"] += 1

        if sender_id == owner_id:
            if text.startswith("/afk "):
                afk_data["reason"] = text[5:].strip()
                afk_data["since"] = datetime.now()
                afk_data["status"] = True
                cl.direct_answer(thread.id, "ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴀꜰᴋ ! 😾")
            elif text == "/back":
                afk_data["status"] = False
                afk_data["reason"] = None
                afk_data["since"] = None
                cl.direct_answer(thread.id, "✅ ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ ɴᴏᴡ.")
            elif text == ".stats":
                send_stats(thread.id)
        elif afk_data["status"] and not text.startswith("/"):
            cl.direct_answer(thread.id, format_afk_message())
            stats["afk_replies"] += 1
    except Exception as e:
        print(f"⚠️ ᴇʀʀᴏʀ ʜᴀɴᴅʟɪɴɢ ᴄᴏᴍᴍᴀɴᴅꜱ: {e}")

def handle_messages():
    print("ʙᴏᴛ ɪꜱ ʀᴜɴɴɪɴɢ. ꜰᴜʟʟ ᴀꜰᴋ ᴄᴏɴᴛʀᴏʟ + ꜱᴛᴀᴛꜱ.")
    last_checked = {}

    while True:
        try:
            inbox = cl.direct_threads()
            for thread in inbox:
                if thread.id not in last_checked:
                    last_checked[thread.id] = 0

                new_messages = [
                    msg for msg in thread.messages
                    if msg.timestamp.timestamp() > last_checked[thread.id]
                ]

                for msg in new_messages:
                    check_and_handle_commands(thread, msg, msg.user_id)

                if new_messages:
                    last_checked[thread.id] = max(
                        msg.timestamp.timestamp() for msg in new_messages
                    )
        except Exception as e:
            print(f"⚠️ ᴇʀʀᴏʀ ɪɴ ᴍᴇꜱꜱᴀɢᴇ ʜᴀɴᴅʟɪɴɢ ʟᴏᴏᴘ: {e}")
        time.sleep(10)

handle_messages()
