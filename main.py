@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("🔍 جاري التحليل الدقيق..")
    
    file = await bot.get_file(message.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    
    # هذه التعليمات (Prompt) تضمن لك دقة عالية واختصاراً شديداً
    system_prompt = (
        "أنت خبير أكاديمي. حل الأسئلة في الصورة التالية (اختيارية ومقالية). "
        "التزم بالآتي: 1. قدم الإجابة برقم السؤال فقط. 2. كن مختصراً جداً. "
        "3. لا تضف أي مقدمات أو عبارات ترحيبية. 4. تأكد من دقة المعلومة العلمية."
    )
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "حل الأسئلة في الصورة:"},
                    {"type": "image_url", "image_url": {"url": url}}
                ]}
            ]
        )
        await message.answer(res.choices[0].message.content)
    except Exception as e:
        await message.answer("عذراً، حدث خطأ أثناء التحليل. تأكد من وضوح الصورة وحاول مجدداً.")
