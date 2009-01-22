from logging import Loggable
from django.conf import settings as django_settings
from higgins.site_settings import site_settings
import os
import pickle

class LocalSettings(Loggable):
    log_domain = "conf"

    _local_settings = {}

    def __init__(self):
        # check for the existence of a local settings file
        if os.access(site_settings['LOCAL_SETTINGS_PATH'], os.F_OK):
            # load the local settings
            try:
                f = open(site_settings['LOCAL_SETTINGS_PATH'], 'r')
                LocalSettings._local_settings = pickle.load(f)
                f.close()
            except EOFError, e:
                # ignore empty file error
                pass
            except Exception, e:
                self.log_error("failed to load local settings from '%s': %s" % (site_settings['LOCAL_SETTINGS_PATH'],e))
                raise e
        if 'SECRET_KEY' not in LocalSettings._local_settings:
            # generate a secret key
            from random import choice
            validchars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            secret_key = ''.join([choice(validchars) for i in range(50)])
            LocalSettings._local_settings = {'SECRET_KEY': secret_key}
            self.log_debug("generated a new secret key")
        # load the local settings into the site_settings dict
        for name,value in LocalSettings._local_settings.items():
            site_settings[name] = value
        # load the site_settings into the django_settings object
        django_settings.configure(**site_settings)
        self.log_debug("loaded settings from '%s'" % (site_settings['LOCAL_SETTINGS_PATH']))

    def get(self, name, default=None):
        try:
            return LocalSettings._local_settings[name]
        except:
            pass
        try:
            return django_settings.__getattr__(name)
        except:
            pass
        return default

    def __getitem__(self, name):
        try:
            return LocalSettings._local_settings[name]
        except:
            pass
        return django_settings.__getattr__(name)

    def set(self, **settings):
        for key,value in settings.items():
            LocalSettings._local_settings[key] = value

    def __setitem__(self, name, value):
        LocalSettings._local_settings[key] = value

    def flush(self):
        f = open(site_settings['LOCAL_SETTINGS_PATH'], 'w')
        pickle.dump(LocalSettings._local_settings, f, 0)
        f.close()
        self.log_debug("flushed settings changes")

conf = LocalSettings()
