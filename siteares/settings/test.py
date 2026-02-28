"""
Settings específicas para ambiente de testes.
Herda de dev.py e adiciona configurações otimizadas para testes.
"""

from .dev import *  # noqa: F403, F401

# Ativa debug em testes para evitar erros de staticfiles
DEBUG = True
TEMPLATE_DEBUG = True

# Desabilita ManifestStaticFilesStorage em testes (não precisa de manifest)
# Django 5.x usa STORAGES ao invés de STATICFILES_STORAGE
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Ignora arquivos estáticos ausentes
WHITENOISE_MANIFEST_STRICT = False

# Usa banco em memória para testes rápidos
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Desabilita senha forte para testes rápidos
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Desabilita logging em testes
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "CRITICAL",
    },
}

# Desabilita webpack loader em testes
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": False,
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}

# Configurações de email para testes
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Desabilita throttling em testes de API
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/hour",
        "user": "2000/hour",
    },
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Desabilita whitenoise em testes
MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m.lower()]
