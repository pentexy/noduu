from instagrapi import Client
from datetime import datetime
import getpass
import time

# Temp AFK state
afk_data = {
    "status": False,
    "reason": None,
    "since": None
}

cl = Client()

# Login
username = input("Enter Instagram Username: ")
password = getpass.getpass("Enter Password: ")

try:
    cl.login(username, password)
    me = cl.account_info()
    owner_id = me.pk
    print("✅ ʟᴏɢɪɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ.")
except Exception as e:
    print(f"❌ ʟᴏɢɪɴ ꜰᴀɪʟᴇᴅ: {e}")
    exit()

# Notify @uchiha.rar bot is live
try:
    uchiha_id = cl.user_id_from_username("uchiha.rar")
    cl.direct_send("ʏᴏᴜꜱᴇʀʙᴏᴛ ɪꜱ ꜱᴛᴀʀᴛᴇᴅ ᴀɴᴅ ʟɪᴠᴇ ✅", [uchiha_id])
    print("✅ ɴᴏᴛɪꜰɪᴇᴅ @uchiha.rar ᴛʜᴀᴛ ʙᴏᴛ ɪꜱ ʟɪᴠᴇ.")
except Exception as e:
    print(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ɴᴏᴛɪꜰʏ @uchiha.rar: {e}")

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

def check_and_handle_commands(thread, msg, sender_id):
    text = msg.text.lower() if msg.text else ""

    if sender_id == owner_id:
        if text.startswith("/afk "):
            afk_data["reason"] = msg.text[5:].strip()
            afk_data["since"] = datetime.now()
            afk_data["status"] = True
            cl.direct_answer(thread.id, "ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴀꜰᴋ ! 😾")
        elif text == "/back":
            afk_data["status"] = False
            afk_data["reason"] = None
            afk_data["since"] = None
            cl.direct_answer(thread.id, "✅ ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ ɴᴏᴡ.")
    elif afk_data["status"] and not text.startswith("/"):
        cl.direct_answer(thread.id, format_afk_message())

def handle_messages():
    print("ʙᴏᴛ ɪꜱ ʀᴜɴɴɪɴɢ. ꜰᴜʟʟ ᴀꜰᴋ ᴄᴏɴᴛʀᴏʟ ᴠɪᴀ ᴅᴍ/ɢʀᴏᴜᴘꜱ.")
    last_checked = {}

    while True:
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

        time.sleep(10)

handle_messages()
