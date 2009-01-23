from logging import Loggable
from django.conf import settings as django_settings
from higgins.site_settings import site_settings
import os
import pickle

class LocalSettings(Loggable):
    log_domain = "conf"

    _local_settings = {}

    def __init__(self):
        self.local_settings_path = os.path.join(site_settings['HIGGINS_DIR'], "settings.dat")
        # check for the existence of a local settings file
        if os.access(self.local_settings_path, os.F_OK):
            # load the local settings
            try:
                f = open(self.local_settings_path, 'r')
                LocalSettings._local_settings = pickle.load(f)
                f.close()
            except EOFError, e:
                # ignore empty file error
                pass
            except Exception, e:
                self.log_error("failed to load local settings from '%s': %s" % (self.local_settings_path,e))
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
        self._doFlush()
        self.log_debug("loaded settings from '%s'" % self.local_settings_path)

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

    def _doFlush(self):
        f = open(self.local_settings_path, 'w')
        pickle.dump(LocalSettings._local_settings, f, 0)
        f.close()

    def flush(self):
        self._doFlush()
        self.log_debug("flushed settings changes")

conf = LocalSettings()
