import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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
    waiting_for_input = State()

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
    await message.answer("يا هلا والله يا راعي التجارة! 🖐️\nأنا مساعدك الذكي، موجود هنا عشان أفك عنك زحمة التسويق وأخلي متجرك يطير في المبيعات.\n\nوش نحتاج نشتغل عليه اليوم؟", reply_markup=main_menu)

@dp.message(F.text.in_({"📝 كتابة وصف منتج", "🏷️ اقتراح هاشتاقات", "💬 رد خدمة عملاء", "🚀 فكرة تسويق إبداعية"}))
async def set_state(message: types.Message, state: FSMContext):
    await state.update_data(task_type=message.text)
    await state.set_state(MerchantStates.waiting_for_input)
    await message.answer(f"تم اختيار: {message.text}. عطني التفاصيل الحين وبضبطك!")

@dp.message(MerchantStates.waiting_for_input)
async def process_ai(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    task = user_data.get("task_type")
    
    await message.answer("جاري التحليل والعمل على طلبك... 🤖🔥")
    
    system_instruction = f"""
    أنت خبير تسويق إلكتروني سعودي محترف، متخصص في تيك توك وإنستقرام.
    المهمة المطلوبة هي: {task}.
    
    قواعد الرد:
    1. تيك توك: اقترح فكرة مقطع عفوي (Hook) يبدأ بكلمة قوية تجذب المشاهد، ثم نص المقطع، ونهاية قوية (Call to Action) توجههم للرابط في البايو.
    2. إنستقرام: اقترح فكرة "بوست" أو "ريلز" بأسلوب بصري جذاب، مع نص (Caption) احترافي، وهاشتاقات قوية للسوق السعودي.
    3. اللهجة: سعودية بيضاء، حماسية، ومقنعة.
    4. التركيز: إبراز "القيمة" (ليش يشتري العميل الآن؟).
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response.choices[0].message.content)
        await state.clear()
        await message.answer("ها، وش رايك؟ إذا تبي نشتغل على شيء ثاني أنا موجود! 🚀", reply_markup=main_menu)
    except Exception as e:
        await message.answer("يا بطل، صار ضغط بسيط، جرب ترسل طلبك مرة ثانية.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
