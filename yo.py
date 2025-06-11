import asyncio
from pyrogram import Client

async def remove_bot_dp():
    bot_token = input("Enter your bot token: ").strip()

    app = Client("bot_session", bot_token=bot_token)

    async with app:
        photos = await app.get_profile_photos("me")
        if photos.total_count == 0:
            print("❌ Bot has no profile picture.")
        else:
            await app.delete_profile_photos(photos.photos[0].file_id)
            print("✅ Bot's profile picture has been removed.")

if __name__ == "__main__":
    asyncio.run(remove_bot_dp())
