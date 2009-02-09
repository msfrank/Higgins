from django import forms
from higgins.core.logger import logger

class ConfiguratorDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        attrs['_config_name'] = name
        config_attrs = {}
        for name,object in attrs.items():
            if isinstance(object, forms.Field):
                config_attrs[name] = object
        attrs['_config_attrs'] = config_attrs
        return super(ConfiguratorDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class Configurator:
    __metaclass__ = ConfiguratorDeclarativeParser
    pretty_name = None
    description = None

    def __init__(self):
        self._config_cls = type(self._config_name + "Form", (forms.Form,), self._config_attrs)
        initial = self._config_cls({})
        for name,field in initial.fields.items():
            logger.log_debug("configurator %s: initial value for %s=%s" % (self._config_name,name,field.default))

    def __call__(self, settings):
        return self._config_cls(settings)

class IntegerSetting(forms.IntegerField):
    def __init__(self, label, default, **kwds):
        if not 'initial' in kwds:
            kwds['initial'] = default
        forms.IntegerField.__init__(self, kwds)
        self.label = label
        self.default = default

class StringSetting(forms.CharField):
    def __init__(self, label, default, **kwds):
        if not 'initial' in kwds:
            kwds['initial'] = default
        forms.CharField.__init__(self, kwds)
        self.label = label
        self.default = default
