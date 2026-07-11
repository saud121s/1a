# أضف هذه المتغيرات في بداية الكود بجانب user_sessions
user_quiz_status = {} # لتتبع حالة الاختبار

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    uid = message.from_user.id
    
    # إذا ضغط المستخدم "حل اختبار" مسبقاً
    if user_sessions.get(uid) == "quiz":
        await message.answer("جاري الحل بدقة.. 🔍")
        
        file = await bot.get_file(message.photo[-1].file_id)
        url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        
        # تعليمات مختصرة جداً للـ AI
        prompt = (
            "حل الأسئلة في الصورة التالية بشكل مختصر جداً ومباشر. "
            "التنسيق المطلوب: 1- الجواب، 2- الجواب. "
            "في نهاية إجابتك اكتب جملة: 'انتهيت من حل الاختبار'."
        )
        
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": url}}]}])
        
        await message.answer(response.choices[0].message.content)
        
        # لا نحذف الحالة إذا أردت إرسال صور أخرى، فقط نحذفها إذا أردت
        # user_sessions.pop(uid) 
    else:
        await message.answer("الرجاء الضغط على زر '📸 حل اختبار' أولاً.")
