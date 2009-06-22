# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.url_dispatcher import UrlDispatcher
from higgins.data import renderTemplate
from higgins.conf import conf
from higgins.core.logger import logger

class SettingsResource(UrlDispatcher):
    def __init__(self, core):
        self.core = core
        self.addRoute('/$', self.showSettings)
        self.addRoute('/plugins$', self.showPlugins)
        self.addRoute('/plugins/(\s+)$', self.configurePlugin)
        self.addRoute('/(\s+)$', self.configureSettings)

    def showSettings(request):
        return renderTemplate('templates/settings-front.t', {})

    def showPlugins(request):
        return renderTemplate('templates/settings-plugins.t', {})

    def configureSettings(request, name):
        return renderTemplate('templates/settings-plugin.t', {})

    def configurePlugin(request, name):
        return renderTemplate('templates/settings-plugin.t', {})
