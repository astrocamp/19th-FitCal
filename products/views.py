import base64
import json
import os
import re

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from google.cloud import aiplatform

from common.decorator import member_required, store_required
from stores.models import Category, Store

from .forms import ProductForm
from .models import Product

PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', 'fitcal19-th-50691')
LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION', 'asia-east1')

# 初始化 Gemini AI Platform 客戶端 (確保此代碼只執行一次)
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# 載入 Gemini 模型
# 建議使用 gemini-1.5-flash，因為它速度快、成本低，且免費額度高
gemini_model = aiplatform.preview.generative_models.GenerativeModel('gemini-1.5-flash')


def index(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            store_id = request.POST.get('store_id')
            store = get_object_or_404(Store, id=store_id)
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('stores:show', id=store.id)
    else:
        form = ProductForm()
    products = Product.objects.all()
    return render(
        request,
        'products/index.html',
        {'products': products, 'form': form},
    )


@store_required
def new(request, category_id):
    store = request.user.store
    category = get_object_or_404(Category, id=category_id)
    form = ProductForm(store=store, category=category)
    return render(
        request,
        'shared/business/products/new_product.html',
        {'form': form, 'category': category},
    )


def show(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.POST:
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products:show', product.id)
    return render(
        request,
        'products/show.html',
        {
            'product': product,
        },
    )


@store_required
@require_POST
def create(request, category_id):
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        form = form.save(commit=False)
        form.store = request.user.store
        form.save()
        category = get_object_or_404(
            Category.objects.prefetch_related('products'), id=category_id
        )
        products = category.products.filter(store=request.user.store)
        messages.success(request, f'商品 {form.name} 已新增')
        return render(
            request,
            'shared/business/products/create_success.html',
            {'products': products, 'category': category},
        )
    return render(request, 'products/create.html', {'form': form})


@store_required
def edit(request, id):
    store = request.user.store
    product = get_object_or_404(Product, pk=id)
    category = product.category
    form = ProductForm(instance=product, store=store, category=category)
    return render(
        request,
        'shared/business/products/edit_product.html',
        {'form': form, 'category': category, 'product': product},
    )


@store_required
@require_POST
def update(request, id):
    product = get_object_or_404(Product, pk=id)
    form = ProductForm(request.POST, request.FILES, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, f'商品 {product.name} 已更新')
        category = product.category
        products = Product.objects.prefetch_related('category').filter(
            category=category, store=request.user.store
        )
        return render(
            request,
            'shared/business/products/create_success.html',
            {'products': products, 'category': category},
        )
    return render(
        request,
        'shared/business/products/edit_product.html',
        {'form': form, 'category': category},
    )


@store_required
def delete(request, id):
    product = get_object_or_404(Product, pk=id)
    category = product.category
    product.delete()
    products = Product.objects.prefetch_related('category').filter(
        category=category, store=request.user.store
    )
    messages.success(request, f'商品 {product.name} 已刪除')
    return render(
        request,
        'shared/business/products/create_success.html',
        {'products': products, 'category': category},
    )


@member_required
def collections(request, id):
    product = get_object_or_404(Product, id=id)
    member = request.user.member  # 正常從user取出member

    collections = member.favorite_products

    if collections.filter(id=product.id).exists():
        collections.remove(product)
    else:
        collections.add(product)

    return render(
        request,
        'shared/collections_btn.html',
        {
            'member': member,
            'product': product,
        },
    )


@require_POST  # 確保這個 API 只接受 POST 請求
def estimate_calories_from_image(request):
    # 簡單檢查請求是否為 AJAX 請求，增加安全性
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request type'}, status=400)

    try:
        # HTMX 從前端發送的 JSON 數據會放在 request.body 中
        data = json.loads(request.body)
        image_base64 = data.get('image_base64')  # 獲取 Base64 編碼的圖片數據
        mime_type = data.get(
            'mime_type', 'image/jpeg'
        )  # 獲取圖片的 MIME Type，預設為 jpeg

        if not image_base64:
            return JsonResponse({'error': 'Base64 image data is missing'}, status=400)

        # 將 Base64 字串解碼回圖片位元組數據
        image_bytes = base64.b64decode(image_base64)
        # 建立 Gemini 可讀的圖片 Part
        image_part = aiplatform.preview.generative_models.Part.from_data(
            image_bytes, mime_type=mime_type
        )

        # 定義給 Gemini 的提示詞 (Prompt)
        # 我們會明確要求 Gemini 估算卡路里並提供數字，並提醒它這是估算值
        prompt_parts = [
            image_part,  # 這是圖片數據
            """Based on this food image, estimate the total calorie content for this serving. Provide only the numerical calorie value (kcal) as the first line, followed by a brief list of main ingredients identified and mention that it's an estimation.
            Example Output:
            250 kcal (estimated)
            Ingredients: Rice, chicken, vegetables

            Please provide the estimated calorie value for the food in the image.""",
        ]

        # 呼叫 Gemini API
        response = gemini_model.generate_content(prompt_parts)

        # 解析 Gemini 回傳的文本結果
        text_response = response.text.strip()

        estimated_calories = None
        # 使用正規表達式從回覆的第一行中提取數字 (例如 "250 kcal (estimated)" 中的 250)
        first_line = text_response.split('\n')[0]
        match = re.search(
            r'(\d+)\s*kcal', first_line, re.IGNORECASE
        )  # 尋找數字後接 kcal
        if match:
            try:
                estimated_calories = int(match.group(1))  # 提取第一個匹配到的數字
            except ValueError:
                pass  # 如果轉換失敗，則保持為 None

        if estimated_calories is None:
            # 如果第一行沒提取到，作為備案，嘗試從整個回覆中尋找第一個數字
            numbers = re.findall(r'\b(\d+)\b', text_response)  # 尋找所有獨立的數字
            if numbers:
                estimated_calories = int(numbers[0])  # 取第一個找到的數字作為備案

        if estimated_calories is None:
            # 如果最終還是沒有提取到數字，給一個預設值，例如 0
            estimated_calories = 0  # 讓前端可以接收並顯示 0，或提示錯誤
            print(f'警告：未能從 Gemini 回應中提取到卡路里數字：{text_response}')

        # 返回 JSON 響應給前端
        return JsonResponse(
            {
                'success': True,
                'estimated_calories': estimated_calories,
                'full_ai_response': text_response,  # 為了調試，可以返回完整的 AI 回應
            }
        )

    except Exception as e:
        # 處理可能發生的錯誤，例如 Gemini API 呼叫失敗、JSON 解析錯誤等
        print(f'呼叫 Gemini 錯誤：{e}')  # 在伺服器日誌中打印錯誤
        return JsonResponse(
            {
                'error': str(e),
                'message': '卡路里估算服務暫時不可用，請手動輸入或稍後再試。',
            },
            status=500,
        )
