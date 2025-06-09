document.addEventListener('alpine:init', () => {
  Alpine.data('formLogic', () => ({
    imagePreview: '',
    imageFile: null,
    loadingEstimation: false,
    estimatedCalories: null,
    fileName: '',
    hasAttemptedEstimation: false,

    init() {
      console.log('formLogic: init() 函式被呼叫');

      const caloriesInput = document.getElementById('id_calories');
      if (caloriesInput && caloriesInput.value) {
        this.estimatedCalories = parseFloat(caloriesInput.value) || null;
      }

      const imageInput = document.getElementById('id_image');
      if (imageInput) {
        // 如果有初始圖片URL，則設定預覽和檔名
        if (imageInput.dataset.initialUrl) {
          this.imagePreview = imageInput.dataset.initialUrl;
          const urlParts = imageInput.dataset.initialUrl.split('/');
          this.fileName = urlParts[urlParts.length - 1];
        }

        // --- 移除這行重複綁定事件監聽器，改用 Alpine.js 的機制 ---
        // imageInput.addEventListener('change', (event) => {
        //   console.log('formLogic: imageInput change 事件被觸發');
        //   this.handleFileChange(event.target.files[0], imageInput);
        // });

        // 使用 $watch 監聽 input[type="file"] 的變化
        // 假設您的 products/new.html 中 <input type="file"> 有 x-ref="imageInput"
        // 如果沒有，我們需要這樣改動：
        // this.$refs.imageInput.addEventListener('change', (event) => {
        //   console.log('formLogic: imageInput change 事件被觸發');
        //   this.handleFileChange(event.target.files[0]);
        // });
        // 但為了避免重複代碼，我們將把事件監聽器直接放在 HTML 中。
        // 請確保您的 products/new.html 中的 image input 像這樣：
        // <input type="file" x-ref="imageInput" @change="handleFileChange($event.target.files[0])">
        // 如果不是，我建議您這樣修改 HTML，否則 Alpine.數據綁定可能會出問題。
      }
    },

    // 接收來自 @change 事件的 file 物件
    handleFileChange(file) {
      // --- 移除 inputElement 參數，因為 Alpine 傳入的就是 File 物件 ---
      console.log('formLogic: handleFileChange() 函式被呼叫，檔案:', file ? file.name : 'null');

      const targetInput = document.getElementById('id_image'); // 總是獲取正確的 input 元素

      if (file) {
        this.imageFile = file;
        this.fileName = file.name;

        // 手動更新 input[type="file"] 的 files 屬性
        // 這對於拖放功能很重要，確保後端能收到文件
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
        this.hasAttemptedEstimation = false; // --- 重設估算嘗試狀態 ---
      } else {
        this.imageFile = null;
        this.imagePreview = '';
        this.fileName = '';
        this.estimatedCalories = null;
        this.hasAttemptedEstimation = false; // --- 重設估算嘗試狀態 ---

        if (targetInput) {
          targetInput.value = ''; // 清空檔案輸入框
        }

        const caloriesInput = document.getElementById('id_calories');
        if (caloriesInput) caloriesInput.value = '';
      }
    },

    // 處理拖放檔案
    handleFileDrop(event) {
      event.preventDefault();
      console.log('formLogic: handleFileDrop() 函式被呼叫');
      const file = event.dataTransfer.files[0];
      if (file) {
        this.handleFileChange(file); // 直接呼叫 handleFileChange
      }
    },

    async estimateCalories() {
      console.log('formLogic: estimateCalories() 函式被呼叫');

      if (!this.imageFile) {
        alert('請先選擇一張圖片才能估算卡路里！');
        return;
      }

      this.loadingEstimation = true;
      this.estimatedCalories = null;
      this.hasAttemptedEstimation = true; // --- 設置為 true，表示已嘗試估算 ---

      try {
        const base64Image = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (e) => {
            const result = e.target.result;
            // 確保只傳送純 Base64 字串，移除 'data:image/jpeg;base64,' 等前綴
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
            'X-Requested-With': 'XMLHttpRequest', // 通常用於區分 AJAX 請求
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
            // 如果估算結果是 null，則清空輸入框，否則填入估算值
            caloriesInput.value = this.estimatedCalories !== null ? this.estimatedCalories : '';
          }
          console.log('formLogic: API 估算成功，結果:', this.estimatedCalories);
          alert('卡路里估算完成！估算值：' + (this.estimatedCalories !== null ? this.estimatedCalories : 'N/A') + ' kcal');
        } else {
          const errorMessage = responseData.message || responseData.error || '未知錯誤。';
          console.error('API 估算失敗:', responseData);
          alert('卡路里估算失敗：' + errorMessage);
          this.estimatedCalories = null; // 估算失敗也確保為 null
          const caloriesInput = document.getElementById('id_calories');
          if (caloriesInput) caloriesInput.value = '';
        }
      } catch (error) {
        console.error('估算卡路里時發生錯誤:', error);
        alert('卡路里估算服務暫時不可用，請稍後再試。');
        this.estimatedCalories = null; // 錯誤時也確保為 null
        const caloriesInput = document.getElementById('id_calories');
        if (caloriesInput) caloriesInput.value = '';
      } finally {
        this.loadingEstimation = false;
        console.log('formLogic: estimateCalories() 執行完畢');
      }
    },
  }));
});
