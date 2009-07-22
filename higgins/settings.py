# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
import pickle
from higgins.platform import netif
from higgins.logger import Loggable

class SettingsLogger(Loggable):
    log_domain = 'settings'
logger = SettingsLogger()

class KeyStore(object):
    log_domain = "conf"

    def __init__(self):
        self._settings = {}
        self._isLoaded = False
        self.settingsPath = None

    def load(self, path):
        if self._isLoaded:
            raise Exception("settings have already been loaded")
        self._isLoaded = True
        self.settingsPath = path
        # check for the existence of a local settings file
        if os.access(self.settingsPath, os.F_OK):
            # load the local settings
            try:
                f = open(self.settingsPath, 'r')
                self._settings = pickle.load(f)
                f.close()
            except EOFError, e:
                # ignore empty file error
                pass
            except Exception, e:
                logger.log_error("failed to load settings from %s: %s" % (self.settingsPath,e))
                raise e
        # flush the initial settings
        #self._doFlush()
        logger.log_debug("loaded settings from %s" % self.settingsPath)

    def __getitem__(self, name):
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        try:
            return self._settings[name]
        except:
            raise Exception('Setting %s not found' % name)

    def __setitem__(self, name, value):
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        self._settings[name] = value

    def __iter__(self):
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        class _SettingsIter:
            def __init__(self, settings):
                self.keys = settings.keys()
            def __iter__(self):
                return self
            def next(self):
                if self.keys == []:
                    raise StopIteration()
                return self.keys.pop(0)
        return _SettingsIter(self._settings)

    def __contains__(self, name):
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        if name in self._settings:
            return True
        return False

    def _doFlush(self):
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        f = open(self.settingsPath, 'w')
        pickle.dump(self._settings, f, 0)
        f.close()

    def get(self, name, default=None):
        """
        Returns the value of the named setting.  If there is no such setting,
        then the default value is returned.
        """
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        try:
            return self._settings[name]
        except:
            pass
        return default

    def set(self, **settings):
        """Saves one or more settings."""
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        for key,value in settings.items():
            self._settings[key] = value

    def flush(self):
        """Flushes settings to disk."""
        if not self._isLoaded:
            raise Exception("settings have not been loaded")
        self._doFlush()
        logger.log_debug("flushed settings changes")

class Setting(object):
    """Base Setting object which contains common attributes for all settings."""

    def __init__(self, label, default, tooltip):
        self.label = label
        self.default = default
        self.tooltip = tooltip

    def validate(self, value):
        raise Exception('no validator function for this setting')

class IntegerSetting(Setting):
    """An integer setting."""

    def __init__(self, label, default, tooltip, **kwds):
        Setting.__init__(self, label, default, tooltip)
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

class StringSetting(Setting):
    """A string setting."""

    def __init__(self, label, default, tooltip, **kwds):
        Setting.__init__(self, label, default, tooltip)

    def validate(self, value):
        if not isinstance(value, str):
            raise Exception('value is not a string')
        return value

class NetworkInterfaceSetting(Setting):
    def __init__(self, label, default, tooltip, allowLocalhost=False, **kwds):
        Setting.__init__(self, label, default, tooltip)
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

class ConfiguratorException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return str(self.reason)

class ConfiguratorDeclarativeParser(type):
    """
    The metaclass does the magic of parsing the Configurator subclass
    and building a configuration form from the supplied settings.
    """

    def __new__(cls, name, bases, attrs):
        """Returns the generated Configurator subclass."""
        attrs['_config_name'] = name
        config_fields = {}
        for key, object in attrs.items():
            if isinstance(object, Setting):
                config_fields[key] = object
                del attrs[key]
                # For each field, set the default value if it hasn't already been set.
                full_key = 'CFG__' + name + '__' + key
                if not full_key in settings:
                    try:
                        settings[full_key] = object.default
                        logger.log_debug("set initial value for %s.%s to '%s'" % (name, key, object.default))
                    except Exception, e:
                        logger.log_warning("failed to set initial value: %s" % e)
        attrs['_config_fields'] = config_fields
        return super(ConfiguratorDeclarativeParser,cls).__new__(cls, name, bases, attrs)

    def __getattr__(cls, name):
        """
        if 'name' is a setting, then return the setting value from the
        configuration store.  otherwise, return an AttributeError exception.
        Note that this method will only be called if 'name' *doesn't* exist
        as a class attribute.
        """
        if name in cls._config_fields:
            value = settings['CFG__' + cls._config_name + '__' + name]
            #logger.log_debug("%s: %s == %s" % (cls._config_name, name, value))
            return value
        raise AttributeError("Configurator is missing config field %s" % name)

    def __setattr__(cls, name, value):
        """
        if 'name' is a setting, then set its value in the configuration
        store.  Otherwise try to set the class attribute to 'value'.
        """
        try:
            field = cls._config_fields[name]
            settings['CFG__' + cls._config_name + '__' + name] = field.validate(value)
            logger.log_debug("%s: %s => %s" % (cls._config_name, name, value))
        except:
            type.__setattr__(cls, name, value)

class Configurator(object):
    """
    Holds one or more configuration settings, and provides a method for
    getting and setting these settings.
    """
    __metaclass__ = ConfiguratorDeclarativeParser
    pretty_name = None
    description = None


settings = KeyStore()

__all__ = ['settings', 'Configurator', 'IntegerSetting', 'StringSetting']
