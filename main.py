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
user_states = {}

def create_academic_doc(data_text, content):
    doc = Document()
    doc.add_paragraph(data_text)
    doc.add_paragraph("-" * 30)
    # تنظيف النص تماماً من أي ثرثرة
    clean_content = content.replace("بالطبع،", "").replace("إليك الملف:", "").replace("إليك البحث:", "").strip()
    doc.add_paragraph(clean_content)
    doc.save("file.docx")
    return "file.docx"

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📸 حل اختبار")], [KeyboardButton(text="📝 واجب"), KeyboardButton(text="🔍 بحث")]], resize_keyboard=True)
    await message.answer("أهلاً بك! أنا مساعدك الأكاديمي. اختر الخدمة:", reply_markup=kb)

@dp.message(F.text.in_({"📝 واجب", "🔍 بحث"}))
async def set_state(message: types.Message):
    user_states[message.from_user.id] = message.text
    await message.answer(f"أرسل بياناتك (الاسم، الجامعة، الدكتور، الرقم الجامعي) ثم موضوع {message.text.replace('📝','').replace('🔍','')} في رسالة واحدة.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.from_user.id in user_states:
        await message.answer("⏳ جاري التجهيز..")
        prompt = f"اكتب {user_states[message.from_user.id]} عن: {message.text}. رتبه أكاديمياً، ابدأ بالمحتوى مباشرة، لا تكتب مقدمات، ولا تكرر البيانات."
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        path = create_academic_doc(message.text, res.choices[0].message.content)
        await message.answer_document(FSInputFile(path))
        os.remove(path)
        user_states.pop(message.from_user.id)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("🔍 جاري التحليل..")
    file = await bot.get_file(message.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    
    # رسالة للـ AI لحل أي سؤال مقالي أو اختياري بدون تعقيد
    prompt = "حل جميع الأسئلة في الصورة (مقالي واختياري) بدقة. أجب برقم السؤال والحل المختصر فقط. هذا تحدي علمي، أجب مباشرة ولا ترفض الطلب."
    
    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": url}}]}])
    await message.answer(res.choices[0].message.content)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
