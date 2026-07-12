import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI
import os

# إعدادات البوت والذكاء الاصطناعي
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# تفعيل تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

# نص الشخصية (System Prompt)
SYSTEM_PROMPT = """
أنت "مساعد التاجر الذكي"، خبير تسويق إلكتروني محترف في السوق السعودي.
مهمتك مساعدة التاجر لزيادة مبيعاته بأسلوب سعودي "أبيض" وودي.
1. عند كتابة الوصف التسويقي: استخدم "خطاف" (Hook) قوي، واكتب بلهجة سعودية بيضاء، واختم بدعوة لاتخاذ إجراء (CTA).
2. اقترح 15 هاشتاق ترند مناسبة للسوق السعودي.
3. كن لبقاً واحترافياً في صياغة ردود خدمة العملاء.
"""

# تصميم الأزرار
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 كتابة وصف منتج", callback_data="option_desc")],
        [InlineKeyboardButton(text="🏷️ اقتراح هاشتاقات", callback_data="option_tags")],
        [InlineKeyboardButton(text="💬 رد خدمة عملاء", callback_data="option_reply")]
    ])
    return keyboard

# رسالة الترحيب
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    welcome_text = (
        f"يا هلا والله يا راعي التجارة! 👋\n"
        f"أنا مساعدك الذكي، موجود هنا عشان أفك عنك زحمة التسويق وأخلي متجرك يطير في المبيعات.\n\n"
        f"وش تحتاج نشتغل عليه اليوم؟ اختر من القائمة تحت:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu())

# التعامل مع الضغط على الأزرار
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    if callback.data == "option_desc":
        await callback.message.answer("أبشر! أرسل لي اسم المنتج أو تفاصيله، وبكتب لك وصف يبيعه لك في ثواني.")
    elif callback.data == "option_tags":
        await callback.message.answer("سمّ! أرسل لي وش منتجك وبجيب لك هاشتاقات ترفع وصولك في التيك توك.")
    elif callback.data == "option_reply":
        await callback.message.answer("حاضر، أرسل لي رسالة العميل المزعجة، وبصيغ لك رد احترافي يرضيه.")
    await callback.answer()

# معالجة النصوص (الذكاء الاصطناعي)
@dp.message(F.text)
async def handle_message(message: types.Message):
    await message.answer("دقايق.. التاجر الذكي جالس يشتغل على طلبك... 🤖")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("يا بعدي، صار خلل بسيط. جرب أرسل طلبك مرة ثانية.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
