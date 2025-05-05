from instagrapi import Client
from datetime import datetime
import time
import threading
import getpass

afk_data = {
    "status": False,
    "reason": None,
    "since": None
}

cl = Client()
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

def format_afk_message():
    elapsed = datetime.now() - afk_data["since"]
    hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    offline_time = f"{hours}h {minutes}m {seconds}s"
    return (
        "ᴍʏ ᴏᴡɴᴇʀ ɪꜱ ᴀꜰᴋ !\n"
        f"ʀᴇᴀꜱᴏɴ : {afk_data['reason']}\n"
        f"ᴏꜰꜰʟɪɴᴇ ᴘᴀʀᴀᴍᴇᴛᴇʀ : {offline_time}"
    )

def check_and_handle_commands(thread, msg, sender_id):
    text = msg.text.lower() if msg.text else ""

    if sender_id == owner_id:
        if text.startswith("/afk "):
            afk_data["reason"] = msg.text[5:].strip()
            afk_data["since"] = datetime.now()
            afk_data["status"] = True
            cl.direct_send("ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴀꜰᴋ ! 😾", [thread.id])
        elif text == "/back":
            afk_data["status"] = False
            afk_data["reason"] = None
            afk_data["since"] = None
            cl.direct_send("✅ ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ ɴᴏᴡ.", [thread.id])
    elif afk_data["status"] and not text.startswith("/"):
        cl.direct_send(format_afk_message(), [sender_id])

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
