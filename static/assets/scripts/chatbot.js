// 控制訊息框的顯示與隱藏
function toggleChatbox() {
  const box = document.getElementById('chatbox');
  box.classList.toggle('hidden');
}

// 處理送出訊息的功能
async function sendMessage(event) {
  event.preventDefault();
  const input = document.getElementById('chatbot-input');
  const messages = document.getElementById('chatbot-messages');
  const text = input.value.trim(); //去除開頭及結尾
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
  if (!text) return;

  messages.innerHTML += `
    <div class="text-right">
      <div class="text-start inline-block bg-green-100 text-green-800 px-3 py-2 rounded-lg my-1 max-w-[70%]">${text}</div>
    </div>`;
  input.value = '';

  const res = await fetch('/chatbot/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken }, //設定請求的標頭，包含內容類型和 CSRF 令牌。
    body: JSON.stringify({ message: text }), //在 fetch() 中發送 HTTP 請求的「請求內容（body）」，並將它轉換成 JSON 字串格式。
  });

  const data = await res.json();
  messages.innerHTML += `
    <div class="text-left">
      <div class="inline-block bg-gray-200 px-3 py-2 rounded-lg my-1 max-w-[70%]">${data.reply}</div>
    </div>`;
  messages.scrollTop = messages.scrollHeight;
}
