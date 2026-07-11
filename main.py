import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from openai import OpenAI
from docx import Document

TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()

user_sessions = {}

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📸 حل اختبار")],
        [KeyboardButton(text="🔍 حل بحث")],
        [KeyboardButton(text="📝 حل واجب")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("أهلاً بك! اختر الخدمة:", reply_markup=get_main_keyboard())

@dp.message(F.text.in_({"📸 حل اختبار", "🔍 حل بحث", "📝 حل واجب"}))
async def handle_choice(message: types.Message):
    user_sessions[message.from_user.id] = {"state": "waiting_info", "type": message.text}
    await message.answer("يرجى إرسال (الاسم، الجامعة، الدكتور، الرقم الجامعي، موضوع البحث/الواجب) في رسالة واحدة.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text == "/start": 
        user_sessions.pop(message.from_user.id, None)
        return await start(message)
    
    uid = message.from_user.id
    if uid in user_sessions and user_sessions[uid]["state"] == "waiting_info":
        await message.answer("جاري إنشاء الملف.. انتظر لحظة ⏳")
        
        prompt = f"اكتب {user_sessions[uid]['type']} مفصل واحترافي بناءً على البيانات: {message.text}. رتبه كملف أكاديمي."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        content = response.choices[0].message.content
        
        doc = Document()
        doc.add_heading(user_sessions[uid]['type'], 0)
        doc.add_paragraph(content)
        file_name = "Academic_File.docx"
        doc.save(file_name)
        
        await message.answer_document(FSInputFile(file_name), caption="✅ تم تجهيز ملفك الأكاديمي.")
        os.remove(file_name)
        user_sessions.pop(uid)
    else:
        await message.answer("اختر خدمة من القائمة.")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("جاري التحليل.. 🧠")
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [{"type": "text", "text": "حل بدقة:"}, {"type": "image_url", "image_url": {"url": image_url}}]}]
    )
    await message.answer(response.choices[0].message.content)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
