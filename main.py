from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# تعريف الأزرار
def get_main_keyboard():
    kb = [
        [KeyboardButton(text="📸 حل اختبار (صورة)")],
        [KeyboardButton(text="📝 بحث/واجب (نص)")],
        [KeyboardButton(text="👤 حسابي")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "أهلاً بك في البوت التعليمي الذكي! كيف يمكنني مساعدتك اليوم؟",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text == "👤 حسابي":
        await message.answer("رصيدك الحالي: 0 نقطة.")
    else:
        await message.answer("جاري المعالجة...")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
