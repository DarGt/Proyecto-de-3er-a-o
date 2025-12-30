
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.templatetags.static import static
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-y1d#0ilqbz4idy7gs^yb-wwoxo$-$2-%!mjxncabvrwh)01a9('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts.apps.AccountsConfig',

    'import_export',

    'guardar',
    'crispy_forms',
    'crispy_bootstrap5',
    'core',
    'cart',
    'payment'


]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'guardar_productos.urls'

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
                    'django.template.context_processors.static',
                    'django.template.context_processors.media',
                    'cart.context_processors.cart',
                ],
            },
    },
]

WSGI_APPLICATION = 'guardar_productos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Motor de base de datos
        'NAME': 'final',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field


# Root imagenes

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # !!!!!!!
#!!! claves que despues os. para que no se vean despues Cambiar¡
#claves de stripe
STRIPE_SECRET_KEY = 'AQUI_IRA_LA_CLAVE_EN_PRODUCCION'
STRIPE_SECRET_KEY = 'AQUI_IRA_LA_CLAVE_EN_PRODUCCION'
STRIPE_API_VERSION = '2022-11-15'

#configuracion de correo
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'basuradecorreo2002@gmail.com'
EMAIL_HOST_PASSWORD = 'rzyqghwrclqpfstn'   #!!!cambiar esto que no se vea .ven
EMAIL_USE_TLS = True
# Mi unfold admin content


UNFOLD = {
    "SITE_TITLE": "Ferretería",
    "SITE_HEADER": "Administración Ferretería",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("logo/LogoFerrer.png"),
        "dark": lambda request: static("logo/LogoFerrer.png"),
    },
    "SITE_LOGO": {
        "light": lambda request: static("logo/LogoFerrer.png"),
        "dark": lambda request: static("logo/LogoFerrer.png"),
    },
    "SITE_SYMBOL": "speed",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("logo/LogoFerrer.png")
        },
    ],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {"500": "33 150 243"},
        "background": {
            "DEFAULT": "24 34 56",
            "foreground": "255 255 255",
            "muted": "44 62 80",
            "subtle": "44 62 80",
        },
        "foreground": {
            "DEFAULT": "255 255 255",
            "muted": "200 200 200",
            "subtle": "150 150 150",
        },
    },
    # la barra lateral del dashboard para agregar las aplicaciones de la app
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": True,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Usuarios Ferreteria"),
                "separator": True,  # Top border
                "collapsible": True,
                "items": [
                    {
                        "title": _("Panel de Administracion"),
                        "icon": "home",  # Aca se puede colocar cualquier icono de: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "badge": "",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Usuarios"),
                        # Aca se puede colocar cualquier icono de: https://fonts.google.com/icons
                        "icon": "group_add",
                        "link": reverse_lazy("admin:accounts_usuario_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],

            },
            {
                "title": _("Productos Ferreteria"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Panel de Administracion"),
                        "icon": "home",  # Aca se puede colocar cualquier icono de: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "badge": "",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Guardar Productos"),
                        # Aca se puede colocar cualquier icono de: https://fonts.google.com/icons
                        "icon": "store",
                        "badge": lambda request: Producto.objects.count(),
                        "link": reverse_lazy("admin:guardar_producto_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Clases"),
                        # Aca se puede colocar cualquier icono de: https://fonts.google.com/icons
                        "icon": "folder_managed",
                        "link": reverse_lazy("admin:guardar_clase_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Sugerencia de eliminacion"),
                        "icon": "receipt_long_off",
                        "link": reverse_lazy("admin:guardar_sugerenciaeliminacion_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],

            },
            {
                "title": _("Pagos Ferreteria"),
                "separator": True,  # Top border
                "collapsible": True,
                "items": [
                    {
                        "title": _("Ordenes"),
                        "icon": "payments",  # Aca se puede colocar cualquier icono de: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:payment_order_changelist"),
                        "badge": "",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Shipping Address"),
                        # Aca se puede colocar cualquier icono de: https://fonts.google.com/icons
                        "icon": "contact_mail",
                        "link": reverse_lazy("admin:payment_shippingaddress_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Ordenes de Productos"),
                        # Aca se puede colocar cualquier icono de: https://fonts.google.com/icons
                        "icon": "shopping_bag",
                        "link": reverse_lazy("admin:payment_orderitem_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],

            },
        ],
    },
     "DASHBOARD_CARDS": [
        {
            "title": "Productos",
            "icon": "store",
            "value": lambda request: Producto.objects.count(),
            "link": reverse_lazy("admin:guardar_producto_changelist"),
            "color": "primary",
        },
        {
            "title": "Usuarios",
            "icon": "group_add",
            "value": lambda request: User.objects.count(),
            "link": reverse_lazy("admin:accounts_usuario_changelist"),
            "color": "background",
        },
        {
            "title": "Órdenes",
            "icon": "payments",
            "value": lambda request: Order.objects.count(),
            "link": reverse_lazy("admin:payment_order_changelist"),
            "color": "primary",
        },
    ],
    # NUEVO: Permitir modo oscuro/claro por usuario
    "THEME_SWITCHER": True,
    # NUEVO: Mostrar notificaciones y badges en el sidebar
    "SIDEBAR_BADGES": True,
    # NUEVO: Permitir cambiar iconos desde el admin (requiere unfold.contrib.settings)
    "ENABLE_ADMIN_SETTINGS": True,

}
