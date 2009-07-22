# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from genshi.input import HTML
from higgins.http.url_dispatcher import UrlDispatcher
from higgins.http.http import Response
from higgins.data import templates
from higgins.core.config import CoreHttpConfig
from higgins.settings import settings, IntegerSetting, StringSetting, NetworkInterfaceSetting
from higgins.core.errorresponse import ErrorResponse
from higgins.core.logger import logger

class SettingsResource(UrlDispatcher):
    def __init__(self, core):
        UrlDispatcher.__init__(self)
        self.core = core
        self.addRoute('/?$', self.showSettings)
        self.addRoute('/general/?$', self.configureGeneralSettings)
        self.addRoute('/http/?$', self.configureHttpSettings)
        self.addRoute('/plugins/?$', self.configurePlugins)
        self.addRoute('/plugins/(\s+)/?$', self.configurePluginSettings)

    def showSettings(self, request):
        from higgins.core.service import CoreHttpConfig
        return Response(200,
            stream=templates.render('templates/settings-front.html', {
                    'topnav': [('Home', '/', False), ('Library', '/library', False),],
                    'subnav': [
                        ('General', '/settings/general', False),
                        (CoreHttpConfig.pretty_name, '/settings/http', False),
                        ('Plugins', '/settings/plugins', False),
                        ]
                    }
                )
            )

    def configureGeneralSettings(self, request):
        return ErrorResponse(404, "resource not found")

    def configureHttpSettings(self, request):
        form = None
        try:
            if request.method == 'POST':
                form = SettingsForm(CoreHttpConfig, request.post)
            else:
                form = SettingsForm(CoreHttpConfig)
        except Exception, e:
            logger.log_error("configureHttpSettings: %s" % e)
        return Response(200,
            stream=templates.render('templates/settings-configure.html', {
                    'topnav': [('Home', '/', False), ('Library', '/library', False),],
                    'subnav': [
                        ('General', '/settings/general', False),
                        (CoreHttpConfig.pretty_name, '/settings/http', False),
                        ('Plugins', '/settings/plugins', False),
                        ],
                    'form': form,
                    'configurator': CoreHttpConfig
                    }
                )
            )

    def configurePlugins(self, request):
        if request.method == 'POST':
            for name,plugin in self.core._plugins.items():
                if name in request.post and not self.core.pluginIsEnabled(name):
                    self.core.enablePlugin(name)
                if not name in request.post and self.core.pluginIsEnabled(name):
                    self.core.disablePlugin(name)
            return Response(200,
                stream=templates.render('templates/settings-plugins.html', {
                        'topnav': [('Home', '/', False), ('Library', '/library', False),],
                        'subnav': [
                            ('General', '/settings/general', False),
                            (CoreHttpConfig.pretty_name, '/settings/http', False),
                            ('Plugins', '/settings/plugins', True),
                            ],
                        'plugins': self.core._plugins.values()
                        }
                    )
                )
        logger.log_debug("discovered plugins: %s" % self.core._plugins.items())
        return Response(200,
            stream=templates.render('templates/settings-plugins.html', {
                    'topnav': [('Home', '/', False), ('Library', '/library', False),],
                    'subnav': [
                        ('General', '/settings/general', False),
                        (CoreHttpConfig.pretty_name, '/settings/http', False),
                        ('Plugins', '/settings/plugins', True),
                        ],
                    'plugins': self.core._plugins.values()
                    }
                )
            )

    def configurePluginSettings(self, request, name):
        return ErrorResponse(404, "resource not found")

class FormField(object):
    def __init__(self, field, name, text):
        self.field = field
        self.name = name
        self.text = text
        self.value = text
        self.error = None
        try:
            self.value = self._validate(text)
        except Exception, e:
            self.error = str(e)
    def _validate(self, text):
        raise Exception('_validate method not defined')

class IntegerFormField(FormField):
    def _validate(self, text):
        return self.field.validate(int(text))
    def __str__(self):
        return """    
            <input class="higgins-settings-field" type="text" name="%s" value="%s"/>
            """ % (self.name, self.text)

class StringFormField(FormField):
    def _validate(self, text):
        return self.field.validate(str(text))
    def __str__(self):
        return """    
            <input class="higgins-settings-field" type="text" name="%s" value="%s"/>
            """ % (self.name, self.text)

class NetworkInterfaceFormField(FormField):
    def _validate(self, text):
        return self.field.validate(str(text))
    def __str__(self):
        html =  '<select class="higgins-settings-field" name="%s">\n' % self.name
        for name,addr in self.field.addresses.items():
            if addr == self.text:
                html += '<option selected="true" value="%s">%s (%s)</option>\n' % (addr, name, addr)
            else:
                html += '<option value="%s">%s (%s)</option>\n' % (addr, name, addr)
        html += "</select>\n"
        return html

class SettingsForm(object):

    def __init__(self, configurator, values={}):
        def newFormField(field, name, text):
            if isinstance(field, IntegerSetting):
                return IntegerFormField(field, name, text)
            if isinstance(field, StringSetting):
                return StringFormField(field, name, text)
            if isinstance(field, NetworkInterfaceSetting):
                return NetworkInterfaceFormField(field, name, text)
            raise Exception('Can\'t create FormField out of type %s' % str(type(field)))

        self.name = configurator._config_name
        self._configurator = configurator
        self._html = """
            <form method="post" action="" class="higgins-settings-form">
                <table class="higgins-settings-table">
            """
        for name,field in configurator._config_fields.items():
            formfield = None
            if not name in values:
                formfield = newFormField(field, name, str(getattr(configurator, name)))
            else:
                formfield = newFormField(field, name, values[name][0])
            self._html += '<tr><td><span class="higgins-settings-field-name">%s</span></td>' % field.label
            self._html += "<td>%s" % str(formfield)
            if formfield.error:
                self._html += '<br/><span class="higgins-settings-field-error">%s</span>' % formfield.error
            else:
                setattr(configurator, name, formfield.value)
            self._html += "</td></tr>\n"
        self._html += """
                </table>
                <input class="higgins-settings-submit" type="submit" value="Save Settings"/>
            </form>
            """

    def toHTML(self):
        return HTML(self._html)
