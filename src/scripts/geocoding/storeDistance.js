export default function storeDistance(url, storeId) {
  return {
    displayText: '正在定位中...',
    fetchDistance() {
      if (!navigator.geolocation) {
        this.displayText = '無法取得您的位置';
        return;
      }
      if (storeId) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            fetch(`${url}?store_id=${storeId}&lat=${lat}&lng=${lng}`)
              .then((response) => response.json())
              .then((data) => {
                this.displayText = `距離您約 ${data.distance_km} 公里`;
              })
              .catch(() => {
                this.displayText = '無法取得距離資料';
              });
          },
          (error) => {
            this.displayText = '定位失敗';
          },
        );
      } else {
        navigator.geolocation.getCurrentPosition((position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          fetch(`${url}?lat=${lat}&lng=${lng}`)
            .then((response) => response.json())
            .then((data) => {
              document.querySelectorAll('[data-store-id]').forEach((el) => {
                const id = el.dataset.storeId;
                const distance = data[id];
                if (distance) {
                  el.textContent = `距離您約 ${distance} 公里`;
                } else {
                  el.textContent = `無法取得距離`;
                }
              });
            });
        });
      }
    },
  };
}
