"""
Django settings for fitcal project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
import sys
from pathlib import Path

import environ
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# env init
env = environ.Env()
# 預設會讀取專案根目錄的 `.env`
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

CSRF_TRUSTED_ORIGINS = ['https://fitcal-life.com', 'https://www.fitcal-life.com']
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE')
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')
if sys.platform.startswith('win'):
    GDAL_LIBRARY_PATH = (
        BASE_DIR / '.venv' / 'Lib' / 'site-packages' / 'osgeo' / 'gdal.dll'
    )
    GEOS_LIBRARY_PATH = (
        BASE_DIR / '.venv' / 'Lib' / 'site-packages' / 'osgeo' / 'geos_c.dll'
    )
# Application definition

INSTALLED_APPS = [
    'locations',
    'users',
    'pages',
    'members',
    'orders',
    'products',
    'widget_tweaks',
    'chatbot',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django.contrib.sites',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.line',
    'carts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'stores',
    'storages',
    'search',
    'payment',
    'anymail',
    'django_celery_beat',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # 預設認證後端
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth 認證後端
]

SITE_ID = 1  # Django Sites Framework 的 ID，預設為 1

LOGIN_REDIRECT_URL = '/'  # 登入成功後的重導向 URL
LOGOUT_REDIRECT_URL = '/'  # 登出後的重導向 URL

ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']


MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',  # 語言中介軟體
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'middleware.block_merchant_cart.BlockMerchantCartMiddleware',  # 限制/cart/相關路由只有登入的會員可以使用
]

ROOT_URLCONF = 'fitcal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',  # 在模板中自動提供與多國語言（i18n）相關的變數與功能
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'carts.context_processors.cart_count',  # 加入購物車上下文處理器
            ],
        },
    },
]

WSGI_APPLICATION = 'fitcal.wsgi.application'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APPS': [
            {
                'client_id': env('SOCIAL_AUTH_GOOGLE_CLIENT_ID'),
                'secret': env('SOCIAL_AUTH_GOOGLE_CLIENT_SECRET'),
                'settings': {
                    'scope': [
                        'profile',
                        'email',
                    ],
                    'auth_params': {
                        'access_type': 'online',
                    },
                },
            },
        ],
    },
    'line': {
        'APP': {
            'client_id': env('SOCIAL_AUTH_LINE_CHANNEL_ID'),
            'secret': env('SOCIAL_AUTH_LINE_CHANNEL_SECRET'),
        },
        'SCOPE': ['profile', 'openid', 'email'],
    },
}

SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    # 自動解析 DATABASE_URL
    'default': {
        **env.db(),
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        # 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'NAME': 'users.validators.CustomUserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        'NAME': 'users.validators.CustomCommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_TZ = True

LANGUAGE_CODE = 'zh-hant'

USE_L10N = True

LANGUAGES = [
    ('zh-hant', '繁體中文'),
    ('en', 'English'),
]

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
# 開發階段放前端打包檔的資料夾
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# collectstatic 收集到此資料夾
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field


AUTH_USER_MODEL = 'users.User'

# 未登入狀態下的轉址
LOGIN_URL = 'users:sign_in'

# 所有登入後的轉址地址
LOGIN_REDIRECT_URL = 'stores:index'

# Debug Toolbar
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# AWS S3
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        'OPTIONS': {
            'location': 'media',
        },
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


# AWS S3

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')

MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/'
AWS_QUERYSTRING_AUTH = False  # 若要讓檔案公開可讀
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

USE_I18N = True
LANGUAGE_CODE = 'zh-hant'

CELERY_BROKER_URL = env('REDIS_URL')

# OPENAI KEY CHATBOT

OPENAI_API_KEY = env('OPENAI_API_KEY')
CELERY_BROKER_URL = env('REDIS_URL')
# Mailgun 配置
ANYMAIL = {
    'MAILGUN_API_KEY': os.getenv('MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': os.getenv('MAILGUN_SENDER_DOMAIN'),
    'MAILGUN_FROM_EMAIL': os.getenv('MAILGUN_FROM_EMAIL'),
}
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
DEFAULT_FROM_EMAIL = 'FitCal <Fitcal@mg.fitcal-life.com>'

OPENAI_API_KEY = env('OPENAI_API_KEY')

CELERY_BEAT_SCHEDULE = {
    'check_overdue_orders_every_5min': {
        'task': 'orders.tasks.check_overdue_orders',
        'schedule': crontab(minute='*/5'),
    },
}
# 1. Celery 任務序列化設定
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# 2. 時區
CELERY_TIMEZONE = 'Asia/Taipei'

# 3. 建議加入這行：使用 django-celery-beat 的資料庫排程系統
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
