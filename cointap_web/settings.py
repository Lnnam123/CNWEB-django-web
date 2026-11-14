"""
Django settings for cointap_web project.
CoinTap - Quản lý chi tiêu & Trợ lý tài chính cá nhân AI.
Hỗ trợ cả môi trường phát triển cục bộ (SQLite) và máy chủ Linux độc lập (PostgreSQL).
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Tải cấu hình từ file .env nếu có
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-cointap-fintech-key-2026-prod-secret')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# Cho phép mọi Host truy cập trên Production & Local (chống lỗi 400 DisallowedHost)
ALLOWED_HOSTS = ['*']

# CSRF Trusted Origins hỗ trợ deploy Linux Nginx/Reverse Proxy & Tên miền/IP
csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [orig.strip() for orig in csrf_origins_env.split(',') if orig.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
        'http://45.119.213.59',
        'https://45.119.213.59',
        'http://127.0.0.1',
    ]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Ứng dụng CoinTap
    'cointap_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cointap_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cointap_app.context_processors.cointap_context',
            ],
            'builtins': [
                'cointap_app.templatetags.cointap_tags',
            ],
        },
    },
]

# Định dạng hiển thị số & tiền tệ chuẩn Việt Nam (Dấu chấm phân cách hàng nghìn)
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','
NUMBER_GROUPING = 3

WSGI_APPLICATION = 'cointap_web.wsgi.application'

# Cấu hình CSDL: Tự động nhận diện PostgreSQL cho Linux Server hoặc SQLite cục bộ
USE_POSTGRES = os.environ.get('USE_POSTGRES', 'False').lower() in ('true', '1', 'yes') or os.environ.get('DATABASE_URL') is not None

if USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'cointap_db'),
            'USER': os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

# Quốc tế hóa & Múi giờ Việt Nam
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session cấu hình cho tài khoản người dùng & admin
SESSION_COOKIE_AGE = 86400 * 30  # 30 ngày
SESSION_SAVE_EVERY_REQUEST = True

# Gemini API Key cho Trợ lý tài chính CoinTap AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
