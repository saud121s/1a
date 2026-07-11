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

# التخزين المؤقت للبيانات الشخصية
user_data = {}

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📸 حل اختبار")],
        [KeyboardButton(text="🔍 حل بحث")],
        [KeyboardButton(text="📝 حل واجب")]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("أهلاً بك! أنا مساعدك الذكي. اختر الخدمة:", reply_markup=get_main_keyboard())

# مرحلة جمع البيانات للبحث والواجب
@dp.message(F.text.in_({"🔍 حل بحث", "📝 حل واجب"}))
async def collect_info(message: types.Message):
    user_data[message.from_user.id] = {"type": message.text}
    await message.answer("لإعداد ملف احترافي، يرجى كتابة البيانات بالتنسيق التالي في رسالة واحدة:\n"
                         "الاسم، الجامعة، اسم الدكتور، الرقم الجامعي.")

# معالجة النصوص (البيانات أو موضوع البحث)
@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text == "/start": return
    
    uid = message.from_user.id
    
    # إذا كان المستخدم في مرحلة تقديم البيانات
    if uid in user_data and "data" not in user_data[uid]:
        user_data[uid]["data"] = message.text
        await message.answer("تم حفظ البيانات! الآن أرسل موضوع البحث أو نص السؤال للواجب.")
        return

    # إذا كان المستخدم جاهزاً لإرسال السؤال
    await message.answer("جاري الكتابة والتنسيق.. ⏳")
    info = user_data.get(uid, {}).get("data", "غير متوفر")
    task_type = user_data.get(uid, {}).get("type", "عمل أكاديمي")
    
    prompt = f"قم بكتابة {task_type} بناءً على هذه البيانات الشخصية: {info}. وموضوع السؤال هو: {message.text}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    await message.answer(response.choices[0].message.content + "\n\n/start للعودة.")

# معالجة الصور (كما هي)
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("جاري التحليل.. 🧠")
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "حل هذا السؤال بدقة:"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}]
    )
    await message.answer(response.choices[0].message.content + "\n\n/start للعودة.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
