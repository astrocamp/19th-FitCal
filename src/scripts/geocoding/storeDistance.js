export default function storeDistanceComponent(storeId, url) {
  return {
    displayText: '正在定位中...',
    fetchDistance() {
      if (!navigator.geolocation) {
        this.displayText = '無法取得您的位置';
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          console.log(lat, lng);
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
    },
  };
}
