from docx import Document  # تأكد من إضافة هذا السطر في الأعلى

@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text == "/start": 
        user_sessions.pop(message.from_user.id, None)
        return await start(message)
    
    uid = message.from_user.id
    if uid in user_sessions and user_sessions[uid]["state"] == "waiting_info":
        await message.answer("جاري كتابة وتنسيق ملف الـ Word الخاص بك.. ⏳")
        
        # 1. توليد المحتوى
        prompt = f"اكتب {user_sessions[uid]['type']} مفصل واحترافي بناءً على البيانات: {message.text}. رتبه كملف أكاديمي كامل."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        content = response.choices[0].message.content
        
        # 2. إنشاء ملف Word
        doc = Document()
        doc.add_heading('الملف الأكاديمي', 0)
        doc.add_paragraph(content)
        file_name = "Academic_File.docx"
        doc.save(file_name)
        
        # 3. إرسال الملف
        from aiogram.types import FSInputFile
        await message.answer_document(FSInputFile(file_name), caption="✅ تم تجهيز ملفك الأكاديمي، تفضل:")
        
        # تنظيف
        os.remove(file_name)
        user_sessions.pop(uid)
    else:
        await message.answer("اختر خدمة من القائمة أولاً.")
