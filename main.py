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

# دالة إنشاء ملف الواجب مع البيانات في الأعلى
def create_doc(content, data):
    doc = Document()
    doc.add_paragraph(f"الاسم: {data.get('name')}\nالجامعة: {data.get('uni')}\nالدكتور: {data.get('dr')}\nالرقم الجامعي: {data.get('id')}")
    doc.add_paragraph("_" * 40)
    doc.add_paragraph(content)
    doc.save("Task.docx")
    return "Task.docx"

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 بحث أو واجب")], [KeyboardButton(text="📸 حل اختبار")]], resize_keyboard=True)
    await message.answer("أهلاً بك! اختر الخدمة:", reply_markup=kb)

@dp.message(F.text == "🔍 بحث أو واجب")
async def start_task(message: types.Message):
    user_sessions[message.from_user.id] = {"state": "task"}
    await message.answer("أرسل بياناتك (الاسم، الجامعة، الدكتور، الرقم الجامعي) ثم موضوع البحث.")

@dp.message(F.text == "📸 حل اختبار")
async def start_quiz(message: types.Message):
    user_sessions[message.from_user.id] = {"state": "quiz"}
    await message.answer("أرسل صورة السؤال. (عندما تنتهي من جميع الأسئلة أرسل كلمة: انتهيت)")

@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    if message.text.lower() == "انتهيت":
        user_sessions.pop(uid, None)
        await message.answer("تم إنهاء جلسة الاختبار، بالتوفيق!")
        return

    session = user_sessions.get(uid)
    if session and session["state"] == "task":
        await message.answer("جاري كتابة الملف..")
        # استخراج بسيط (يفترض أنك ترسل البيانات والموضوع)
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"اكتب بحثاً عن: {message.text}"}])
        data = {"name": "سعود", "uni": "الخليج", "dr": "فخري", "id": "128"} # يمكنك تطوير هذا لاستخراج البيانات
        path = create_doc(res.choices[0].message.content, data)
        await message.answer_document(FSInputFile(path))
        os.remove(path)
        user_sessions.pop(uid)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    uid = message.from_user.id
    if user_sessions.get(uid, {}).get("state") == "quiz":
        await message.answer("جاري الحل..")
        file = await bot.get_file(message.photo[-1].file_id)
        url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": [{"type": "text", "text": "حل الأسئلة في الصورة برقم السؤال وجوابه فقط (1- ... 2- ...)."}, {"type": "image_url", "image_url": {"url": url}}]}])
        await message.answer(res.choices[0].message.content)
    else:
        await message.answer("الرجاء الضغط على '📸 حل اختبار' أولاً.")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
