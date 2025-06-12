# 使用 Python 3.13 Slim 作為基礎映像
FROM python:3.13-slim

# 安裝必要套件
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    # gdal-bin \
    # libgdal-dev \
    # libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 先複製依賴檔案
COPY pyproject.toml uv.lock ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 安裝套件
RUN uv export --no-dev > requirements.txt && \
    uv pip install --system -r requirements.txt
# ^測試使用！！！！！
# ^實際上線需要改用--no-dev版本
# RUN uv export > requirements.txt && \
#     uv pip install --system -r requirements.txt

# 再複製其他程式碼
COPY . .

# 安裝 Gunicorn
RUN uv pip install --system gunicorn

# 開放 Gunicorn port
EXPOSE 8000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh