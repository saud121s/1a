import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI
from docx import Document

TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_sessions = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 حل بحث")], [KeyboardButton(text="📸 حل اختبار")]], resize_keyboard=True)
    await message.answer("مرحباً بك! اختر الخدمة:", reply_markup=kb)

@dp.message(F.text == "🔍 حل بحث")
async def start_research(message: types.Message):
    user_sessions[message.from_user.id] = "research"
    await message.answer("أرسل موضوع البحث وسأقوم بكتابته فوراً وبشكل منسق وجاهز للرفع.")

@dp.message(F.text == "📸 حل اختبار")
async def start_quiz(message: types.Message):
    user_sessions[message.from_user.id] = "quiz"
    await message.answer("أرسل صورة السؤال أو الاختبار، وسأقوم بحله لك بدقة متناهية فوراً.")

@dp.message(F.text)
async def handle_research(message: types.Message):
    if user_sessions.get(message.from_user.id) == "research":
        await message.answer("جاري كتابة البحث.. ⏳")
        prompt = f"اكتب بحثاً أكاديمياً احترافياً عن: {message.text}. رتبه بوضوح (مقدمة، فصول، خاتمة). استخدم لغة الموضوع (عربي أو إنجليزي). لا تكتب صفحات غلاف ولا مقدمات جانبية، ابدأ بالمحتوى مباشرة وبشكل مرتب."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        
        doc = Document()
        doc.add_paragraph(response.choices[0].message.content)
        doc.save("Research.docx")
        await message.answer_document(FSInputFile("Research.docx"), caption="✅ ملف البحث جاهز للرفع.")
        os.remove("Research.docx")
        user_sessions.pop(message.from_user.id)

@dp.message(F.photo)
async def handle_quiz(message: types.Message):
    await message.answer("جاري تحليل السؤال بدقة.. 🔍")
    file = await bot.get_file(message.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": [{"type": "text", "text": "حل هذا السؤال بدقة علمية واشرح الإجابة باختصار:"}, {"type": "image_url", "image_url": {"url": url}}]}])
    await message.answer(response.choices[0].message.content)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
