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

# --- 舊的 Vertex AI 相關變數，現在已不再需要，可以註釋或移除 ---
# PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', 'fitcal19-th-50691')
# LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')

# 設定 Google Generative AI 的 API Key
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
        gemini_model = genai.GenerativeModel(
            'gemini-1.5-flash'
        )  # 建議改用 vision 模型，對圖片處理更好
        print(
            'Gemini model "gemini-pro-vision" loaded successfully with google-generativeai.'
        )
    else:
        print('錯誤：API Key 未設置，無法初始化 Gemini 模型。')
except Exception as e:
    print(f'Error initializing or loading Gemini model with google-generativeai: {e}')
    # 在實際應用中，您可能需要更健壯的錯誤處理，例如日誌記錄或發送警報

# --- 以下是您的原有的視圖函式，沒有修改 ---


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
    print('--- 進入 estimate_calories_from_image API 偵錯資訊 ---')
    print(f'請求方法: {request.method}')
    print(f'請求頭 (Headers): {request.headers}')
    print(f'內容類型 (Content-Type): {request.content_type}')
    print(f'原始請求體 (Raw Request Body): {request.body}')
    print('--- 偵錯資訊結束 ---')

    # 簡單檢查請求是否為 AJAX 請求，增加安全性
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print('錯誤：請求類型無效，不是 XMLHttpRequest。')
        return JsonResponse({'error': 'Invalid request type'}, status=400)

    try:
        # 檢查請求的 Content-Type 是否為 application/json
        if request.content_type != 'application/json':
            print(
                f'錯誤：Content-Type 不正確 - 實際為 {request.content_type}，預期為 application/json。'
            )
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Invalid Content-Type, expected application/json',
                },
                status=400,
            )

        # 嘗試解析 request.body
        # HTMX 從前端發送的 JSON 數據會放在 request.body 中
        data = json.loads(request.body)
        print(f'成功解析請求體為 JSON: {data}')

        image_base64 = data.get('image_base64')  # 獲取 Base64 編碼的圖片數據
        mime_type = data.get(
            'mime_type', 'image/jpeg'
        )  # 獲取圖片的 MIME Type，預設為 jpeg

        if not image_base64:
            print('錯誤：Base64 圖片數據缺失。')
            return JsonResponse({'error': 'Base64 image data is missing'}, status=400)

        # 將 Base64 字串解碼回圖片位元組數據
        image_bytes = base64.b64decode(image_base64)

        # *** 關鍵修改：使用 genai.upload_file 或直接構造 Content 內容 ***
        # 最直接的方式是將圖片bytes直接放入Content列表中
        # 或使用 genai.types.Blob
        # 但由於您無法直接導入 Part，我們嘗試以下方式：
        # 這裡我們將圖片數據作為 BytesIO 對象傳遞給模型，
        # 或者直接作為字典傳遞，讓 genai 處理其內部類型

        # 根據 google-generativeai 的最新使用方式，通常是直接傳遞字典或 BytesIO 對象
        # 嘗試直接傳遞字典，這是最常見且穩定的方式
        image_content = {'mime_type': mime_type, 'data': image_bytes}

        # 定義給 Gemini 的提示詞 (Prompt)
        prompt_parts = [
            image_content,  # 這是圖片數據，現在作為字典傳遞
            """Based on this food image, estimate the total calorie content for this serving. Provide only the numerical calorie value (kcal) as the first line, followed by a brief list of main ingredients identified and mention that it's an estimation.
            Example Output:
            250 kcal (estimated)
            Ingredients: Rice, chicken, vegetables

            Please provide the estimated calorie value for the food in the image.""",
        ]

        # 檢查 gemini_model 是否已成功載入
        if gemini_model is None:
            print('錯誤：Gemini 模型未成功載入。')
            return JsonResponse(
                {'success': False, 'error': 'Gemini model is not initialized.'},
                status=500,
            )

        # 呼叫 Gemini API
        print('正在呼叫 Gemini API 進行估算...')
        # 注意：對於多模態模型，模型名稱應為 'gemini-pro-vision'
        response = gemini_model.generate_content(prompt_parts)
        print('Gemini API 呼叫完成。')

        # 解析 Gemini 回傳的文本結果
        text_response = response.text.strip()
        print(f'Gemini 原始回應: {text_response}')

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
            print(
                f'警告：未能從 Gemini 回應中提取到卡路里數字，設定為 0。原始回應：{text_response}'
            )

        # 返回 JSON 響應給前端
        print(f'成功估算卡路里：{estimated_calories} kcal。返回響應。')
        return JsonResponse(
            {
                'success': True,
                'estimated_calories': estimated_calories,
                'full_ai_response': text_response,  # 為了調試，可以返回完整的 AI 回應
            }
        )

    except json.JSONDecodeError as e:
        # 捕獲 JSON 解析錯誤
        print(f'嚴重大於 JSON 解析錯誤 (json.JSONDecodeError): {e}')
        print(
            f'錯誤的請求體內容: {request.body.decode("utf-8", errors="ignore")}'
        )  # 嘗試解碼並打印，忽略編碼錯誤
        return JsonResponse(
            {'success': False, 'error': 'Invalid JSON format in request body.'},
            status=400,
        )
    except Exception as e:
        # 捕獲所有其他未知錯誤，例如 Gemini API 呼叫失敗、網絡問題等
        print(f'發生未預期錯誤 (Exception): {e}')  # 在伺服器日誌中打印錯誤
        return JsonResponse(
            {
                'success': False,
                'error': str(e),
                'message': '卡路里估算服務暫時不可用，請手動輸入或稍後再試。',
            },
            status=500,
        )
