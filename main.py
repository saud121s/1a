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
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔍 حل بحث"), KeyboardButton(text="📝 حل واجب")]], resize_keyboard=True)
    await message.answer("أهلاً بك! اختر الخدمة:", reply_markup=kb)

@dp.message(F.text.in_({"🔍 حل بحث", "📝 حل واجب"}))
async def handle_choice(message: types.Message):
    user_sessions[message.from_user.id] = {"type": message.text}
    await message.answer("أرسل البيانات (الاسم، الجامعة، الدكتور، الرقم الجامعي) وموضوع البحث في رسالة واحدة.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    if uid in user_sessions:
        await message.answer("يتم الآن إعداد ملفك.. انتظر ⏳")
        
        # تعليمات صارمة للذكاء الاصطناعي لإنتاج محتوى "خام" بدون تعليقات
        prompt = f"اكتب بحثاً أكاديمياً كاملاً عن: {message.text}. البيانات المطلوبة: {user_sessions[uid]}. " \
                 "يجب أن يكون الملف: 1. صفحة غلاف رسمية. 2. فهرس. 3. محتوى مرتب بعناوين فرعية. 4. خاتمة. " \
                 "مهم جداً: لا تكتب أي مقدمات أو عبارات جانبية، اكتب محتوى البحث فقط ليكون جاهزاً للتحميل."
        
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        
        doc = Document()
        # إضافة المحتوى كما هو من الذكاء الاصطناعي بدون إضافات برمجية تعيق التنسيق
        doc.add_paragraph(response.choices[0].message.content)
        
        file_path = "Search_Final.docx"
        doc.save(file_path)
        
        await message.answer_document(FSInputFile(file_path), caption="✅ ملفك جاهز للرفع في موقع الكلية.")
        user_sessions.pop(uid)
        os.remove(file_path)
    else: await message.answer("ابدأ بـ /start")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
