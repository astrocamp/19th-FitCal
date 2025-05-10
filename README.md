# FitCal

### 專注<u>**卡路里**</u>均衡飲食的訂餐平臺

## 版本及套件

- `Python`版本：3.13
- `Node.js`版本：20.x以上
- 安裝 `uv`套件：
  - Windows：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - Mac：`brew install uv`
- 安裝PostgreSQL：[https://www.postgresql.org/](https://www.postgresql.org/)
  - 版本17.4
  - 請記錄`dbname`、`username`、`password`，後續設定會用到

## Setup

- `uv sync`同步虛擬環境、格式器及套件
- `npm run reset`同步前端格式器及套件(會安裝缺失套件以及刪除失效套件)
- 複製`.env-example`到專案根目錄下，重新命名為`.env`

  - 修改`SECRET_KEY`為自己的版本(**如為團體專案請統一設定**)：  
    可通過終端機指令產生：`uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  - 修改`DATABASE_URL`(範例)：  
     `dbname:MyDB`  
     `username:postgres`  
     `password:1234`  
     `hostname:localhost`  
     修改為：  
     `DATABASE_URL=postgres://postgres:1234@localhost/MyDB`

- `uv run manage.py migrate`同步資料庫設定
- `uv run manage.py runserver`啟動伺服器  
  或  
  `npm run dev`同時啟動`esbuild`，`Tailwind`的監聽及`django server`
