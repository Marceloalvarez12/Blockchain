# django_project/django_project/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent # Esto debería apuntar a la carpeta raíz de Django (django_project)

# Cargar variables de entorno del archivo .env
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'default-unsafe-secret-key-for-dev-only-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

ALLOWED_HOSTS_STRING = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',')]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceros
    'rest_framework',
    # Mis Apps
    'credenciales_app.apps.CredencialesAppConfig', # Forma más explícita de registrar la app
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

ROOT_URLCONF = 'django_project.urls' # Nombre de tu proyecto Django

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Si tienes plantillas a nivel de proyecto
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application' # Nombre de tu proyecto Django


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# Por defecto usa SQLite, configurado para tomar el nombre del .env si se define
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
DB_NAME = os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3') # Si DB_NAME en .env no tiene ruta, lo pone en BASE_DIR

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        # Si usas otras DBs, añade USER, PASSWORD, HOST, PORT desde .env
        # 'USER': os.getenv('DB_USER'),
        # 'PASSWORD': os.getenv('DB_PASSWORD'),
        # 'HOST': os.getenv('DB_HOST'),
        # 'PORT': os.getenv('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'es-es' # O el que prefieras 'en-us'

TIME_ZONE = 'UTC' # O tu zona horaria

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = 'static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles' # Para `collectstatic` en producción
# STATICFILES_DIRS = [BASE_DIR / "static"] # Si tienes archivos estáticos a nivel de proyecto

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Custom Settings para Blockchain y IPFS ---

# Blockchain Config
BLOCKCHAIN_NETWORK_RPC_URL = os.getenv('BLOCKCHAIN_NETWORK_RPC_URL')
DJANGO_WALLET_PRIVATE_KEY = os.getenv('DJANGO_WALLET_PRIVATE_KEY')

# Cargar dirección del contrato y ABI
# Asume que la carpeta `blockchain_data` está en la raíz del proyecto Django (BASE_DIR)
CONTRACT_DATA_PATH = BASE_DIR / 'blockchain_data'
SMART_CONTRACT_ADDRESS = None
SMART_CONTRACT_ABI = None

try:
    with open(CONTRACT_DATA_PATH / 'contract-address.json', 'r') as f:
        contract_addresses = json.load(f)
    SMART_CONTRACT_ADDRESS = contract_addresses.get('CredencialAlumno')

    with open(CONTRACT_DATA_PATH / 'CredencialAlumno.json', 'r') as f:
        contract_artifact = json.load(f)
    SMART_CONTRACT_ABI = contract_artifact.get('abi')

    if not SMART_CONTRACT_ADDRESS or not SMART_CONTRACT_ABI:
        print("ADVERTENCIA: Dirección del contrato o ABI no encontrados en los archivos JSON.")
except FileNotFoundError:
    print(f"ADVERTENCIA: Archivos de contrato (contract-address.json o CredencialAlumno.json) no encontrados en {CONTRACT_DATA_PATH}.")
    print("Asegúrate de haber desplegado el Smart Contract con `npx hardhat run scripts/deploy.js --network localhost` desde la carpeta 'blockchain'.")
except json.JSONDecodeError:
    print("ADVERTENCIA: Error al decodificar los archivos JSON del contrato. Verifica su formato.")


# IPFS Config
IPFS_API_MULTIADDR = os.getenv('IPFS_API_MULTIADDR') # Para la API del nodo IPFS local
IPFS_GATEWAY_URL = os.getenv('IPFS_GATEWAY_URL')   # Para acceder a archivos vía HTTP desde nodo local

# Pinata Config (si se usa)
PINATA_API_KEY = os.getenv('PINATA_API_KEY')
PINATA_SECRET_API_KEY = os.getenv('PINATA_SECRET_API_KEY')
PINATA_GATEWAY_URL = os.getenv('PINATA_GATEWAY_URL') # El gateway de Pinata para acceder a archivos

# Configuración de Django REST Framework (opcional si la necesitas ahora)
# REST_FRAMEWORK = {
# 'DEFAULT_PERMISSION_CLASSES': [
# 'rest_framework.permissions.AllowAny', # Cambia según tus necesidades de seguridad
# ]
# }