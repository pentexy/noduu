import asyncio
import logging
from aiogram import Bot, Dispatcher, types, html
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
    BotCommandScopeDefault
)
from aiogram.filters.callback_data import CallbackData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotConfigState(StatesGroup):
    WAITING_FOR_BOT_INPUT = State()

class BotConfigCallback(CallbackData, prefix="bot_config"):
    action: str

class BotManagerBot:
    def __init__(self, main_bot_token: str):
        self.main_bot = Bot(token=main_bot_token)
        self.dp = Dispatcher()
        self.current_bot: Bot | None = None
        
        self.register_handlers()

    def register_handlers(self):
        self.dp.message(CommandStart())(self.handle_start)
        self.dp.message(Command("connect"))(self.handle_connect)
        self.dp.message(Command("disconnect"))(self.handle_disconnect)
        self.dp.callback_query(BotConfigCallback.filter())(self.handle_config_callback)
        self.dp.message(BotConfigState.WAITING_FOR_BOT_INPUT)(self.handle_bot_input)

    async def handle_start(self, message: types.Message):
        text = html.bold(
            "Welcome to Bot Manager! 🤖\n\n"
            "To Change Bot Details, First Connect Your Bot Using:\n"
            "/connect bot_token"
        )
        await message.answer(text, parse_mode="HTML")

    async def handle_connect(self, message: types.Message, state: FSMContext):
        if self.current_bot:
            await message.answer(html.bold(
                "🚨 You Already Have A Bot Connected. Please Disconnect It First Using /disconnect Before Connecting A New Bot."
            ), parse_mode="HTML")
            return

        parts = message.text.split()
        if len(parts) != 2:
            await message.answer(html.bold("Please Use This Format: /connect bot_token"), parse_mode="HTML")
            return

        try:
            new_bot = Bot(token=parts[1])
            bot_info = await new_bot.get_me()
            self.current_bot = new_bot
            bot_name = bot_info.username

            await message.answer(
                f"<b>@{bot_name} Connected Successfully! Choose An Action:</b>",
                reply_markup=self.build_config_keyboard(), parse_mode="HTML"
            )
        except Exception as e:
            await message.answer(f"Failed To Connect Bot. Error: {str(e)}")


    async def handle_disconnect(self, message: types.Message):
        if not self.current_bot:
            await message.answer(html.bold("Please Connect A Bot First."), parse_mode="HTML")
            return

        self.current_bot = None
        await message.answer(html.bold("Successfully Disconnected The Connected Bot."), parse_mode="HTML")
    
    def build_config_keyboard(self) -> InlineKeyboardMarkup:
        actions = [
            ("🤖 Set Bot Name", "set_name"),
            ("📋 Set Bot Commands", "set_commands"),
            ("📝 Set Bot Description", "set_description"),
            ("📑 Set Short Description", "set_short_description"),
        ]
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=label, callback_data=BotConfigCallback(action=action).pack())]
                for label, action in actions
            ]
        )

    async def handle_config_callback(
        self, callback: types.CallbackQuery, callback_data: BotConfigCallback, state: FSMContext
    ):
        if not self.current_bot:
            await callback.message.answer(html.bold("Please Connect A Bot First Using /connect"), parse_mode="HTML")
            await callback.answer()
            return

        prompts = {
            "set_name": "Enter The New Name For Your Bot:",
            "set_commands": "Send Bot Commands In Format:\ncommand1 - Description1\ncommand2 - Description2",
            "set_description": "Enter The New Bot Description:",
            "set_short_description": "Enter The New Short Description For Your Bot:",
        }

        prompt_text = html.bold(prompts[callback_data.action])
        await callback.message.answer(prompt_text, parse_mode="HTML")
        await state.update_data(action=callback_data.action)
        await state.set_state(BotConfigState.WAITING_FOR_BOT_INPUT)
        await callback.answer()

    async def handle_bot_input(self, message: types.Message, state: FSMContext):
        if not self.current_bot:
            await message.answer(html.bold("Please Connect A Bot First Using /connect"), parse_mode="HTML")
            await state.clear()
            return

        state_data = await state.get_data()
        action = state_data.get("action")

        try:
            if action == "set_name":
                await self.current_bot.set_my_name(name=message.text)
                await message.answer(f"<b>Bot Name Updated To:</b>\n\n{message.text}", parse_mode="HTML")
            elif action == "set_commands":
                await self.update_bot_commands(message)
            elif action == "set_description":
                await self.current_bot.set_my_description(description=message.text)
                await message.answer(html.bold(f"Bot Description Updated To:\n\n{message.text}"), parse_mode="HTML")
            elif action == "set_short_description":
                await self.current_bot.set_my_short_description(short_description=message.text)
                await message.answer(html.bold(f"Bot Short Description Updated To:\n\n{message.text}"), parse_mode="HTML")
        except Exception as e:
            await message.answer(f"Failed To Update Bot {action.replace('_', ' ')}: {str(e)}")

        await state.clear()

    async def update_bot_commands(self, message: types.Message):
        command_lines = message.text.splitlines()
        bot_commands = [
            BotCommand(command=cmd.strip(), description=desc.strip())
            for line in command_lines if ' - ' in line
            for cmd, desc in [line.split(' - ', 1)]
        ]
        await self.current_bot.set_my_commands(bot_commands, scope=BotCommandScopeDefault())
        await message.answer(html.bold("Bot Commands Updated Successfully!"), parse_mode="HTML")

    async def run(self):
        try:
            await self.dp.start_polling(self.main_bot)
        except Exception as e:
            logger.error(f"Error running bot: {e}")

async def main():
    bot_manager = BotManagerBot("8191195022:AAFbr7_8xTpW3lTnt4MiTQgzJVOcrBWFAWc")
    await bot_manager.run()

if __name__ == "__main__":
    asyncio.run(main())

