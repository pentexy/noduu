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
        # Get current profile photos
        photos = await app.invoke(
            app._client.functions.photos.GetUserPhotos(
                user_id="me",
                offset=0,
                max_id=0,
                limit=1
            )
        )

        if not photos.photos:
            print("❌ Bot has no profile picture.")
            return

        # Delete the first profile photo
        photo_id = photos.photos[0].id
        await app.invoke(
            app._client.functions.photos.DeletePhotos(
                id=[photos.photos[0].id]
            )
        )

        print("✅ Bot's profile picture has been removed.")

if __name__ == "__main__":
    asyncio.run(remove_bot_dp())
