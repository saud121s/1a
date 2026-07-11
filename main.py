import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI
from docx import Document

# إعدادات البوت
TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_sessions = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 بحث أو واجب")], [KeyboardButton(text="📸 حل اختبار")]], resize_keyboard=True)
    await message.answer("أهلاً بك! اختر الخدمة:", reply_markup=kb)

@dp.message(F.text == "🔍 بحث أو واجب")
async def ask_for_data(message: types.Message):
    user_sessions[message.from_user.id] = "task"
    await message.answer("أرسل بياناتك (الاسم، الجامعة، الدكتور، الرقم) وموضوع البحث.")

@dp.message(F.text == "📸 حل اختبار")
async def ask_for_photo(message: types.Message):
    user_sessions[message.from_user.id] = "quiz"
    await message.answer("أرسل صورة السؤال وسأحله فوراً.")

@dp.message(F.text)
async def process_text(message: types.Message):
    if user_sessions.get(message.from_user.id) == "task":
        await message.answer("جاري الكتابة.. انتظر ⏳")
        prompt = f"اكتب بحثاً أو واجباً عن: {message.text}. اكتبه بشكل أكاديمي مرتب، بدون صفحة غلاف، ابدأ بالمحتوى مباشرة."
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        doc = Document()
        doc.add_paragraph(res.choices[0].message.content)
        doc.save("output.docx")
        await message.answer_document(FSInputFile("output.docx"))
        os.remove("output.docx")
        user_sessions.pop(message.from_user.id)

@dp.message(F.photo)
async def process_photo(message: types.Message):
    if user_sessions.get(message.from_user.id) == "quiz":
        await message.answer("جاري الحل بدقة.. 🔍")
        file = await bot.get_file(message.photo[-1].file_id)
        url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": [{"type": "text", "text": "حل هذا السؤال بدقة علمية:"}, {"type": "image_url", "image_url": {"url": url}}]}])
        await message.answer(res.choices[0].message.content)
        user_sessions.pop(message.from_user.id)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
