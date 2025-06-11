import asyncio
from pyrogram import Client

async def remove_bot_dp():
    api_id = int(input("Enter your API ID: ").strip())
    api_hash = input("Enter your API HASH: ").strip()
    bot_token = input("Enter your BOT TOKEN: ").strip()

    app = Client(
        name="bot_session",
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token
    )

    async with app:
        photos = await app.get_profile_photos("me")
        if photos.total_count == 0:
            print("❌ Bot has no profile picture.")
        else:
            await app.delete_profile_photos(photos.photos[0].file_id)
            print("✅ Bot's profile picture has been removed.")

if __name__ == "__main__":
    asyncio.run(remove_bot_dp())
