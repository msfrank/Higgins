# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

site_settings = {
    'HIGGINS_DIR': None,
    'DEBUG': True,
    'TEMPLATE_DEBUG': True,
    'ADMINS': (),
    'MANAGERS': (),
    'DATABASE_ENGINE': 'sqlite3',
    'DATABASE_NAME': None,
    'TIME_ZONE': 'America/Pacific',
    'LANGUAGE_CODE': 'en-us',
    'SITE_ID': 1,
    'USE_I18N': True,
    'MEDIA_ROOT': '',
    'MEDIA_URL': '',
    'ADMIN_MEDIA_PREFIX': '',
    'SECRET_KEY': '',
    'TEMPLATE_LOADERS': (
        'higgins.loader.load_template_source',
        'django.template.loaders.app_directories.load_template_source',
        'django.template.loaders.filesystem.load_template_source',
        ),
    'MIDDLEWARE_CLASSES': (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.middleware.doc.XViewMiddleware',
        ),
    'ROOT_URLCONF': 'higgins.core.urls',
    'TEMPLATE_DIRS': (),
    'INSTALLED_APPS': (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',
        'higgins.core',
        ),
}
