import asyncio
import os
from pyrogram import Client
from pyrogram.errors import RPCError

# Convert normal text to bold Unicode (basic)
def bold(text: str) -> str:
    return ''.join(chr(ord(c) + 0x1D400 - ord('A')) if 'A' <= c <= 'Z'
                   else chr(ord(c) + 0x1D41A - ord('a')) if 'a' <= c <= 'z'
                   else c for c in text)

# Visual blockquote style
def blockquote(text: str) -> str:
    lines = text.split('\n')
    return "\n".join([f"┃  {line}" for line in lines])

async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("╭────────────────────────────╮")
    print("│        ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ        │")
    print("╰────────────────────────────╯\n")

    try:
        api_id = int(input("⟶ ᴇɴᴛᴇʀ ᴀᴘɪ ɪᴅ: "))
        api_hash = input("⟶ ᴇɴᴛᴇʀ ᴀᴘɪ ʜᴀꜱʜ: ")
        bot_token = input("⟶ ᴇɴᴛᴇʀ ʙᴏᴛ ᴛᴏᴋᴇɴ: ")
        print()

        async with Client("ᴍʏ_ʙᴏᴛ", api_id=api_id, api_hash=api_hash, bot_token=bot_token) as app:
            me = await app.get_me()
            print(blockquote(f"{bold('Connected as')} @{me.username}"))

            name = input("\n⟶ ɴᴇᴡ ʙᴏᴛ ɴᴀᴍᴇ (ꜱᴋɪᴘ ᴛᴏ ʟᴇᴀᴠᴇ): ").strip()
            bio = input("⟶ ɴᴇᴡ ʙɪᴏ (ꜱᴋɪᴘ ᴛᴏ ʟᴇᴀᴠᴇ): ").strip()
            desc = input("⟶ ɴᴇᴡ ᴅᴇꜱᴄʀɪᴘᴛɪᴏɴ (ꜱᴋɪᴘ ᴛᴏ ʟᴇᴀᴠᴇ): ").strip()

            print(f"\n{bold('<BOT UPDATE STATUS>')}")
            print("────────────────────────────")

            if name:
                await app.set_bot_name(name=name)
                print(blockquote(f"{bold('✓ NAME UPDATED')}"))

            if bio:
                await app.set_bot_short_description(short_description=bio)
                print(blockquote(f"{bold('✓ BIO UPDATED')}"))

            if desc:
                await app.set_bot_description(description=desc)
                print(blockquote(f"{bold('✓ DESCRIPTION UPDATED')}"))

            if not (name or bio or desc):
                print(blockquote(f"{bold('No changes made.')}"))

    except RPCError as e:
        print(f"\n{bold('<ERROR>')}")
        print("────────────")
        print(blockquote(str(e)))

    except Exception as e:
        print(f"\n{bold('<UNEXPECTED ERROR>')}")
        print("──────────────────────")
        print(blockquote(str(e)))

if __name__ == "__main__":
    asyncio.run(main())
