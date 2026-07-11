import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from openai import OpenAI

TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📸 حل اختبار")],
        [KeyboardButton(text="🔍 حل بحث")],
        [KeyboardButton(text="📝 حل واجب")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("أهلاً بك! اختر الخدمة:", reply_markup=get_main_keyboard())

@dp.message(F.text.in_({"📸 حل اختبار", "🔍 حل بحث", "📝 حل واجب"}))
async def handle_choice(message: types.Message):
    await message.answer(f"تم اختيار {message.text}. أرسل السؤال الآن (صورة أو نص).", reply_markup=ReplyKeyboardRemove())

# التعامل مع الصور
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("جاري التحليل.. انتظر.")
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "حل هذا السؤال بدقة:"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}]
    )
    await message.answer(response.choices[0].message.content + "\n\n/start للعودة.")

# التعامل مع النصوص (البحث والواجب)
@dp.message(F.text)
async def handle_text(message: types.Message):
    # نتجاهل أمر /start لأنه معرف فوق
    if message.text == "/start": return
    
    await message.answer("جاري البحث وكتابة الإجابة.. ⏳")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": message.text}]
    )
    await message.answer(response.choices[0].message.content + "\n\n/start للعودة.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
