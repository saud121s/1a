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

# الترحيب الرسمي
@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        "أهلاً بك يا سعود في مساعدك الأكاديمي الذكي. 🎓\n"
        "أنا هنا لتسهيل دراستك، يمكنك إرسال:\n"
        "1. بياناتك وموضوع البحث وسأقوم بتجهيزه لك في ملف Word.\n"
        "2. صورة الاختبار وسأقوم بحله لك فوراً وبشكل مختصر."
    )
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 بحث أو واجب")], [KeyboardButton(text="📸 حل اختبار")]], resize_keyboard=True)
    await message.answer(welcome_text, reply_markup=kb)

# دالة إنشاء الملف (بيانات فوق + محتوى بدون تكرار)
def create_clean_doc(text, user_info):
    doc = Document()
    doc.add_paragraph(user_info) # البيانات في الأعلى
    doc.add_paragraph("-" * 30)
    doc.add_paragraph(text) # المحتوى
    doc.save("file.docx")
    return "file.docx"

@dp.message(F.text)
async def handle_text(message: types.Message):
    if "الاسم" in message.text and "موضوع" in message.text:
        await message.answer("جاري العمل على طلبك.. ثوانٍ وسيكون الملف جاهزاً.")
        res = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": f"اكتب بحثاً أكاديمياً عن: {message.text}. اكتب المحتوى مباشرة، لا تكتب مقدمات، ولا تكرر البيانات."}]
        )
        path = create_clean_doc(res.choices[0].message.content, message.text.split("موضوع")[0])
        await message.answer_document(FSInputFile(path))
        os.remove(path)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("🔍 جاري التحليل.. سأقدم لك الإجابة مباشرة.")
    file = await bot.get_file(message.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    res = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": [{"type": "text", "text": "حل الاختبار التالي (مقالي واختياري). أجب برقم السؤال والجواب فقط، بشكل مختصر جداً."}, {"type": "image_url", "image_url": {"url": url}}]}]
    )
    await message.answer(res.choices[0].message.content)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
