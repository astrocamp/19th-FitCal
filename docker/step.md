- 打包images
  `docker compose -p fitcal build`
- 執行container
  `docker compose -p fitcal up -d`
- 停止並移除container
  `docker compose down`
- 查看目前運行狀態
  `docker compose ps`
- 執行migrate
  `docker compose -p fitcal exec web python manage.py migrate`

## 備註

-`.env`需要設定`DEBUG=False`以及同步調整`CSRF_COOKIE_SECURE=False`&`SESSION_COOKIE_SECURE=False`才能夠運行正式環境
