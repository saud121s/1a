import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI
from docx import Document

# إعدادات البوت
TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_sessions = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📸 حل اختبار")], [KeyboardButton(text="🔍 حل بحث"), KeyboardButton(text="📝 حل واجب")]], resize_keyboard=True)
    await message.answer("أهلاً بك يا سعود! اختر الخدمة:", reply_markup=kb)

@dp.message(F.text.in_({"📸 حل اختبار", "🔍 حل بحث", "📝 حل واجب"}))
async def handle_choice(message: types.Message):
    user_sessions[message.from_user.id] = {"state": "waiting_info", "type": message.text}
    await message.answer("أرسل بياناتك (الاسم، الجامعة، الدكتور، الرقم الجامعي) وموضوع البحث أو الواجب في رسالة واحدة.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text == "/start": return await start(message)
    uid = message.from_user.id
    if uid in user_sessions and user_sessions[uid]["state"] == "waiting_info":
        await message.answer("جاري كتابة الملف بتنسيق أكاديمي احترافي.. انتظر ⏳")
        prompt = f"أنت خبير أكاديمي. اكتب {user_sessions[uid]['type']} احترافي بناءً على: {message.text}. رتبه كالتالي: صفحة غلاف، فهرس محتويات، مقدمة، فصول مرقمة، وخاتمة. اجعل المحتوى منسقاً للطباعة."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        
        doc = Document()
        doc.add_heading(user_sessions[uid]['type'], 0)
        doc.add_paragraph(response.choices[0].message.content)
        doc.save("Academic_File.docx")
        
        await message.answer_document(FSInputFile("Academic_File.docx"), caption="✅ تم تجهيز ملفك الأكاديمي.")
        user_sessions.pop(uid)
    else: await message.answer("اختر خدمة أولاً عبر /start")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("جاري التحليل.. 🧠")
    file = await bot.get_file(message.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": [{"type": "text", "text": "حل هذا بدقة:"}, {"type": "image_url", "image_url": {"url": url}}]}])
    await message.answer(response.choices[0].message.content)

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
