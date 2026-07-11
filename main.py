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

# قائمة الأزرار الرئيسية
def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔍 حل بحث / واجب")], 
        [KeyboardButton(text="📸 حل اختبار")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("أهلاً بك يا سعود! أنا مساعدك الأكاديمي المحترف. اختر الخدمة:", reply_markup=get_main_kb())

@dp.message(F.text == "🔍 حل بحث / واجب")
async def start_research(message: types.Message):
    user_sessions[message.from_user.id] = "research"
    await message.answer("أرسل موضوع البحث أو الواجب وسأقوم بكتابته فوراً بشكل منسق وجاهز للرفع.")

@dp.message(F.text == "📸 حل اختبار")
async def start_quiz(message: types.Message):
    user_sessions[message.from_user.id] = "quiz"
    await message.answer("أرسل صورة السؤال أو الاختبار، وسأقوم بحله لك بدقة متناهية.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    if user_sessions.get(uid) == "research":
        await message.answer("جاري كتابة الملف.. ⏳")
        prompt = f"اكتب بحثاً أكاديمياً أو واجباً كاملاً عن: {message.text}. رتبه بوضوح (مقدمة، فصول، خاتمة). استخدم لغة الموضوع. لا تكتب غلافاً، ابدأ بالمحتوى مباشرة وبشكل مرتب واحترافي."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        
        doc = Document()
        doc.add_paragraph(response.choices[0].message.content)
        doc.save("Academic_Task.docx")
        
        await message.answer_document(FSInputFile("Academic_Task.docx"), caption="✅ الملف جاهز للرفع.")
        os.remove("Academic_Task.docx")
        user_sessions.pop(uid)
    else:
        await message.answer("يرجى اختيار خدمة من الأزرار أولاً.", reply_markup=get_main_kb())

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    if user_sessions.get(message.from_user.id) == "quiz":
        await message.answer("جاري تحليل السؤال بدقة.. 🔍")
        file = await bot.get_file(message.photo[-1].file_id)
        url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": [{"type": "text", "text": "حل هذا السؤال بدقة علمية واشرح الإجابة باختصار:"}, {"type": "image_url", "image_url": {"url": url}}]}])
        await message.answer(response.choices[0].message.content)
        user_sessions.pop(message.from_user.id)
    else:
        await message.answer("الرجاء الضغط على '📸 حل اختبار' قبل إرسال الصورة.")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
