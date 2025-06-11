import asyncio
from pyrogram import Client
import aiohttp
from tempfile import NamedTemporaryFile

API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"

async def download_image(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to download image. Status: {resp.status}")
            temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(await resp.read())
            temp_file.close()
            return temp_file.name

async def update_bot_dp():
    target_bot_token = input("🔑 Enter the bot token you want to update DP for: ").strip()
    image_url = input("🖼️ Enter the image URL: ").strip()

    try:
        image_path = await download_image(image_url)
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return

    app = Client("target_bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=target_bot_token)

    async with app:
        try:
            await app.set_profile_photo(photo=image_path)
            print("✅ Bot profile picture successfully updated.")
        except Exception as e:
            print(f"❌ Failed to update bot profile photo: {e}")

if __name__ == "__main__":
    asyncio.run(update_bot_dp())
