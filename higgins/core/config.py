# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.settings import settings, Configurator, IntegerSetting

class CoreHttpConfig(Configurator):
    pretty_name = "HTTP Server"
    description = "Configure the built-in HTTP Server"
    HTTP_PORT = IntegerSetting("Listening Port", 8000, '', min=0, max=65535)
