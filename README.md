# FitCal

---

<div align="center">
  <img src="static\images\logo.png" width="300">
</div>

## 簡介

---

你是否曾因為餐點卡路里感到困擾?

「 FITCAL 」是以點餐平台為基礎,專為販售健康餐的商家提供線上點餐的服務,並加值卡路里客製化功能,協助消費者在短時間內快速找到健康餐販售商家,及提供健康的餐點的平臺。

<div align="center">
  Fit Your Calories, Fit Your Life.<br>
  讓FitCal在健康的道路上助力你前行！<br><br>

<a href="https://fitcal-life.com">fitcal-life.com</a><br>
<a href="https://www.youtube.com/watch?v=6cLQmp8Xfpc">Demo影片</a><br>
<a href="https://drive.google.com/file/d/1agi4KriW24LxEABAsupDi-7Qg-QtOua5/view?usp=sharing">專案介紹</a>
</div>

## 功能介紹

---

- **第三方登入**
  <div align="center">
    <img src="static\images\README\third-party.png"/>
  </div>

- **快速搜尋**
  <div align="center">
    <img src="static\images\README\search.png" />
  </div>

- **AI客服**
  <div align="center">
    <img src="static\images\README\AI-client.png" />
  </div>

- **商家/商品收藏 & 店家實時距離顯示**
  <div align="center">
    <img src="static\images\README\collection.png" />
  </div>

- **第三方金流-LinePay**
  <div align="center">
    <img src="static\images\README\payment.png" />
  </div>

- **商品圖片卡路里分析**
  <div align="center">
    <img src="static\images\README\cal.png" />
  </div>

- **銷售分析**
  <div align="center">
    <img src="static\images\README\analysis.png" />
  </div >

## 使用技術

---

- 前端 ：HTML / CSS / JavaScript / TailwindCSS / daisyUI / Alpine.js / HTMX
- 後端 ：Python Django
- 資料庫 ：PostgreSQL
- 部署 ：Docker / AWS EC2
- 其他 :
  - 金流：LinePay
  - Email服務：MailGun
  - 檔案存儲 ：AWS S3
  - AI：OpenAI / Gemini

## 版本及套件

---

- `Python`版本：3.11以上
- `Node.js`版本：20.x以上
- `uv`版本：0.6.14以上
- `postgres`:17.4

## Setup

---

- `uv sync`
- `npm run reset`
- `.env`建立
- `npm run dev`啟動伺服器

## 團隊成員

---

- 鄒幸娟[GitHub](https://github.com/Sachico0912)

  - AI(OpenAI)客服
  - 會員系統
  - 商家收藏

- 洪世賢[GitHub](https://github.com/Hongben8993)

  - 系統排程
  - 自動寄信
  - 第三方登入
  - 商品收藏

- 黃姵青[GitHub](https://github.com/Sabrinaa77)

  - 報表匯出
  - AWS S3 圖片上傳
  - 卡路里搜尋功能
  - 通知視窗

- 黃韋翰[GitHub](https://github.com/ab000641)

  - AI(Gemini)卡路里分析
  - 圖表分析
  - 商家評分

- 楊凱崴[GitHub](https://github.com/nivek-yang)

  - 串接 LINE PAY
  - 串接 LINE BOT
  - 建構訂單系統

- 王嘉禾[GitHub](https://github.com/Andywang-95)
  - 網站部署
  - 購物車
  - 地圖定位
  - 專案容器化
