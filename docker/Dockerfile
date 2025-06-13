FROM python:3.11-slim

RUN apt-get update && apt-get install -y software-properties-common curl

# 加入 sid（unstable）套件來源，方便拿新版 libgdal
RUN echo "deb http://deb.debian.org/debian sid main" > /etc/apt/sources.list.d/sid.list

# 先更新套件快取
RUN apt-get update

# 從 sid 安裝新版 libgdal 和相關套件（會覆蓋舊版本）
RUN apt-get -t sid install -y gdal-bin libgdal-dev libgeos-dev gcc g++ libpq-dev

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv pip install --system --no-deps . \
    && uv export --no-dev > requirements.txt \
    && uv pip install --system -r requirements.txt

COPY . .

RUN uv pip install --system gunicorn

EXPOSE 8000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
