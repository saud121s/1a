# دالة محدثة لإنشاء الملف مع بيانات الطالب في الرأس
def create_professional_doc(content, user_data):
    doc = Document()
    
    # إضافة بيانات الطالب في بداية الملف
    doc.add_paragraph(f"الاسم: {user_data.get('name', '---')}")
    doc.add_paragraph(f"الجامعة: {user_data.get('uni', '---')}")
    doc.add_paragraph(f"اسم الدكتور: {user_data.get('dr', '---')}")
    doc.add_paragraph(f"الرقم الجامعي: {user_data.get('id', '---')}")
    doc.add_paragraph("-" * 30) # خط فاصل جمالي
    
    # إضافة المحتوى
    doc.add_paragraph(content)
    
    file_name = "Academic_Task.docx"
    doc.save(file_name)
    return file_name

# تحديث دالة التعامل مع الرسائل لتطلب البيانات وتستخدمها
@dp.message(F.text)
async def handle_text(message: types.Message):
    uid = message.from_user.id
    
    # التحقق مما إذا كان المستخدم يرسل بياناته وموضوع البحث
    if "الاسم" in message.text and "الجامعة" in message.text:
        # هنا سنقوم باستخراج البيانات (مبسط)
        # يمكنك جعل المستخدم يرسلها في رسالة واحدة منظمة
        await message.answer("جاري معالجة بياناتك وكتابة الملف.. ⏳")
        
        # استخراج افتراضي (يفضل أن يرسل المستخدم البيانات بشكل منظم)
        user_data = {"name": "سعود العنزي", "uni": "كلية الخليج", "dr": "الدكتور سعود", "id": "1282882"}
        
        prompt = f"اكتب بحثاً أكاديمياً عن: {message.text}. رتبه بوضوح وابدأ بالمحتوى مباشرة."
        response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
        
        file_path = create_professional_doc(response.choices[0].message.content, user_data)
        await message.answer_document(FSInputFile(file_path), caption="✅ تم تجهيز ملفك مع البيانات.")
        os.remove(file_path)
    else:
        await message.answer("يرجى إرسال البيانات (الاسم، الجامعة، الدكتور، الرقم الجامعي) متبوعة بموضوع البحث.")
