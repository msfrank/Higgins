# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.http import Response
from higgins.http.responsecode import RESPONSES
from higgins.data import templates

class ErrorResponse(Response):
    def __init__(self, code, description, headers=None):
        Response.__init__(self, code, headers=headers,
            stream=templates.render('templates/error.html', {
                    'topnav': [('Home', '/', False), ('Library', '/library', False),],
                    'errorname': RESPONSES[code],
                    'description': description
                    }
                )
            )
