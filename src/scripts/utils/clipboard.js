export function copyToClipboard() {
  return {
    copy(text) {
      navigator.clipboard
        .writeText(text)
        .then(() => {
          alert('已複製訂單編號！');
        })
        .catch((err) => {
          console.error('複製失敗:', err);
        });
    },
  };
}
