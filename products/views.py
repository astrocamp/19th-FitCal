import base64
import json
import os
import re

# 導入 Google Generative AI 函式庫
import google.generativeai as genai
from django.contrib import messages

# 移除所有關於 'Part' 的直接導入，我們將使用 genai.upload_file 或 genai.Types.Part
# Django 相關導入
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from common.decorator import member_required, store_required
from stores.models import Category, Store

from .forms import ProductForm
from .models import Product

# 請確保您已在環境變數中設置 GOOGLE_API_KEY (從 .env 檔案載入)
API_KEY = os.environ.get('GOOGLE_API_KEY')
if not API_KEY:
    print(
        "警告: 環境變數 'GOOGLE_API_KEY' 未設置。請在 Google Cloud Console 或 Google AI Studio 中建立並設置 API Key。"
    )
    # 在開發環境可以繼續，但實際部署時應該考慮更嚴格的錯誤處理，例如：
    # raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")

# 初始化 Gemini 模型
# 這段程式碼在 Django 應用啟動時會執行一次
gemini_model = None  # 先初始化為 None
try:
    if API_KEY:
        genai.configure(api_key=API_KEY)
        # 載入 Gemini 模型。這裡不需要 location 參數。
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print(
            'Gemini model "gemini-pro-vision" loaded successfully with google-generativeai.'
        )
    else:
        print('錯誤：API Key 未設置，無法初始化 Gemini 模型。')
except Exception as e:
    print(f'Error initializing or loading Gemini model with google-generativeai: {e}')


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
    member = request.user.member

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


@require_POST
def estimate_calories_from_image(request):
    print('--- 進入 estimate_calories_from_image API ---')
    print(f'請求方法: {request.method}')
    # print(f'請求頭 (Headers): {request.headers}') # 移除不必要的詳細日誌
    print(f'內容類型 (Content-Type): {request.content_type}')
    # print(f'原始請求體 (Raw Request Body): {request.body}') # 移除不必要的詳細日誌
    print('--- 偵錯資訊結束 ---')

    try:
        # 檢查請求的 Content-Type 是否為 application/json
        if request.content_type != 'application/json':
            print(
                f'錯誤：Content-Type 不正確。實際為 "{request.content_type}"，預期為 "application/json"。'
            )
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Invalid Content-Type, expected application/json',
                },
                status=400,
            )

        # 嘗試解析 request.body 中的 JSON 數據
        data = json.loads(request.body)
        print('成功解析請求體為 JSON。')

        image_base64 = data.get('image_base64')
        mime_type = data.get('mime_type', 'image/jpeg')

        if not image_base64:
            print('錯誤：Base64 圖片數據缺失。')
            return JsonResponse(
                {'success': False, 'error': 'Base64 image data is missing'}, status=400
            )

        # 將 Base64 字串解碼回圖片位元組數據
        image_bytes = base64.b64decode(image_base64)

        # 構造用於 Gemini API 的圖片內容
        image_content = {'mime_type': mime_type, 'data': image_bytes}

        # 定義給 Gemini 的提示詞 (Prompt)
        prompt_parts = [
            image_content,
            """Based on this food image, estimate the total calorie content for this serving. Provide only the numerical calorie value (kcal) as the first line, followed by a brief list of main ingredients identified and mention that it's an estimation.
            Example Output:
            250 kcal (estimated)
            Ingredients: Rice, chicken, vegetables

            Please provide the estimated calorie value for the food in the image.""",
        ]

        # 檢查 gemini_model 是否已成功載入
        if gemini_model is None:  # 確保 gemini_model 已經被正確定義和初始化
            print('錯誤：Gemini 模型未成功載入。')
            return JsonResponse(
                {'success': False, 'error': 'Gemini model is not initialized.'},
                status=500,
            )

        # 呼叫 Gemini API
        print('正在呼叫 Gemini API 進行估算...')
        response = gemini_model.generate_content(prompt_parts)
        print('Gemini API 呼叫完成。')

        # 解析 Gemini 回傳的文本結果
        text_response = response.text.strip()
        print(f'Gemini 原始回應: {text_response}')

        estimated_calories = None
        # 從回應的第一行中提取卡路里數字
        first_line = text_response.split('\n')[0]
        match = re.search(r'(\d+)\s*kcal', first_line, re.IGNORECASE)
        if match:
            try:
                estimated_calories = int(match.group(1))
            except ValueError:
                pass  # 如果轉換失敗，保持為 None

        if estimated_calories is None:
            # 如果第一行未找到，嘗試從整個回應中尋找第一個數字
            numbers = re.findall(r'\b(\d+)\b', text_response)
            if numbers:
                estimated_calories = int(numbers[0])

        if estimated_calories is None:
            # 如果最終未能提取到數字，設定為 0 並發出警告
            estimated_calories = 0
            print(
                f'警告：未能從 Gemini 回應中提取到卡路里數字，設定為 0。原始回應：{text_response}'
            )

        # 返回 JSON 響應給前端
        print(f'成功估算卡路里：{estimated_calories} kcal。')
        return JsonResponse(
            {
                'success': True,
                'estimated_calories': estimated_calories,
                'full_ai_response': text_response,  # 為了調試或前端顯示，可以返回完整的 AI 回應
            }
        )

    except json.JSONDecodeError as e:
        # 捕獲 JSON 解析錯誤
        print(f'錯誤：JSON 解析失敗 - {e}')
        # 打印錯誤的請求體內容，有助於調試
        print(f'錯誤的請求體內容: {request.body.decode("utf-8", errors="ignore")}')
        return JsonResponse(
            {'success': False, 'error': 'Invalid JSON format in request body.'},
            status=400,
        )
    except Exception as e:
        # 捕獲所有其他未知錯誤，例如 Gemini API 呼叫失敗、網絡問題等
        print(f'發生未預期錯誤：{e}')
        return JsonResponse(
            {
                'success': False,
                'error': str(e),
                'message': '卡路里估算服務暫時不可用，請手動輸入或稍後再試。',
            },
            status=500,
        )
@store_required
@require_POST
def api_product_sort(request):
    ids = request.POST.getlist('ids')
    store = request.user.store

    for index, pid in enumerate(ids):
        Product.objects.filter(id=pid, store=store).update(sort_order=index)
    messages.success(request, '菜單排序已更新')

    return render(request, 'shared/messages.html')
