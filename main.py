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
    choosing_style = State()
    waiting_for_product = State()
    waiting_for_target = State()

# القوائم
main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚀 فكرة تسويق إبداعية")], [KeyboardButton(text="📝 كتابة وصف منتج")]],
    resize_keyboard=True
)

style_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="أسلوب ولد 👨‍💻")], [KeyboardButton(text="أسلوب بنت 👩‍💻")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("يا هلا بـ راعي التجارة! أنا مُسوّقك الذكي 💡.\nقبل نبدأ، كيف تحب أكون أسلوبي معك؟", reply_markup=style_menu)
    await state.set_state(MerchantStates.choosing_style)

@dp.message(MerchantStates.choosing_style)
async def choose_style(message: types.Message, state: FSMContext):
    await state.update_data(style=message.text)
    await message.answer("تم اعتماد الأسلوب! الحين، وش الخدمة اللي تحتاجها؟", reply_markup=main_menu)
    await state.set_state(MerchantStates.waiting_for_product)

@dp.message(MerchantStates.waiting_for_product)
async def ask_product_and_target(message: types.Message, state: FSMContext):
    await state.update_data(task=message.text)
    await message.answer("أبشر! عطني اسم المنتج أو فكرته، ومن هو جمهورك المستهدف؟ (مثلاً: دورة قدرات للطلاب، أو روج للبنات).", reply_markup=ReplyKeyboardRemove())
    await state.set_state(MerchantStates.waiting_for_target)

@dp.message(MerchantStates.waiting_for_target)
async def generate_marketing(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    style = user_data.get("style")
    task = user_data.get("task")
    
    await message.answer("جالس أضبط لك خطة تسويقية تكسر الدنيا... 🤖🔥")
    
    system_instruction = f"""
    أنت خبير تسويق إلكتروني سعودي محترف. أسلوبك في الرد هو: {style}.
    الجمهور المستهدف هو: {message.text}.
    المهمة: {task}.
    
    القواعد:
    1. تيك توك: اقترح Hook قوي، نص المقطع، و CTA لرابط البايو.
    2. إنستقرام: اقترح بوست مع Caption جذاب وهاشتاقات سعودية.
    3. اللهجة: سعودية بيضاء، حماسية، ومناسبة للجمهور المستهدف (سواء كان أسلوب ولد أو بنت).
    4. التركيز: إبراز الفائدة والقيمة للعميل.
    """
    
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": message.text}]
    )
    
    await message.answer(response.choices[0].message.content, reply_markup=main_menu)
    await state.set_state(MerchantStates.waiting_for_product)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
