@dp.message(F.text)
async def process_ai(message: types.Message, state: FSMContext):
    user_state = await state.get_state()
    # إذا لم يختر خدمة، نجعله يختار
    if not user_state:
        return await message.answer("هلا بالتاجر، اختر خدمة من القائمة عشان أضبطك صح! 🚀", reply_markup=main_menu)

    await message.answer("يا بعدي، جالس أفكر لك في فكرة تكسر التيك توك وتخلي المبيعات تطير... 🤖🔥")
    
    # هذه هي التعليمات الجديدة (System Prompt) التي ستغير مستوى الردود تماماً
    system_instruction = """
    أنت خبير تسويق إلكتروني سعودي محترف جداً، متخصص في صناعة محتوى تيك توك وتطوير متاجر سلة.
    طريقتك في الرد:
    1. جذابة، حماسية، وتستخدم مصطلحات السوق السعودي.
    2. إذا طلبت فكرة تسويقية: أعطني (فكرة المقطع، الـ Hook الجذاب للثواني الأولى، نص الكلام، وكيف نطلب منهم الدخول للرابط في البايو).
    3. إذا طلبت وصف منتج: اكتب وصفاً طويلاً، مقنعاً، يركز على الفائدة للعميل، وينتهي بـ CTA (نداء للعمل) قوي لرابط المتجر.
    4. اجعل الردود مرتبة، استخدم الإيموجي، واحرص على تحفيز العميل للشراء فوراً.
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
        await message.answer("ها، وش رايك بالفكرة؟ إذا تبي نعدل عليها أو نشتغل على شيء ثاني أنا موجود! 🚀", reply_markup=main_menu)
    except Exception as e:
        await message.answer("يا بطل، صار ضغط بسيط، جرب ترسل طلبك مرة ثانية.")
