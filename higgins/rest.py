# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os, simplejson
from higgins.http.http_headers import MimeType
from higgins.http.http import Response

# API Error codes
class Error(object):
    NONE = 0
    INTERNAL_SERVER_ERROR = 1
    INVALID_INPUT = 2
    _errors = [
        "No Error",
        "Internal Server Error",
        "Validation Error"
        ]
    @classmethod
    def getString(cls, errno):
        try:
            return cls._errors[errno]
        except:
            return 'Unknown error'

class RestResponse(Response):
    def __init__(self, data={}, type='json'):
        headers = {}
        if type == 'json':
            data['status'] = Error.NONE
            headers['content-type'] = MimeType.fromString('application/json')
            stream = simplejson.dumps(data)
        else:
            raise Exception('Unknown response format %s' % type)
        Response.__init__(self, 200, headers, stream)

class RestError(Response):
    def __init__(self, status, extra=None, type='json'):
        headers = {}
        if type == 'json':
            data = { 'status': status, 'error': Error.getString(status) }
            if extra:
                data['extra'] = extra
            headers['content-type'] = MimeType.fromString('application/json')
            stream = simplejson.dumps(data)
        else:
            raise Exception('Unknown response format %s' % type)
        Response.__init__(self, 200, headers, stream)

class RestInternalServerError(RestError):
    def __init__(self, extra=None, type='json'):
        RestError.__init__(self, Error.INTERNAL_SERVER_ERROR, extra, type)

class RestInvalidInputError(RestError):
    def __init__(self, extra=None, type='json'):
        RestError.__init__(self, Error.INVALID_INPUT, extra, type)
