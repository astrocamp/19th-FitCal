from .models import Cart, CartItem


# 商品加入購物車
def add_to_cart(member, cart_form, formset):
    store = cart_form.cleaned_data['store']
    # 檢查是否已有相同 member 與 store 的 cart
    cart, created = Cart.objects.get_or_create(
        member=member,
        store=store,
        defaults={
            'note': cart_form.cleaned_data.get('note', ''),
            'total_price': cart_form.cleaned_data.get('total_price', 0),
        },
    )

    if not created:
        # 若是已存在的 cart，更新欄位（視情況而定）
        cart.note = cart_form.cleaned_data.get('note', '')
        cart.total_price = cart_form.cleaned_data.get('total_price', 0)
        cart.save()

        # 手動儲存每個 form
    for form in formset:
        if form.cleaned_data:
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            customize = form.cleaned_data.get('customize', '')

            # 找出是否已有相同 product 的項目
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'customize': customize},
            )
            if not created:
                # 如果已存在，就加上數量
                item.quantity += quantity
                item.customize = customize
                item.save()
