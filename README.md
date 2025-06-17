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
<a href="https://drive.google.com/drive/u/0/folders/1qshSmxno1hdNriJnzx2AXc-IsYTD777l">專案介紹</a>

</div>

## 功能介紹

---

- 第三方登入
  <img src="static\images\README\third-party.png"/>
- 快速搜尋
  <img src="static\images\README\search.png" />
- AI客服
  <img src="static\images\README\AI-client.png" />
- 商家/商品收藏 & 店家實時距離顯示
  <img src="static\images\README\collection.png" />
- 第三方金流-LinePay
  <img src="static\images\README\payment.png" />
- 商品圖片卡路里分析
  <img src="static\images\README\cal.png" />
- 銷售分析
  <img src="static\images\README\analysis.png" />

## 使用技術

---

|                                                                                                                                                    前端                                                                                                                                                     |                                                                                      後端                                                                                       |                       資料庫                       |                                                部署                                                |                                                    其他                                                     |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------: | :------------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------: |
| <img width="150" src="static\images\README\HTML-CSS-JS.png" alt="html5-CSS3-JavaScript"/><br><img src="static\images\README\tailwindcss.svg"/><br><img src="static\images\README\daisyUI.png"/><br><img src="static\images\README\alpine_long.svg"/><br><img src="static\images\README\htmx-seeklogo.svg"/> | <img src="static\images\README\python-logo-generic.svg" /> <br><img src="static\images\README\django-logo-positive.svg" /> <br><img src="static\images\README\amazon-s3.png" /> | <img src="static\images\README\postgresSQL.png" /> | <img src="static\images\README\docker-logo-blue.svg" /> <img src="static\images\README\EC2.svg" /> | <img src="htstatic\images\README\LINE-Pay.png"/> <br><img src="static\images\README\mailgun-seeklogo.svg"/> |

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

  - AI 客服
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

  - AI 卡路里分析
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
  - 統籌規劃
