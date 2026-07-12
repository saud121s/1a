import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from openai import AsyncOpenAI

# إعدادات البوت
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# تعريف الحالات
class MerchantStates(StatesGroup):
    waiting_for_product = State()
    waiting_for_hashtags = State()
    waiting_for_customer_service = State()
    waiting_for_marketing_idea = State()

# القائمة الرئيسية
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
    await message.answer("أهلاً بك في مساعد التاجر الذكي! 🚀\nاختر الخدمة اللي تبيها من القائمة:", reply_markup=main_menu)

# --- معالجة الأزرار ---
@dp.message(F.text == "📝 كتابة وصف منتج")
async def desc_cmd(message: types.Message, state: FSMContext):
    await state.set_state(MerchantStates.waiting_for_product)
    await message.answer("أرسل لي اسم المنتج ومميزاته، وبكتب لك وصف يبيعه لك في ثواني!")

@dp.message(F.text == "🏷️ اقتراح هاشتاقات")
async def hash_cmd(message: types.Message, state: FSMContext):
    await state.set_state(MerchantStates.waiting_for_hashtags)
    await message.answer("وش هو المنتج أو الخدمة؟ بعطيك أقوى هاشتاقات ترند بالسعودية.")

@dp.message(F.text == "💬 رد خدمة عملاء")
async def service_cmd(message: types.Message, state: FSMContext):
    await state.set_state(MerchantStates.waiting_for_customer_service)
    await message.answer("أرسل لي رسالة العميل، وبصيغ لك رد ذكي ولبق.")

@dp.message(F.text == "🚀 فكرة تسويق إبداعية")
async def idea_cmd(message: types.Message, state: FSMContext):
    await state.set_state(MerchantStates.waiting_for_marketing_idea)
    await message.answer("أبشر! عطني فكرة عن منتجك، وبصمم لك خطة تسويقية تكسر الدنيا.")

# --- المعالجة الذكية ---
@dp.message(F.text)
async def process_ai(message: types.Message, state: FSMContext):
    user_state = await state.get_state()
    if not user_state:
        return await message.answer("الرجاء اختيار خدمة من القائمة فوق.", reply_markup=main_menu)

    await message.answer("جاري التحليل... 🤖")
    
    prompt = f"أنت خبير تجارة إلكترونية سعودي. أجب باحترافية وبلهجة سعودية بيضاء: {message.text}"
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        await message.answer(response.choices[0].message.content)
        await state.clear() # مسح الحالة بعد الرد
        await message.answer("وش تبي نشتغل عليه الحين؟", reply_markup=main_menu)
    except Exception:
        await message.answer("يا بعدي، صار ضغط بسيط، حاول مرة ثانية.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
