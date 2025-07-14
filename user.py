import asyncio
from telethon import TelegramClient, events, functions, types

api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"

client = TelegramClient("clone_userbot", api_id, api_hash)

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

        # Username cloning logic
        if user.username:
            original_username = user.username
            tried_usernames = [original_username]

            try:
                # Try exact username first
                await client(functions.account.UpdateUsernameRequest(username=original_username))
                print(f"Username set exactly: {original_username}")
            except Exception as e:
                print(f"Exact username failed: {e}")

                # Define minimal replacements
                replacements = [
                    ("ii", "ll"),
                    ("ll", "ii"),
                    ("0", "o"),
                    ("o", "0"),
                    ("I", "l"),
                    ("l", "I"),
                    ("s", "5"),
                    ("5", "s"),
                    ("a", "e"),
                    ("e", "a"),
                ]

                # Try each replacement only once
                for old, new in replacements:
                    if old in original_username:
                        tweaked_username = original_username.replace(old, new, 1)
                        if tweaked_username not in tried_usernames:
                            try:
                                await client(functions.account.UpdateUsernameRequest(username=tweaked_username))
                                print(f"Username changed minimally to: {tweaked_username}")
                                break  # Success
                            except Exception as e:
                                print(f"Failed with {old}->{new}: {e}")
                                tried_usernames.append(tweaked_username)
                else:
                    # Fallback: add underscore
                    fallback_username = original_username + "_"
                    try:
                        await client(functions.account.UpdateUsernameRequest(username=fallback_username))
                        print(f"Username fallback to: {fallback_username}")
                    except Exception as e:
                        print(f"All username tweaks failed: {e}")
        else:
            print("No username to copy.")

        # Clone profile photos
        photos = await client.get_profile_photos(user.id)
        count = 0
        for photo in photos:
            file = await client.download_media(photo)
            await client(functions.photos.UploadProfilePhotoRequest(
                file=await client.upload_file(file)
            ))
            count += 1
            print(f"Set photo {count}")

        await event.reply(f"**Cloned {user.first_name} with {count} DPs. Username updated if possible.**")
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
