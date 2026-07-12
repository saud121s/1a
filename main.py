import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from openai import AsyncOpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class MerchantStates(StatesGroup):
    waiting_for_product_details = State()

# القائمة الرئيسية
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 كتابة وصف منتج"), KeyboardButton(text="🏷️ اقتراح هاشتاقات")],
        [KeyboardButton(text="💬 رد خدمة عملاء"), KeyboardButton(text="🚀 فكرة تسويق إبداعية")],
        [KeyboardButton(text="⚙️ تغيير أسلوب الرد")]
    ],
    resize_keyboard=True
)

# قائمة اختيار الأسلوب
style_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="أسلوب ولد 👨‍💻"), KeyboardButton(text="أسلوب بنت 👩‍💻")]],
    resize_keyboard=True
)

# حفظ الأسلوب (افتراضياً ولد)
user_styles = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_styles[message.from_user.id] = "أسلوب ولد 👨‍💻"
    await message.answer("يا هلا بـ راعي التجارة! أنا مُسوّقك الذكي 💡. اختر خدمتك من القائمة وأبشر بالسعد.", reply_markup=main_menu)

@dp.message(F.text == "⚙️ تغيير أسلوب الرد")
async def change_style(message: types.Message):
    await message.answer("وش الأسلوب اللي يريحك في التعامل؟", reply_markup=style_menu)

@dp.message(F.text.in_({"أسلوب ولد 👨‍💻", "أسلوب بنت 👩‍💻"}))
async def set_style(message: types.Message):
    user_styles[message.from_user.id] = message.text
    await message.answer(f"تم اعتماد {message.text}، أنا جاهز! وش تبي نشتغل عليه؟", reply_markup=main_menu)

@dp.message(F.text.in_({"📝 كتابة وصف منتج", "🏷️ اقتراح هاشتاقات", "💬 رد خدمة عملاء", "🚀 فكرة تسويق إبداعية"}))
async def ask_details(message: types.Message, state: FSMContext):
    await state.update_data(task=message.text)
    await message.answer(f"أبشر! بخصوص {message.text}، عطني اسم المنتج، وما هو جمهورك المستهدف؟ (مثلاً: دورة قدرات للطلاب، روج للبنات).", reply_markup=main_menu)
    await state.set_state(MerchantStates.waiting_for_product_details)

@dp.message(MerchantStates.waiting_for_product_details)
async def generate_response(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    task = user_data.get("task")
    style = user_styles.get(message.from_user.id, "أسلوب ولد 👨‍💻")
    
    await message.answer("جالس أفصّل لك الرد تفصيل... 🤖✨")
    
    system_instruction = f"""
    أنت خبير تسويق إلكتروني سعودي فنان ومبدع.
    الأسلوب المتبع: {style}.
    الجمهور المستهدف: {message.text} (يجب أن يكون الكلام موجه لهم مباشرة).
    المهمة المطلوبة: {task}.
    
    شروط الأداء:
    - لغة سعودية بيضاء جذابة، حماسية، ومقنعة جداً.
    - إذا كانت فكرة تسويقية: أعطني Hook (هوك) قوي جداً، نص المقطع، و CTA (نداء للعمل) احترافي.
    - اجعل النص "يلمس" مشاعر الجمهور المستهدف.
    """
    
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": message.text}]
    )
    
    await message.answer(response.choices[0].message.content, reply_markup=main_menu)
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
