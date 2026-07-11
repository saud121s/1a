import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_sessions = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📸 حل اختبار")], [KeyboardButton(text="🔍 حل بحث"), KeyboardButton(text="📝 حل واجب")]], resize_keyboard=True)
    await message.answer("أهلاً بك! اختر الخدمة:", reply_markup=kb)

@dp.message(F.text.in_({"📸 حل اختبار", "🔍 حل بحث", "📝 حل واجب"}))
async def handle_choice(message: types.Message):
    user_sessions[message.from_user.id] = {"state": "waiting_info", "type": message.text}
    await message.answer("أرسل بياناتك (الاسم، الجامعة، الدكتور، الرقم الجامعي) وموضوع البحث في رسالة واحدة.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    if uid in user_sessions:
        await message.answer("جاري كتابة الملف بتنسيق احترافي.. انتظر ⏳")
        
        # نطلب من الذكاء الاصطناعي هيكلة الملف
        prompt = f"اكتب بحثاً أكاديمياً احترافياً عن: {message.text}. اجعل الهيكل: صفحة غلاف، فهرس، مقدمة، عناوين فصول، خاتمة."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        
        # إنشاء ملف Word وتنسيقه
        doc = Document()
        
        # إضافة عنوان رئيسي
        title = doc.add_heading("بحث أكاديمي", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # إضافة المحتوى
        doc.add_paragraph(response.choices[0].message.content)
        
        file_path = "Academic_Report.docx"
        doc.save(file_path)
        
        await message.answer_document(FSInputFile(file_path), caption="✅ تم تجهيز ملفك الأكاديمي المنسق.")
        user_sessions.pop(uid)
        os.remove(file_path)
    else: await message.answer("اختر خدمة من القائمة أولاً.")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
