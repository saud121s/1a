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
user_data_storage = {}

# دالة إنشاء ملف أكاديمي احترافي
def create_doc(user_info, content):
    doc = Document()
    doc.add_paragraph(user_info) # البيانات في الأعلى
    doc.add_paragraph("--------------------------------------------------")
    doc.add_paragraph(content) # المحتوى
    doc.save("Final_Task.docx")
    return "Final_Task.docx"

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📸 حل اختبار")],
        [KeyboardButton(text="📝 واجب"), KeyboardButton(text="🔍 بحث")]
    ], resize_keyboard=True)
    await message.answer("أهلاً بك يا سعود. اختر الخدمة:", reply_markup=kb)

@dp.message(F.text.in_({"📝 واجب", "🔍 بحث"}))
async def ask_data(message: types.Message):
    user_data_storage[message.from_user.id] = message.text
    await message.answer(f"أرسل بياناتك (الاسم، الجامعة، الدكتور، الرقم الجامعي) ثم موضوع {message.text.replace('📝','').replace('🔍','')} وسأجهز الملف فوراً.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    state = user_data_storage.get(uid)
    if state:
        await message.answer("⏳ جاري الكتابة..")
        prompt = f"اكتب {state} بناءً على هذه البيانات والموضوع: {message.text}. اكتب المحتوى مباشرة، بدون مقدمات، وبدون تكرار البيانات."
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        path = create_doc(message.text, res.choices[0].message.content)
        await message.answer_document(FSInputFile(path))
        os.remove(path)
        user_data_storage.pop(uid)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("🔍 جاري الحل الدقيق (مقالي واختياري)..")
    file = await bot.get_file(message.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    res = client.chat.completions.create(model="gpt-4o", messages=[
        {"role": "user", "content": [
            {"type": "text", "text": "حل الاختبار التالي (مقالي واختياري). أجب برقم السؤال والحل المختصر والدقيق فقط."},
            {"type": "image_url", "image_url": {"url": url}}
        ]}
    ])
    await message.answer(res.choices[0].message.content)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
