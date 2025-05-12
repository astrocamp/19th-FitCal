from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product
from stores.models import Store

from .forms import CartForm, EditCartItemFormSet, NewCartItemFormSet
from .models import Cart, CartItem


# 這裏是後續以member關聯的購物車的相關功能
@require_POST
def add(req):
    product_id = req.POST.get('product_id')
    quantity = req.POST.get('quantity')
    print(product_id, quantity)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': '商品不存在'})

    cart, created = Cart.objects.get_or_create(
        member=req.user.member, store=product.store, total_price=0
    )
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        return JsonResponse({'success': True, 'message': '商品已成功加入購物車'})
    else:
        cart_item.quantity += int(quantity)
        cart_item.save()
        return JsonResponse(
            {'success': True, 'message': '購物車中已存在該商品，數量+1'}
        )


def index(req):
    # member = req.user.member
    # stores = Store.objects.filter(carts__member=member).distinct()
    # carts = Cart.objects.filter(member=req.user.member)
    member = req.user
    stores = Store.objects.filter(carts__member=member).distinct()
    carts = Cart.objects.filter(member=member)

    if req.method == 'POST':
        cart_form = CartForm(req.POST)
        formset = NewCartItemFormSet(req.POST)
        if cart_form.is_valid() and formset.is_valid():
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

                    # 嘗試找出是否已有相同 product 的項目
                    item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=product,
                        defaults={'quantity': quantity, 'customize': customize},
                    )
                    if not created:
                        # 如果已存在，就加上數量（或視需求改為覆蓋）
                        item.quantity += quantity
                        item.customize = customize  # 可視情況合併或取代
                        item.save()

            return redirect('carts:index')
    return render(
        req, 'carts/index.html', {'carts': carts, 'stores': stores, 'member': member}
    )


def new(req):
    cart_form = CartForm()
    formset = NewCartItemFormSet()

    return render(
        req,
        'carts/new.html',
        {
            'cart_form': cart_form,
            'formset': formset,
        },
    )


def show(req, id):
    member = req.user
    cart = get_object_or_404(Cart, id=id)
    # cart_item = CartItem.objects.filter(cart=cart)
    # carts = Cart.objects.filter(member=req.user)
    cart_item = CartItem.objects.filter(cart__member=member).filter(cart=cart)

    if req.method == 'POST':
        formset = EditCartItemFormSet(req.POST, instance=cart)
        if formset.is_valid():
            formset.save()
            return redirect('carts:show', id=cart.id)
    return render(
        req,
        'carts/show.html',
        {
            'member': member,
            'cart': cart,
            'cart_item': cart_item,
        },
    )


def edit(req, id):
    cart = get_object_or_404(Cart, id=id)
    cart_form = CartForm(instance=cart)
    formset = EditCartItemFormSet(instance=cart)

    return render(
        req,
        'carts/edit.html',
        {'cart_form': cart_form, 'formset': formset, 'id': id},
    )


def delete_cart(req, id):
    cart = get_object_or_404(Cart, id=id)
    cart.delete()
    return redirect('carts:index')


def delete_item(req, id):
    cart_item = get_object_or_404(CartItem, id=id)
    cart_item.delete()
    if cart_item.cart.items.count() == 0:
        cart_item.cart.delete()
        return redirect('carts:index')
    return redirect('carts:show', id=cart_item.cart.id)
