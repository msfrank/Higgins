# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from logging import Loggable
from django.conf import settings as django_settings
from higgins.site_settings import site_settings
import os
import pickle

class LocalSettings(Loggable):
    log_domain = "conf"

    def __init__(self):
        self._local_settings = {}
        self.local_settings_path = os.path.join(site_settings['HIGGINS_DIR'], "settings.dat")
        # check for the existence of a local settings file
        if os.access(self.local_settings_path, os.F_OK):
            # load the local settings
            try:
                f = open(self.local_settings_path, 'r')
                self._local_settings = pickle.load(f)
                f.close()
            except EOFError, e:
                # ignore empty file error
                pass
            except Exception, e:
                self.log_error("failed to load local settings from '%s': %s" % (self.local_settings_path,e))
                raise e
        if 'SECRET_KEY' not in self._local_settings:
            # generate a secret key
            from random import choice
            validchars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            secret_key = ''.join([choice(validchars) for i in range(50)])
            self._local_settings = {'SECRET_KEY': secret_key}
            self.log_debug("generated a new secret key")
        # load the local settings into the site_settings dict
        for name,value in self._local_settings.items():
            site_settings[name] = value
        # load the site_settings into the django_settings object
        django_settings.configure(**site_settings)
        self._doFlush()
        self.log_debug("loaded settings from '%s'" % self.local_settings_path)

    def __getitem__(self, name):
        try:
            return self._local_settings[name]
        except:
            pass
        return django_settings.__getattr__(name)

    def __setitem__(self, name, value):
        self._local_settings[name] = value

    def __iter__(self):
        print "called __iter__"
        class LocalSettingsIter:
            def __init__(self, settings):
                print "localsettingsiter __init__"
                self.keys = settings.keys()
            def __iter__(self):
                print "localsettingsiter __iter__"
                return self
            def next(self):
                print "localsettingsiter next"
                if self.keys == []:
                    raise StopIteration()
                return self.keys.pop(0)
        copy = django_settings.copy()
        copy.update(self._local_settings)
        return LocalSettingsIter(copy)

    def __contains__(self, name):
        if name in self._local_settings:
            return True
        try:
            django_settings.__getattr__(name)
            return True
        except:
            return False

    def _doFlush(self):
        f = open(self.local_settings_path, 'w')
        pickle.dump(self._local_settings, f, 0)
        f.close()

    def get(self, name, default=None):
        """
        Returns the value of the named setting.  If there is no such setting,
        then the default value is returned.
        """
        try:
            return self._local_settings[name]
        except:
            pass
        try:
            return django_settings.__getattr__(name)
        except:
            pass
        return default

    def set(self, **settings):
        """Saves one or more settings."""
        for key,value in settings.items():
            self._local_settings[key] = value

    def flush(self):
        """Flushes settings to disk."""
        self._doFlush()
        self.log_debug("flushed settings changes")

conf = LocalSettings()
