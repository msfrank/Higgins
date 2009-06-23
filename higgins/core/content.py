# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.python import filepath
from higgins.db import Song
from higgins.http.stream import FileStream
from higgins.http.http_headers import MimeType
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.core.logger import logger

class ContentResource(Resource):

    def allowedMethods(self):
        return ("GET",)

    def locateChild(self, request, segments):
        try:
            if len(segments) != 1:
                return None, []
            request.songid = int(segments[0])
            return self, []
        except:
            return None, []

    def render(self, request):
        try:
            song = Song.objects.filter(id=request.songid)[0]
            f = open(song.file.path, 'rb')
            mimetype = str(song.file.mimetype)
            logger.log_debug("%s -> %s (%s)" % (request.path, song.file.path, mimetype))
            mimetype = MimeType.fromString(mimetype)
            return Response(200, {'content-type': mimetype}, FileStream(f))
        except IndexError:
            return Response(404) 
        except:
            return Response(500)
