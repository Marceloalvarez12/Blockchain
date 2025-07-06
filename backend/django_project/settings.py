# Archivo: D:\PS\backend\django_project\settings.py

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR apunta a la carpeta 'backend', que contiene 'manage.py'
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables de entorno desde el archivo .env que está en BASE_DIR (backend/.env)
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)


# --- Quick-start development settings - unsuitable for production ---
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-key-for-dev-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

ALLOWED_HOSTS = []


# --- Application definition ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones de terceros
    'rest_framework',

    # Mis aplicaciones
    'credenciales_app',
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

ROOT_URLCONF = 'django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'django_project.wsgi.application'


# --- Database ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- Password validation ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# --- Internationalization ---
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Static files (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'


# --- Default primary key field type ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#################################################################
###           CONFIGURACIÓN DE BLOCKCHAIN & IPFS              ###
#################################################################

# --- Conexión a la Blockchain ---
BLOCKCHAIN_NETWORK_RPC_URL = os.getenv('BLOCKCHAIN_NETWORK_RPC_URL')
DJANGO_WALLET_PRIVATE_KEY = os.getenv('DJANGO_WALLET_PRIVATE_KEY')

# --- Datos del Smart Contract ---
# Se calcula la ruta donde deberían estar los artefactos del contrato.
# Para la estructura `backend/django_project/`, esta definición de BASE_DIR es correcta.
CONTRACT_DATA_PATH = os.path.join(BASE_DIR, 'django_project', 'blockchain_data')

# ======================================================================
#                     ¡LÍNEAS DE DEPURACIÓN CLAVE!
#   Estas líneas imprimirán en la consola las rutas que Django está usando.
# ======================================================================
print("\n[DEBUG-DJANGO] La ruta BASE_DIR calculada es:", BASE_DIR)
print("[DEBUG-DJANGO] La ruta final para buscar artefactos es:", CONTRACT_DATA_PATH)
print("[DEBUG-DJANGO] ¿Existe esa ruta?", os.path.exists(CONTRACT_DATA_PATH), "\n")
# ======================================================================

SMART_CONTRACT_ADDRESS = None
SMART_CONTRACT_ABI = None

try:
    # Cargar la dirección del contrato desde el JSON
    address_file_path = os.path.join(CONTRACT_DATA_PATH, 'contract-address.json')
    with open(address_file_path, 'r') as f:
        contract_addresses = json.load(f)
    SMART_CONTRACT_ADDRESS = contract_addresses.get('CredencialAlumno')

    # Cargar el ABI del contrato desde el JSON
    abi_file_path = os.path.join(CONTRACT_DATA_PATH, 'CredencialAlumno.json')
    with open(abi_file_path, 'r') as f:
        contract_artifact = json.load(f)
    SMART_CONTRACT_ABI = contract_artifact.get('abi')

    if not SMART_CONTRACT_ADDRESS or not SMART_CONTRACT_ABI:
        print("\nADVERTENCIA: La dirección del contrato o el ABI no se pudieron cargar desde los archivos JSON.\n")
    else:
        # Este mensaje solo se imprimirá si todo se carga correctamente
        print("\n[ÉXITO] Configuración de Blockchain cargada exitosamente.")
        print(f"[ÉXITO] Dirección del Contrato: {SMART_CONTRACT_ADDRESS[:10]}...\n")

        IPFS_API_MULTIADDR = os.getenv('IPFS_API_MULTIADDR')

except FileNotFoundError:
    print("\nADVERTENCIA: Archivos de contrato (contract-address.json o CredencialAlumno.json) no encontrados en la ruta especificada.")
    print("Asegúrate de haber desplegado el Smart Contract con `npx hardhat run scripts/deploy.js --network localhost` desde la carpeta 'blockchain'.\n")
except Exception as e:
    print(f"\n[ERROR] Ocurrió un error inesperado al cargar los archivos del contrato: {e}\n")

    