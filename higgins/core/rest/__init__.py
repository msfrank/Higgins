# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os, simplejson
from higgins.core.logger import logger
from higgins.http.http_headers import MimeType
from higgins.http.http import Response

# API Error codes
NO_ERROR = 0
ERROR_INTERNAL_SERVER_ERROR = 1
ERROR_INVALID_INPUT = 2

# API Error reasons
_APIErrors = [
    "No Error",
    "Internal Server Error",
    "Validation Error"
    ]

class RestResponse(Response):
    def __init__(self, data={}, type='json'):
        headers = {}
        if type == 'json':
            data['status'] = NO_ERROR
            headers['content-type'] = MimeType.fromString('application/json')
            stream = simplejson.dumps(data)
        else:
            raise Exception('Unknown response format %s' % type)
        Response.__init__(self, 200, headers, stream)

class RestError(Response):
    def __init__(self, status, extra=None, type='json'):
        headers = {}
        if type == 'json':
            data = { 'status': status, 'error': _APIErrors[status] }
            if extra:
                data['extra'] = extra
            headers['content-type'] = MimeType.fromString('application/json')
            stream = simplejson.dumps(data)
        else:
            raise Exception('Unknown response format %s' % type)
        Response.__init__(self, 200, headers, stream)

class RestInternalServerError(RestError):
    def __init__(self, extra=None, type='json'):
        RestError.__init__(self, ERROR_INTERNAL_SERVER_ERROR, extra, type)

class RestInvalidInputError(RestError):
    def __init__(self, extra=None, type='json'):
        RestError.__init__(self, ERROR_INVALID_INPUT, extra, type)
