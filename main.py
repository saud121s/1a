import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from openai import OpenAI

TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()

# التخزين المؤقت للبيانات
user_sessions = {}

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📸 حل اختبار")],
        [KeyboardButton(text="🔍 حل بحث")],
        [KeyboardButton(text="📝 حل واجب")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("أهلاً بك في منصتك الأكاديمية! 🎓\nأنا مساعدك الشخصي، اختر الخدمة من الأسفل:", reply_markup=get_main_keyboard())

@dp.message(F.text.in_({"📸 حل اختبار", "🔍 حل بحث", "📝 حل واجب"}))
async def handle_choice(message: types.Message):
    user_sessions[message.from_user.id] = {"state": "waiting_info", "type": message.text}
    await message.answer(
        f"أهلاً بك في خدمة ({message.text.replace('📸 ', '').replace('🔍 ', '').replace('📝 ', '')}). 📝\n\n"
        "لأقوم بتجهيز ملفك بشكل أكاديمي متكامل، يرجى إرسال البيانات التالية في رسالة واحدة:\n"
        "1. الاسم الثلاثي\n"
        "2. اسم الجامعة\n"
        "3. اسم الدكتور\n"
        "4. الرقم الجامعي\n"
        "5. موضوع البحث أو الواجب المطلوب",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text == "/start": 
        user_sessions.pop(message.from_user.id, None)
        return await start(message)
    
    uid = message.from_user.id
    
    # إذا كان المستخدم في مرحلة تقديم البيانات
    if uid in user_sessions and user_sessions[uid]["state"] == "waiting_info":
        await message.answer("جاري صياغة ملفك الأكاديمي وتنسيقه.. ⏳")
        
        prompt = f"قم بكتابة {user_sessions[uid]['type']} بشكل أكاديمي واحترافي. " \
                 f"يجب أن يتضمن الملف المعلومات التالية في الأعلى: {message.text}. " \
                 "اجعل الأسلوب رسمياً ومنسقاً كملف جاهز للتسليم."
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        await message.answer(f"✅ تم تجهيز الملف:\n\n{response.choices[0].message.content}\n\n/start للعودة.")
        user_sessions.pop(uid)
    else:
        await message.answer("يرجى اختيار خدمة من القائمة أولاً عبر الضغط على /start")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("جاري تحليل صورة الاختبار.. 🧠")
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "حل هذا السؤال الأكاديمي بدقة واحترافية:"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}]
    )
    await message.answer(f"✅ الإجابة:\n\n{response.choices[0].message.content}\n\n/start للعودة.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
