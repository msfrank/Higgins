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
from higgins.settings import settings, IntegerSetting, StringSetting
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
        try:
            if request.method == 'POST':
                form = SettingsForm(CoreHttpConfig, request.post)
            else:
                form = SettingsForm(CoreHttpConfig)
        except Exception, e:
            logger.log_debug("configureHttpSettings: %s" % e)
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

class SettingsForm(object):
    def _getSettingString(self, name):
        type = self._configurator._config_fields[name]
        value = getattr(self._configurator, name)
        if isinstance(type, IntegerSetting):
            return str(value)
        if isinstance(type, StringSetting):
            return str(value)
        logger.log_debug("unknown type for setting %s" % name)
        return None

    def _updateSetting(self, name, value):
        try:
            field = self._configurator._config_fields[name]
            if isinstance(field, IntegerSetting):
                value = field.validate(int(value))
            if isinstance(field, StringSetting):
                value = field.validate(value)
            setattr(self._configurator, name, value)
            return value
        except Exception, e:
            logger.log_error("failure: %s" % e)
            raise e

    def __init__(self, configurator, values=None):
        self.name = configurator._config_name
        self._configurator = configurator
        self._html = """
            <form method="post" action="" enctype="multipart/form-data" class="higgins-settings-form" id="higgins-settings-form_%s">
                <div class="higgins-settings-description">%s</div>
                <table class="higgins-settings-table">
            """ % (configurator.pretty_name, configurator.description)
        for name,field in configurator._config_fields.items():
            value = ''
            error = ''
            try:
                # pull the value of the setting from the configurator
                if values == None:
                    value = self._getSettingString(name)
                # validate the input, convert it to the correct type, and update the configurator
                else:
                    value = self._updateSetting(name, values[name])
            except Exception, e:
                error = "<div>Error: %s</div>" % str(e)
            self._html += """
                    <tr>
                        <td><span class="higgins-settings-field-name">%s</span></td>
                        <td><input class="higgins-settings-field" type="text" name="%s" value="%s"/>%s</td>
                    </tr>
                """ % (field.label, name, value, error)
        self._html += """
                </table>
                <input class="higgins-settings-submit" type="submit" value="Save Settings"/>
            </form>
            """

    def toHTML(self):
        return HTML(self._html)
