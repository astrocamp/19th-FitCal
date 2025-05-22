export default function myGeocode() {
  return {
    // 取得csrf token
    csrfToken: document.querySelector('input[name="csrfmiddlewaretoken"]')?.value,
    type: '我的目前位置',
    address: '',
    latitude: null,
    longitude: null,
    radius: 1,
    tomtom_addr: '',
    getLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((pos) => {
          this.latitude = pos.coords.latitude;
          this.longitude = pos.coords.longitude;
          this.type = '我的目前位置';
          this.address = '';
        });
      } else {
        alert('瀏覽器不支援定位功能');
        this.latitude = null;
        this.longitude = null;
        this.type = '';
      }
    },
    async getAddress(event) {
      const e = event.target;
      const url = e.dataset.url;
      console.log(url, this.csrfToken);
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': this.csrfToken,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        // 以表單傳送資料
        body: new URLSearchParams({
          address: this.address,
        }),
      });
      if (!resp.ok) {
        alert('無法取得地址');
        return;
      }
      const data = await resp.json();
      this.latitude = data.latitude;
      this.longitude = data.longitude;
      this.tomtom_addr = data.tomtom_addr;
      this.type = '地址位置';
      console.log('data', data);
    },
    // async search(event) {
    //   const e = event.target;
    //   const url = e.dataset.url;
    //   console.log(url, csrfToken);
    //   const resp = await fetch(url, {
    //     method: 'POST',
    //     headers: {
    //       'X-CSRFToken': csrfToken,
    //       'Content-Type': 'application/x-www-form-urlencoded',
    //     },
    //     // 以表單傳送資料
    //     body: new URLSearchParams({
    //       latitude: this.latitude,
    //       longitude: this.longitude,
    //       radius: this.radius,
    //     }),
    //   });
    // },
  };
}
