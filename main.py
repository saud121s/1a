import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_sessions = {}

@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    # هنا الكود الذي ينظم التنسيق
    await message.answer("جاري إنشاء الملف بتنسيق احترافي.. انتظر ⏳")
    
    # طلب محتوى منظم من الذكاء الاصطناعي
    prompt = f"اكتب بحثاً عن: {message.text}. رتبه بوضوح إلى: غلاف، فهرس، مقدمة، فصول، خاتمة."
    response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
    
    # إنشاء ملف Word وتنسيقه
    doc = Document()
    
    # إضافة العنوان بخط كبير
    title = doc.add_heading("بحث أكاديمي", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # إضافة المحتوى
    doc.add_paragraph(response.choices[0].message.content)
    
    # حفظ الملف
    file_path = "Academic_Report.docx"
    doc.save(file_path)
    
    await message.answer_document(FSInputFile(file_path), caption="✅ ملفك جاهز ومنسق.")
    os.remove(file_path)
