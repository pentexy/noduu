import asyncio
import random
from telethon import TelegramClient, events, functions, types

api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"

client = TelegramClient("clone_userbot", api_id, api_hash)

# Replacement mapping for username tweaks
replacement_map = {
    "I": "l",
    "i": "l",
    "O": "0",
    "o": "0",
    "a": "@",
    "A": "@",
    "s": "5",
    "S": "5",
    "E": "3",
    "e": "3",
}

def tweak_username(username):
    new_username = ""
    for char in username:
        if char in replacement_map and random.random() < 0.5:
            new_username += replacement_map[char]
        else:
            new_username += char
    return new_username

@client.on(events.NewMessage(pattern=r"\.clone", outgoing=True))
async def clone_profile(event):
    print("Clone command triggered.")

    if not event.is_reply:
        await event.reply("**Reply to a user to clone them.**")
        print("No reply found.")
        return

    replied = await event.get_reply_message()
    if not replied.sender:
        await event.reply("**Can't fetch user.**")
        print("No user in reply.")
        return

    user = await client.get_entity(replied.sender_id)
    print(f"Fetched user: {user.first_name}")

    try:
        # Change name
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        await client(functions.account.UpdateProfileRequest(first_name=first_name, last_name=last_name))
        print(f"Updated name to: {first_name} {last_name}")

        # Change bio
        if isinstance(user, types.User):
            about = (await client(functions.users.GetFullUserRequest(user.id))).full_user.about
            if about:
                await client(functions.account.UpdateProfileRequest(about=about))
                print("Updated bio.")
            else:
                print("No bio found.")

        # Tweak username
        if user.username:
            tweaked_username = tweak_username(user.username)
            # Update username
            try:
                await client(functions.account.UpdateUsernameRequest(username=tweaked_username))
                print(f"Username changed to: {tweaked_username}")
            except Exception as e:
                print(f"Failed to update username: {e}")
        else:
            print("No username to tweak.")

        # Download and set profile photos
        photos = await client.get_profile_photos(user.id)
        count = 0
        for photo in photos:
            file = await client.download_media(photo)
            await client(functions.photos.UploadProfilePhotoRequest(
                file=await client.upload_file(file)
            ))
            count += 1
            print(f"Set photo {count}")

        await event.reply(f"**Cloned {user.first_name} with {count} DPs. Username tweaked.**")
        print("Clone completed.")

    except Exception as e:
        await event.reply(f"Error during clone: {e}")
        print(f"Clone error: {e}")

@client.on(events.NewMessage(pattern=r"\.fuckup", outgoing=True))
async def fuckup(event):
    print("Fuckup command triggered.")
    try:
        # Reset name and bio
        await client(functions.account.UpdateProfileRequest(first_name="Deleted", last_name=""))
        await client(functions.account.UpdateProfileRequest(about=""))
        print("Name and bio deleted.")

        # Delete all profile photos
        photos = await client.get_profile_photos("me")
        count = 0
        for photo in photos:
            await client(functions.photos.DeletePhotosRequest(id=[photo]))
            count += 1
            print(f"Deleted photo {count}")

        await event.reply("**Fuckup completed. All cloned data removed.**")
        print("Fuckup completed.")

    except Exception as e:
        await event.reply(f"Error during fuckup: {e}")
        print(f"Fuckup error: {e}")

async def main():
    print("Mission starting.")
    await client.start()
    print("Mission ready.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
