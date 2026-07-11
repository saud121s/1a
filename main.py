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

# دالة إنشاء ملف نظيف تماماً
def create_doc(content, data):
    doc = Document()
    # وضع البيانات في الأعلى فقط
    doc.add_paragraph(f"الاسم: {data.get('name')}")
    doc.add_paragraph(f"الجامعة: {data.get('uni')}")
    doc.add_paragraph(f"الدكتور: {data.get('dr')}")
    doc.add_paragraph(f"الرقم الجامعي: {data.get('id')}")
    doc.add_paragraph("-" * 30)
    # إضافة المحتوى كما هو من الـ AI
    doc.add_paragraph(content)
    doc.save("Academic_File.docx")
    return "Academic_File.docx"

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    # تغيير الأمر البرمجي ليكون تعليمياً وتحليلياً
    prompt = "قم بتحليل المحتوى التعليمي في هذه الصورة وقدم شرحاً أو حلاً توضيحياً للأمثلة الموجودة."
    
    file = await bot.get_file(message.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    
    res = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": url}}]}])
    
    await message.answer(res.choices[0].message.content)

# باقي الكود يظل كما هو...
