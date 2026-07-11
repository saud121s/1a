@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text == "/start": return await start(message)
    uid = message.from_user.id
    if uid in user_sessions and user_sessions[uid]["state"] == "waiting_info":
        await message.answer("جاري إعداد الملف الأكاديمي بتنسيق احترافي.. ⏳")
        
        # هنا التعليمات لضمان نفس التنسيق المطلوب
        prompt = (
            f"أنت خبير أكاديمي. اكتب {user_sessions[uid]['type']} بناءً على البيانات والموضوع التالي: {message.text}.\n"
            "يرجى الالتزام بالهيكل التالي بدقة:\n"
            "1. صفحة الغلاف: يجب أن تحتوي على (اسم البحث/الواجب، اسم الطالب، اسم الجامعة، اسم الدكتور، الرقم الجامعي).\n"
            "2. فهرس المحتويات (Table of Contents) مرتب وواضح.\n"
            "3. المحتوى: مقدمة، فصول مرقمة (Chapter 1, 2, 3...)، وخاتمة.\n"
            "4. الأسلوب: استخدم لغة أكاديمية رصينة، وتأكد من خلو النص من أي أخطاء.\n"
            "5. التنسيق: اجعل العناوين واضحة ليكون الملف جاهزاً للطباعة."
        )
        
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        
        doc = Document()
        # إضافة العناوين والمحتوى
        doc.add_paragraph(response.choices[0].message.content)
        
        file_path = "Academic_Report.docx"
        doc.save(file_path)
        
        await message.answer_document(FSInputFile(file_path), caption="✅ تم تجهيز ملفك الأكاديمي بنظام وتنسيق احترافي.")
        os.remove(file_path)
        user_sessions.pop(uid)
    else: 
        await message.answer("اختر خدمة أولاً عبر /start")
