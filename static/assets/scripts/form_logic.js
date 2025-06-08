// static/assets/scripts/form_logic.js

document.addEventListener('alpine:init', () => {
  Alpine.data('formLogic', () => ({
    // ... (其他狀態變數和 init 函數保持不變) ...
    imagePreview: '',
    imageFile: null,
    loadingEstimation: false,
    estimatedCalories: '',
    fileName: '',

    init() {
      const caloriesInput = document.getElementById('id_calories');
      if (caloriesInput && caloriesInput.value) {
        this.estimatedCalories = caloriesInput.value;
      }

      const imageInput = document.getElementById('id_image');
      if (imageInput) {
        if (imageInput.dataset.initialUrl) {
          this.imagePreview = imageInput.dataset.initialUrl;
          const urlParts = imageInput.dataset.initialUrl.split('/');
          this.fileName = urlParts[urlParts.length - 1];
        }

        imageInput.addEventListener('change', (event) => {
          this.handleFileChange(event.target.files[0]);
        });
      }
    },

    handleFileChange(file) {
      if (file) {
        this.imageFile = file;
        this.fileName = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      } else {
        this.imageFile = null;
        this.imagePreview = '';
        this.fileName = '';
        this.estimatedCalories = '';
        const caloriesInput = document.getElementById('id_calories');
        if (caloriesInput) caloriesInput.value = '';
      }
    },

    handleFileDrop(event) {
      event.preventDefault();
      const file = event.dataTransfer.files[0];
      if (file) {
        this.handleFileChange(file);
      }
    },

    /**
     * 執行卡路里估算，透過 Fetch API 與後端 AI 服務互動
     */
    async estimateCalories() {
      if (!this.imageFile) {
        alert('請先選擇一張圖片才能估算卡路里！');
        return;
      }

      this.loadingEstimation = true;
      this.estimatedCalories = '';

      try {
        // --- 關鍵修改從這裡開始 ---
        const base64Image = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (e) => {
            // 當讀取完成時，解析 Base64 字串並 resolve Promise
            const result = e.target.result;
            // 從完整的 Data URL 中提取純粹的 Base64 字串
            const pureBase64 = result.split(',')[1];
            resolve(pureBase64);
          };
          reader.onerror = (error) => {
            // 如果讀取失敗，reject Promise
            reject(error);
          };
          reader.readAsDataURL(this.imageFile); // 開始讀取檔案
        });
        // --- 關鍵修改到這裡結束 ---

        const mimeType = this.imageFile.type; // 獲取圖片的 MIME 類型

        // 使用原生的 Fetch API 發送 POST 請求到後端 API
        // ESTIMATE_CALORIES_API_URL 變數應在 HTML 模板中定義 (請確保其存在)
        const response = await fetch(ESTIMATE_CALORIES_API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
          },
          body: JSON.stringify({
            image_base64: base64Image, // 現在這裡的 base64Image 確定會有值
            mime_type: mimeType,
          }),
        });

        const responseData = await response.json();

        if (response.ok && responseData.success) {
          this.estimatedCalories = responseData.estimated_calories;
          const caloriesInput = document.getElementById('id_calories');
          if (caloriesInput) {
            caloriesInput.value = responseData.estimated_calories;
          }
          alert('卡路里估算完成！估算值：' + responseData.estimated_calories + ' kcal');
        } else {
          const errorMessage = responseData.message || responseData.error || '未知錯誤。';
          console.error('API 估算失敗:', responseData);
          alert('卡路里估算失敗：' + errorMessage);
          this.estimatedCalories = '';
          const caloriesInput = document.getElementById('id_calories');
          if (caloriesInput) caloriesInput.value = '';
        }
      } catch (error) {
        console.error('估算卡路里時發生錯誤:', error);
        alert('卡路里估算服務暫時不可用，請稍後再試。');
        this.estimatedCalories = '';
        const caloriesInput = document.getElementById('id_calories');
        if (caloriesInput) caloriesInput.value = '';
      } finally {
        this.loadingEstimation = false;
      }
    },
  }));
});
