# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django import forms
from django.http import QueryDict
from higgins.conf import conf
from higgins.core.logger import logger

class ConfiguratorException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return str(self.reason)

class ConfiguratorDeclarativeParser(type):
    # The metaclass does the magic of parsing the Configurator subclass
    # and building a configuration form from the supplied settings.

    def __new__(cls, name, bases, attrs):
        # Returns the generated Configurator subclass.
        attrs['_config_name'] = name
        config_fields = {}
        for key,object in attrs.items():
            if isinstance(object, forms.Field):
                config_fields[key] = object
                del attrs[key]
        attrs['_config_fields'] = config_fields
        config_cls = type(name + "Form", (forms.Form,), config_fields.copy())
        attrs['_config_cls'] = config_cls
        new_class = super(ConfiguratorDeclarativeParser,cls).__new__(cls, name, bases, attrs)
        # For each field, set the default value if it hasn't already been set.
        initial = config_cls({})
        for key,field in initial.fields.items():
            full_key = 'CFG__' + name + '__' + key
            if not full_key in conf:
                try:
                    conf[full_key] = field.clean(field.default)
                    logger.log_debug("set initial value for %s.%s to '%s'" % (name, key, field.default))
                except forms.ValidationError:
                    e = ConfiguratorException("'%s' is not a valid value for %s.%s" % (field.default, name, key))
                    logger.log_warning("failed to set initial value: %s" % e)
                    raise e
        return new_class

    def __getattr__(cls, name):
        # if 'name' is a setting, then return the setting value from the
        # configuration store.  otherwise, return an AttributeError exception.
        # Note that this method will only be called if 'name' *doesn't* exist
        # as a class attribute.
        if name in cls._config_fields:
            return conf['CFG__' + cls._config_name + '__' + name]
        raise AttributeError("Configurator is missing config field %s" % name)

    def __setattr__(cls, name, value):
        # if 'name' is a setting, then set its value in the configuration
        # store.  Otherwise try to set the class attribute to 'value'.
        try:
            field = cls._config_fields[name]
            conf['CFG__' + cls._config_name + '__' + name] = field.clean(value)
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

    def __call__(self, settings=None):
        # Return an instance of the Configurator form.
        current = QueryDict('').copy()
        for key in self._config_fields.keys():
            current[key] = conf['CFG__' + self._config_name + '__' + key]
        if settings:
            for key,value in settings.items():
                current[key] = value
        config = self._config_cls(current)
        if settings and config.is_valid():
            for key in config.fields.keys():
                value = config.cleaned_data[key]
                full_key = 'CFG__' + self._config_name + '__' + key
                if conf[full_key] != value:
                    logger.log_debug("%s: %s => %s" % (self._config_name, key, value))
                    conf[full_key] = value
        return config

class IntegerSetting(forms.IntegerField):
    """An integer setting."""

    def __init__(self, label, default, **kwds):
        if not 'initial' in kwds:
            kwds['initial'] = default
        forms.IntegerField.__init__(self, kwds)
        self.label = label
        self.default = default

class StringSetting(forms.CharField):
    """A string setting."""

    def __init__(self, label, default, **kwds):
        if not 'initial' in kwds:
            kwds['initial'] = default
        forms.CharField.__init__(self, kwds)
        self.label = label
        self.default = default
