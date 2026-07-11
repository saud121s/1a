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
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 بحث أو واجب")], [KeyboardButton(text="📸 حل اختبار")]], resize_keyboard=True)
    await message.answer("أهلاً بك! اختر الخدمة:", reply_markup=kb)

@dp.message(F.text == "🔍 بحث أو واجب")
async def start_task(message: types.Message):
    user_sessions[message.from_user.id] = "task"
    await message.answer("أرسل بياناتك وموضوع البحث.")

@dp.message(F.text == "📸 حل اختبار")
async def start_quiz(message: types.Message):
    user_sessions[message.from_user.id] = "quiz"
    await message.answer("أرسل صورة السؤال.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    if user_sessions.get(uid) == "task":
        await message.answer("جاري التجهيز..")
        prompt = f"اكتب بحثاً عن: {message.text}. اكتب المحتوى فقط بدون مقدمات."
        resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        doc = Document()
        doc.add_paragraph(resp.choices[0].message.content)
        doc.save("file.docx")
        await message.answer_document(FSInputFile("file.docx"))
        os.remove("file.docx")
        user_sessions.pop(uid)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    if user_sessions.get(message.from_user.id) == "quiz":
        await message.answer("جاري الحل..")
        # هنا سيتم حل الاختبار
        user_sessions.pop(message.from_user.id)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
