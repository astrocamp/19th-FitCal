from django.shortcuts import render

from members.models import Member

from .models import Product


def index(request):
    products = Product.objects.all()
    members = Member.objects.all()  # 新增會員資料
    return render(
        request, 'products/index.html', {'products': products, 'members': members}
    )
