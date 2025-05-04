from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = "IntelliTeach"
COLLEGE_NAME = 'IntelliTeach'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5tm(^75*kg(d6=f&nn91-esky50y#0zuqzd87dp^(l@bl^4n5c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Admin',
] 

INSTALLED_APPS += [                                                                                                                                                                                     
    'Home',
    'teachers',
    'student'
]


AUTH_USER_MODEL = 'Admin.AuthUser'
# AUTHENTICATION_BACKENDS = ['Admin.backends.AuthBackend']

EMAIL_HOST = 'mail.vizion2050.in'
DEFAULT_FROM_EMAIL = 'intelliteach@gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'intelliteach@vizion2050.in'
EMAIL_HOST_PASSWORD = 'IgCMS@r#99'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'IgCMS.urls'

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//' # RabbitMQ
CELERY_BEAT_SCHEDULE = {
    'attendance_runner': {
        'task': 'Admin.tasks.get_Attendance',
        'schedule': timedelta(minutes=3),
    },
    'att_email': {
        'task': 'Admin.tasks.send_attendance_email',
        'schedule': timedelta(hours=24),
    },
}

CELERY_TIMEZONE = 'Asia/Kolkata'
FACE_RECOGNITION_THRESHOLD = 0.6
FACE_RECOGNITION_TIMEOUT = 120
FACE_RECOGNITION_DAY = 'Auto' # Add 'Auto' to automatically detect the day

TIME_TABLE_WEEKEND_CLASSES = False # If True, the timetable will be generated for weekend classes
TOTAL_MARKS = 40

TIME_RANGE_ORDER = [
    '09:00 AM - 10:00 AM',
    '10:00 AM - 11:00 AM',
    '11:00 AM - 12:00 PM',
    '12:00 PM - 01:00 PM',
    '02:00 PM - 03:00 PM',
    '03:00 PM - 04:00 PM',
    '04:00 PM - 05:00 PM'
] # This is the order of the time range in the timetable

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

WSGI_APPLICATION = 'IgCMS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
# DEFAULT_FILE_STORAGE = 'Admin.storage.CustomFileSystemStorage'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'Home/static'
]

MEDIA_ROOT = BASE_DIR / 'media' 
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
