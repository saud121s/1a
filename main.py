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

# الأزرار الرئيسية
def get_main_keyboard():
    kb = [
        [KeyboardButton(text="📸 حل اختبار")],
        [KeyboardButton(text="🔍 حل بحث")],
        [KeyboardButton(text="📝 حل واجب")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    welcome = (
        "أهلاً بك في منصتك الأكاديمية الذكية! 🎓\n"
        "أنا هنا لأكون مساعدك الشخصي في دراستك.\n\n"
        "اختر الخدمة التي تحتاجها من الأسفل:"
    )
    await message.answer(welcome, reply_markup=get_main_keyboard())

# عند اختيار خدمة، نحذف الأزرار ونوجه الطالب
@dp.message(F.text.in_({"📸 حل اختبار", "🔍 حل بحث", "📝 حل واجب"}))
async def handle_choice(message: types.Message):
    await message.answer(
        f"اختيار موفق! لخدمة ({message.text})، يرجى إرسال الصورة أو نص السؤال الآن.\n"
        "سأقوم بالتحليل والرد عليك فوراً. ⏳",
        reply_markup=ReplyKeyboardRemove() # هذا السطر يحذف الأزرار
    )

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("جاري معالجة الصورة وفهم السؤال.. ثوانٍ وسأعطيك الإجابة! 🧠")
    
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "حل هذا السؤال بدقة واحترافية:"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}]
    )
    await message.answer(f"✅ الإجابة:\n\n{response.choices[0].message.content}\n\n/start للعودة للقائمة الرئيسية.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
