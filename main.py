import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from openai import AsyncOpenAI

# إعداد المتغيرات
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# القائمة الجديدة (الأزرار)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 كتابة وصف منتج")],
        [KeyboardButton(text="🏷️ اقتراح هاشتاقات")],
        [KeyboardButton(text="💬 رد خدمة عملاء")],
        [KeyboardButton(text="🚀 فكرة تسويق إبداعية")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "يا هلا والله يا راعي التجارة! 🖐️\nأنا مساعدك الذكي، موجود هنا عشان أفك عنك زحمة التسويق وأخلي متجرك يطير في المبيعات.\n\nوش نحتاج نشتغل عليه اليوم؟",
        reply_markup=main_menu
    )

@dp.message(F.text == "🚀 فكرة تسويق إبداعية")
async def marketing_idea(message: types.Message):
    await message.answer("أبشر! وش هو منتجك؟ عطني نبذة عنه وبطلع لك فكرة تسويقية سعودية تضرب ترند!")

@dp.message()
async def handle_message(message: types.Message):
    # هنا يتم الربط مع OpenAI
    try:
        await message.answer("دقايق.. التاجر الذكي جالس يشتغل على طلبك... 🤖")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"أنت خبير تسويق سعودي، أجب على هذا الطلب بلهجة سعودية جذابة: {message.text}"}]
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        await message.answer("يا بعدي، صار خلل بسيط. جرب أرسل طلبك مرة ثانية.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
