from pyrogram import Client, filters
import asyncio

api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"

app = Client("clone_userbot", api_id=api_id, api_hash=api_hash)

@app.on_message(filters.command("clone", ".") & filters.me & filters.reply)
async def clone_profile(client, message):
    replied_user = message.reply_to_message.from_user
    if not replied_user:
        await message.reply("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴛᴏ ᴄʟᴏɴᴇ ᴛʜᴇᴍ**")
        return

    user = await client.get_users(replied_user.id)

    # Change name
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    await client.update_profile(first_name=first_name, last_name=last_name)
    
    # Change bio
    if user.bio:
        await client.update_profile(bio=user.bio)

    # Download and set all profile photos
    photos = client.get_profile_photos(user.id)
    count = 0
    async for photo in photos:
        file = await client.download_media(photo.file_id)
        await client.set_profile_photo(file)
        count += 1

    await message.reply(f"**ᴄʟᴏɴᴇᴅ {user.first_name} ᴡɪᴛʜ {count} ᴅᴘs.**")

@app.on_message(filters.command("fuckup", ".") & filters.me)
async def fuckup(client, message):
    # Reset name and bio
    await client.update_profile(first_name="ᴅᴇʟᴇᴛᴇᴅ", last_name="")
    await client.update_profile(bio="")

    # Delete all profile photos
    photos = client.get_profile_photos("me")
    async for photo in photos:
        await client.delete_profile_photos(photo.file_id)

    await message.reply("**ғᴜᴄᴋᴜᴘ**\n**ᴀʟʟ ᴄʟᴏɴᴇᴅ ᴅᴀᴛᴀ ʀᴇᴍᴏᴠᴇᴅ.**")

async def main():
    print("**ᴍɪssɪᴏɴ : sᴛᴀʀᴛɪɴɢ**")
    await app.start()
    print("**ᴍɪssɪᴏɴ : ʀᴇᴀᴅʏ**")

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
