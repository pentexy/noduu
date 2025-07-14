import asyncio
from telethon import TelegramClient, events

api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"

client = TelegramClient("clone_userbot", api_id, api_hash)

@client.on(events.NewMessage(pattern=r"\.clone"))
async def clone(event):
    print("Clone command triggered.")
    if not event.is_reply:
        await event.reply("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴛᴏ ᴄʟᴏɴᴇ ᴛʜᴇᴍ**")
        print("No reply found.")
        return

    replied = await event.get_reply_message()
    user = await client.get_entity(replied.sender_id)
    print(f"Fetched user: {user.first_name}")

    try:
        # Change name
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        await client(functions.account.UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name
        ))
        print(f"Updated name to: {first_name} {last_name}")

        # Change bio
        if user.about:
            await client(functions.account.UpdateProfileRequest(about=user.about))
            print("Updated bio.")
        else:
            print("No bio to update.")

        # Get all profile photos
        photos = await client.get_profile_photos(user)
        count = 0
        for photo in photos:
            file = await client.download_media(photo, file="dp.jpg")
            await client(functions.photos.UploadProfilePhotoRequest(
                file=await client.upload_file("dp.jpg")
            ))
            print(f"Set photo {count+1}")
            count += 1

        await event.reply(f"**ᴄʟᴏɴᴇᴅ {first_name} ᴡɪᴛʜ {count} ᴅᴘs.**")
        print("Clone completed.")

    except Exception as e:
        await event.reply(f"Error during clone: {e}")
        print(f"Clone error: {e}")

@client.on(events.NewMessage(pattern=r"\.fuckup"))
async def fuckup(event):
    print("Fuckup command triggered.")
    try:
        # Reset name and bio
        await client(functions.account.UpdateProfileRequest(first_name="ᴅᴇʟᴇᴛᴇᴅ", last_name=""))
        await client(functions.account.UpdateProfileRequest(about=""))
        print("Name and bio deleted.")

        # Delete all profile photos
        photos = await client.get_profile_photos('me')
        count = 0
        for photo in photos:
            await client(functions.photos.DeletePhotosRequest(id=[photo]))
            print(f"Deleted photo {count+1}")
            count += 1

        await event.reply("**ғᴜᴄᴋᴜᴘ**\n**ᴀʟʟ ᴄʟᴏɴᴇᴅ ᴅᴀᴛᴀ ʀᴇᴍᴏᴠᴇᴅ.**")
        print("Fuckup completed.")

    except Exception as e:
        await event.reply(f"Error during fuckup: {e}")
        print(f"Fuckup error: {e}")

async def main():
    print("**ᴍɪssɪᴏɴ : sᴛᴀʀᴛɪɴɢ**")
    await client.start()
    print("**ᴍɪssɪᴏɴ : ʀᴇᴀᴅʏ**")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
