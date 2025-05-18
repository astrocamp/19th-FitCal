function toggleChatbox() {
  const box = document.getElementById('chatbox');
  box.classList.toggle('hidden');
}

async function sendMessage() {
  const input = document.getElementById('chatbot-input');
  const messages = document.getElementById('chatbot-messages');
  const text = input.value.trim();
  if (!text) return;

  messages.innerHTML += `
    <div class="text-right">
      <div class="inline-block bg-blue-100 text-blue-800 px-3 py-2 rounded-lg my-1 max-w-[70%]">${text}</div>
    </div>`;
  input.value = '';

  const res = await fetch('/chatbot/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text }),
  });

  const data = await res.json();
  messages.innerHTML += `
    <div class="text-left">
      <div class="inline-block bg-gray-200 px-3 py-2 rounded-lg my-1 max-w-[70%]">${data.reply}</div>
    </div>`;
  messages.scrollTop = messages.scrollHeight;
}
