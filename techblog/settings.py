"""
Django settings for techblog project"""
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production-use-env-file')
DEBUG = config('DEBUG', default='False') == 'True'
CSRF_TRUSTED_ORIGINS = [
    'https://*.data-science.uz',
    'https://data-science.uz',
    'http://data-science.uz',
    'http://www.data-science.uz',
    'http://localhost',
    'http://127.0.0.1',
]
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Sites framework (allauth uchun zarur)
    'django.contrib.sites',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_summernote',
    # allauth — Google OAuth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # Local
    'apps.accounts',
    'apps.articles',
    'apps.comments',
    'apps.analytics',

    'mdeditor',
]


MDEDITOR_CONFIGS = {
    'default': {
        'width': '100%',
        'language': 'en',
        'height': 500,
        'toolbar': [
            "undo", "redo", "|",
            "bold", "del", "italic", "quote", "uppercase", "lowercase", "|",
            "h1", "h2", "h3", "h5", "h6", "|",
            "list-ul", "list-ol", "hr", "|",
            "link", "reference-link", "image", "code", "preformatted-text",
            "code-block", "table", "datetime",
            "emoji", "html-entities", "pagebreak",
            "||",                              # ← ajratgich
            "watch", "preview", "fullscreen", "clear", "search", "|",
            "help", "info"
        ],
        'upload_image_formats': ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
        'image_folder': 'editor',
        'theme': 'dark',
        'preview_theme': 'default',
        'editor_theme': 'default',
        'toolbar_autofixed': True,
        'search_replace': True,
        'emoji': True,
        'tex': True,
        'flow_chart': True,
        'sequence_diagram': True,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.analytics.middleware.VisitTrackingMiddleware',
]

ROOT_URLCONF = 'techblog.urls'

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
                'apps.articles.context_processors.nav',
            ],
        },
    },
]

WSGI_APPLICATION = 'techblog.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='techblog_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# CORS

CORS_ALLOW_ALL_ORIGINS = DEBUG

# Summernote
SUMMERNOTE_THEME = 'bs4'
SUMMERNOTE_CONFIG = {
    'iframe': True,
    'summernote': {
        'airMode': False,
        'width': '100%',
        'height': '480',
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear', 'italic', 'strikethrough', 'superscript', 'subscript']],
            ['fontname', ['fontname']],
            ['fontsize', ['fontsize']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video', 'hr']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],
    },
    'attachment_filesize_limit': 10 * 1024 * 1024,  # 10MB
}

# ─────────────────────────────────────────────────────────────
# Email — zayavka qabul qilinganda foydalanuvchiga xabar yuborish
# Sozlanmagan bo'lsa (dev) xatlar konsolga chiqadi.
# Production'da .env'da EMAIL_BACKEND'ni SMTP'ga o'zgartiring.
# ─────────────────────────────────────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default='True') == 'True'
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='DataScience <noreply@data-science.uz>')
SITE_URL = config('SITE_URL', default='https://data-science.uz')

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ─────────────────────────────────────────────────────────────
# django-allauth — Google OAuth orqali kirish
# ─────────────────────────────────────────────────────────────
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Django standart backend (username/parol orqali kirish saqlanadi)
    'django.contrib.auth.backends.ModelBackend',
    # allauth backend (Google va boshqa social login uchun)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Google credentials — .env'dan o'qiladi (hardcode QILINMAYDI)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# Tezkor va oraliq formasiz oqim:
# Google tugmasi bosilgach → to'g'ridan avtomatik ro'yxatdan o'tib bosh sahifaga
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapter.AutoSignupAdapter'
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_QUERY_EMAIL = True
# username majburiy bo'lsa ham, allauth email/ismdan avtomatik unikal username
# generatsiya qiladi (populate_username), shuning uchun to'qnashuvda forma chiqmaydi.

X_FRAME_OPTIONS = 'SAMEORIGIN'
