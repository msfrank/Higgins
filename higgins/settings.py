# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
from ConfigParser import ConfigParser
from higgins.platform import netif
from higgins.logger import Loggable

class SettingsLogger(Loggable):
    log_domain = 'settings'
logger = SettingsLogger()

class ConfigurationError(Exception):
    pass

class KeyStore(object):
    def __init__(self):
        self.settingsPath = None
        self._settings = None
        self._isLoaded = False

    def load(self, path):
        if self._isLoaded:
            raise ConfigurationError("settings have already been loaded")
        self._isLoaded = True
        self.settingsPath = path
        # check for the existence of a local settings file
        if os.access(self.settingsPath, os.F_OK):
            # load the local settings
            try:
                f = open(self.settingsPath, 'r')
                self._settings = ConfigParser()
                self._settings.readfp(f, self.settingsPath)
                f.close()
            except EOFError, e:
                # ignore empty file error
                pass
            except Exception, e:
                logger.log_error("failed to load settings from %s: %s" % (self.settingsPath,e))
                raise e
        logger.log_debug("loaded settings from %s" % self.settingsPath)

    def contains(self, section, option):
        return self._settings.has_option(section, option)

    def get(self, section, option):
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        return self._settings.get(section, option)

    def set(self, section, name, value):
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        self._settings.set(section, option, value)

    def flush(self):
        """
        Flushes settings to disk.
        """
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        logger.log_debug("flushed settings changes")

settings = KeyStore()

class Setting(object):
    """
    Base Setting object which contains common attributes for all settings.
    """
    def __init__(self, name, default):
        self.name = name
        self.default = default
    def parse(self, value):
        raise Exception('no parse() function for setting %s' % self.name)
    def write(self, value):
        raise Exception('no write() function for setting %s' % self.name)

class IntegerSetting(Setting):
    """
    An integer setting.
    """
    def __init__(self, name, default=None, **kwds):
        Setting.__init__(self, name, default)
        self.min = None
        self.max = None
        if 'min' in kwds:
            self.min = self.validate(kwds['min'])
        if 'max' in kwds:
            self.max = self.validate(kwds['max'])
        if self.min and self.max and self.min > self.max:
            raise Exception('minimum value is greater than maximum value')

    def validate(self, value):
        if not isinstance(value, int):
            raise Exception('value is not an integer')
        if self.min and value < self.min:
            raise Exception('value is smaller than minimum')
        if self.max and value > self.max:
            raise Exception('value is greater than maximum')
        return value

    def parse(self, value):
        return self.validate(int(value))

    def write(self, value):
        return str(self.validate(value))

class StringSetting(Setting):
    """
    A string setting.
    """
    def __init__(self, name, default=None, **kwds):
        Setting.__init__(self, name, default)

    def validate(self, value):
        if not isinstance(value, str):
            raise Exception('value is not a string')
        return value

    def parse(self, value):
        return self.validate(str(value))

    def write(self, value):
        return str(self.validate(value))

class NetworkInterfaceSetting(Setting):
    """
    A network interface setting.
    """
    def __init__(self, name, default=None, allowLocalhost=False, **kwds):
        Setting.__init__(self, name, default)
        self.addresses = {'All Interfaces': '0.0.0.0' }
        for name,iface in netif.list_interfaces().items():
            logger.log_debug("netif: name=%s, iface=%s" % (name,iface))
            self.addresses[name] = iface.address

    def validate(self, value):
        if not isinstance(value, str):
            raise Exception('value is not a string')
        if not value in self.addresses.values():
            raise Exception('%s is not a valid interface' % value)
        return value

    def parse(self, value):
        return self.validate(str(value))

    def write(self, value):
        return str(self.validate(value))

class ConfigurableDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        options = {}
        for key,obj in attrs.items():
            if isinstance(obj, Setting):
                options[key] = obj
                del attrs[key]
        attrs['__options__'] = options
        return type.__new__(cls, name, bases, attrs)

class Configurable(object):
    __metaclass__ = ConfigurableDeclarativeParser

    def __init__(self, name):
        self.__section__ = name
        for key,obj in getattr(self, '__options__').items():
            if settings.contains(name, key):
                try:
                    opt.parse(settings.get(name, key))
                except Exception, e:
                    raise ConfigurationError("failed to parse %s/%s: %s" % (name, key, str(e)))
            elif obj.default == None:
                raise ConfigurationError("missing required setting %s/%s" % (name, key))

    def __getattr__(self, name):
        try:
            section = getattr(self, '__section__')
            options = getattr(self, '__options__')
            opt = options[name]
            if settings.contains(section, opt.name):
                return opt.parse(settings.get(section, opt.name))
            return opt.default
        except Exception, e:
            raise AttributeError("failed to get %s" % name)

    def __setattr__(self, name, value):
        if not name in self.__options__:
            object.__setattr__(self, name, value)
        else:
            try:
                opt = self.__options__[name]
                settings.set(self.__section__, opt.name, opt.write(value))
            except Exception, e:
                logger.log_warning("failed to set %s/%s: %s" % (self.__section__, opt.name, str(e)))
