import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_sessions = {}

# دالة لتنسيق النصوص داخل ملف الوورد
def create_professional_doc(content, user_data):
    doc = Document()
    # غلاف مرتب
    title = doc.add_heading(f"بحث أكاديمي: {user_data.get('topic', 'عنوان البحث')}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"\nإعداد الطالب: {user_data.get('name', '---')}")
    doc.add_paragraph(f"الجامعة: {user_data.get('uni', '---')}")
    doc.add_page_break()
    
    # المحتوى
    doc.add_paragraph(content)
    
    file_name = "Academic_Research.docx"
    doc.save(file_name)
    return file_name

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 بحث أكاديمي")], [KeyboardButton(text="📝 واجب مدرسي")]], resize_keyboard=True)
    await message.answer("مرحباً بك! أنا مساعدك الأكاديمي المحترف. ماذا تريد أن ننجز اليوم؟", reply_markup=kb)

@dp.message(F.text)
async def process_request(message: types.Message):
    uid = message.from_user.id
    
    # إذا كانت رسالة أولية (بيانات)
    if not hasattr(process_request, "data"): process_request.data = {}
    
    await message.answer("جاري معالجة طلبك بدقة عالية.. 🚀")
    
    prompt = f"اكتب بحثاً أكاديمياً احترافياً باللغة التي استخدمها الطالب في هذا الموضوع: {message.text}. " \
             "يجب أن يكون النص منظماً، خالياً من العبارات الجانبية، وجاهزاً للرفع مباشرة. ابدأ بالمقدمة وانتهِ بالخاتمة."
    
    response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
    
    file_path = create_professional_doc(response.choices[0].message.content, {"topic": message.text})
    
    await message.answer_document(FSInputFile(file_path), caption="✅ تم تجهيز الملف باحترافية تامة.")
    os.remove(file_path)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
