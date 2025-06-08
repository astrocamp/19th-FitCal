// static/assets/scripts/form_logic.js

document.addEventListener('alpine:init', () => {
  Alpine.data('formLogic', () => ({
    imagePreview: '',
    imageFile: null,
    loadingEstimation: false,
    estimatedCalories: null,
    fileName: '',

    init() {
      console.log('formLogic: init() 函式被呼叫'); // --- 添加此日誌 ---

      const caloriesInput = document.getElementById('id_calories');
      if (caloriesInput && caloriesInput.value) {
        this.estimatedCalories = parseFloat(caloriesInput.value) || null;
      }

      const imageInput = document.getElementById('id_image');
      if (imageInput) {
        if (imageInput.dataset.initialUrl) {
          this.imagePreview = imageInput.dataset.initialUrl;
          const urlParts = imageInput.dataset.initialUrl.split('/');
          this.fileName = urlParts[urlParts.length - 1];
        }

        // 檢查監聽器是否已經存在（儘管 Alpine 通常會處理這個）
        // 如果 init() 執行多次，這行程式碼是重複監聽器的常見原因。
        imageInput.addEventListener('change', (event) => {
          console.log('formLogic: imageInput change 事件被觸發'); // --- 添加此日誌 ---
          this.handleFileChange(event.target.files[0], imageInput);
        });
      }
    },

    handleFileChange(file, inputElement = null) {
      console.log('formLogic: handleFileChange() 函式被呼叫，檔案:', file ? file.name : 'null'); // --- 添加此日誌 ---
      if (file) {
        this.imageFile = file;
        this.fileName = file.name;

        let targetInput = inputElement;
        if (!targetInput) {
          targetInput = document.getElementById('id_image');
        }

        if (targetInput) {
          const dataTransfer = new DataTransfer();
          dataTransfer.items.add(file);
          targetInput.files = dataTransfer.files;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
        this.estimatedCalories = null;
      } else {
        this.imageFile = null;
        this.imagePreview = '';
        this.fileName = '';
        this.estimatedCalories = null;

        let targetInput = inputElement;
        if (!targetInput) {
          targetInput = document.getElementById('id_image');
        }
        if (targetInput) {
          targetInput.value = '';
        }

        const caloriesInput = document.getElementById('id_calories');
        if (caloriesInput) caloriesInput.value = '';
      }
    },

    handleFileDrop(event) {
      event.preventDefault();
      console.log('formLogic: handleFileDrop() 函式被呼叫'); // --- 添加此日誌 ---
      const file = event.dataTransfer.files[0];
      if (file) {
        const imageInput = document.getElementById('id_image');
        this.handleFileChange(file, imageInput);
      }
    },

    async estimateCalories() {
      console.log('formLogic: estimateCalories() 函式被呼叫'); // --- 添加此關鍵日誌 ---

      if (!this.imageFile) {
        alert('請先選擇一張圖片才能估算卡路里！');
        return;
      }

      this.loadingEstimation = true;
      this.estimatedCalories = null;

      try {
        const base64Image = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (e) => {
            const result = e.target.result;
            const pureBase64 = result.split(',')[1];
            resolve(pureBase64);
          };
          reader.onerror = (error) => {
            reject(error);
          };
          reader.readAsDataURL(this.imageFile);
        });

        const mimeType = this.imageFile.type;

        const response = await fetch(ESTIMATE_CALORIES_API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
          },
          body: JSON.stringify({
            image_base64: base64Image,
            mime_type: mimeType,
          }),
        });

        const responseData = await response.json();

        if (response.ok && responseData.success) {
          const estimatedValue = parseFloat(responseData.estimated_calories);
          this.estimatedCalories = isNaN(estimatedValue) ? null : estimatedValue;

          const caloriesInput = document.getElementById('id_calories');
          if (caloriesInput) {
            caloriesInput.value = this.estimatedCalories !== null ? this.estimatedCalories : '';
          }
          console.log('formLogic: API 估算成功，結果:', this.estimatedCalories); // --- 添加此日誌 ---
          alert('卡路里估算完成！估算值：' + (this.estimatedCalories !== null ? this.estimatedCalories : 'N/A') + ' kcal');
        } else {
          const errorMessage = responseData.message || responseData.error || '未知錯誤。';
          console.error('API 估算失敗:', responseData);
          alert('卡路里估算失敗：' + errorMessage);
          this.estimatedCalories = null;
          const caloriesInput = document.getElementById('id_calories');
          if (caloriesInput) caloriesInput.value = '';
        }
      } catch (error) {
        console.error('估算卡路里時發生錯誤:', error);
        alert('卡路里估算服務暫時不可用，請稍後再試。');
        this.estimatedCalories = null;
        const caloriesInput = document.getElementById('id_calories');
        if (caloriesInput) caloriesInput.value = '';
      } finally {
        this.loadingEstimation = false;
        console.log('formLogic: estimateCalories() 執行完畢'); // --- 添加此日誌 ---
      }
    },
  }));
});
