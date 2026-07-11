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
    await message.answer("أهلاً بك! أنا جاهز. اختر الخدمة:", reply_markup=kb)

@dp.message(F.text == "🔍 بحث أو واجب")
async def start_task(message: types.Message):
    user_sessions[message.from_user.id] = "task"
    await message.answer("أرسل بياناتك (الاسم، الجامعة، الدكتور، الرقم) وموضوع البحث.")

@dp.message(F.text == "📸 حل اختبار")
async def start_quiz(message: types.Message):
    user_sessions[message.from_user.id] = "quiz"
    await message.answer("أرسل صورة السؤال. (عند الانتهاء أرسل: انتهيت)")

@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    if message.text.lower() == "انتهيت":
        user_sessions.pop(uid, None)
        await message.answer("تم إنهاء الجلسة.")
        return
    
    if user_sessions.get(uid) == "task":
        await message.answer("جاري الكتابة..")
        try:
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"اكتب بحثاً عن: {message.text}. اكتب البيانات والبحث في ملف Word منظم وبدون تكرار."}])
            doc = Document()
            doc.add_paragraph(res.choices[0].message.content)
            doc.save("file.docx")
            await message.answer_document(FSInputFile("file.docx"))
            os.remove("file.docx")
        except Exception as e: await message.answer(f"حدث خطأ: {e}")
        user_sessions.pop(uid, None)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    uid = message.from_user.id
    if user_sessions.get(uid) == "quiz":
        await message.answer("جاري الحل..")
        file = await bot.get_file(message.photo[-1].file_id)
        url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": [{"type": "text", "text": "حل الأسئلة (مقالي واختياري) برقم السؤال وإجابة مختصرة."}, {"type": "image_url", "image_url": {"url": url}}]}])
        await message.answer(res.choices[0].message.content)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
