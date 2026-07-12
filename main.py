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
    waiting_for_details = State()

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 كتابة وصف منتج"), KeyboardButton(text="🏷️ اقتراح هاشتاقات")],
        [KeyboardButton(text="💬 رد خدمة عملاء"), KeyboardButton(text="🚀 فكرة تسويق إبداعية")],
        [KeyboardButton(text="⚙️ تغيير أسلوب الرد")]
    ],
    resize_keyboard=True
)

style_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="أسلوب ولد 👨‍💻"), KeyboardButton(text="أسلوب بنت 👩‍💻")]],
    resize_keyboard=True
)

user_styles = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_styles[message.from_user.id] = "أسلوب ولد 👨‍💻"
    await message.answer("أهلاً بك يا تاجر! أنا مُسوّقك الذكي، جاهز لرفع مبيعاتك 💡. اختر خدمتك:", reply_markup=main_menu)

@dp.message(F.text == "⚙️ تغيير أسلوب الرد")
async def change_style(message: types.Message):
    await message.answer("اختر الأسلوب اللي يمثل متجرك:", reply_markup=style_menu)

@dp.message(F.text.in_({"أسلوب ولد 👨‍💻", "أسلوب بنت 👩‍💻"}))
async def set_style(message: types.Message):
    user_styles[message.from_user.id] = message.text
    await message.answer(f"تم اعتماد {message.text}، وش تبي نشتغل عليه الحين؟", reply_markup=main_menu)

@dp.message(F.text.in_({"📝 كتابة وصف منتج", "🏷️ اقتراح هاشتاقات", "💬 رد خدمة عملاء", "🚀 فكرة تسويق إبداعية"}))
async def ask_details(message: types.Message, state: FSMContext):
    await state.update_data(task=message.text)
    await message.answer(f"أبشر! بخصوص {message.text}، عطني اسم المنتج، والجمهور المستهدف (مثلاً: طلاب، بنات، فئة عمرية معينة).", reply_markup=main_menu)
    await state.set_state(MerchantStates.waiting_for_details)

@dp.message(MerchantStates.waiting_for_details)
async def generate_final(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    task = user_data.get("task")
    style = user_styles.get(message.from_user.id, "أسلوب ولد 👨‍💻")
    
    await message.answer("جاري تنفيذ طلبك... 🤖⚡")
    
    system_instruction = f"""
    أنت خبير تسويق إلكتروني سعودي محترف جداً. أسلوبك: {style}.
    المهمة: {task}.
    الجمهور: {message.text}.
    
    القواعد الصارمة:
    1. ابدأ فوراً في صلب الموضوع (لا مقدمات، لا "أهلاً بك").
    2. في التسويق: Hook قوي، نص مباشر، نداء للعمل (رابط البايو).
    3. في وصف المنتج: وصف جذاب يركز على الفائدة + نداء للعمل.
    4. في خدمة العملاء: ردود لبقة، احترافية، تحل المشكلة فوراً.
    5. في الهاشتاقات: عطني أفضل 10 هاشتاقات متداولة بالسعودية.
    6. اللهجة: سعودية بيضاء حماسية تجذب العميل للشراء فوراً.
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
