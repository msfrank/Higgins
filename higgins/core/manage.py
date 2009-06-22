# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.url_dispatcher import UrlDispatcher
from higgins.http.http_headers import MimeType
from higgins.http.http import Response
from higgins.core.logger import logger

class ManageResource(UrlDispatcher):
    def allowedMethods(self):
        return ('POST')

    def __init__(self):
        self.addRoute('/playlist', self.manage_playlists)
        self.addRoute('/playlist/(\d+)$', self.manage_playlist_item)

    def manage_playlists(request):
        logger.log_debug("manage_playlists: POST=%s" % request.POST)
        return HttpResponse('')

    def manage_playlist_item(request, playlist_id):
        logger.log_debug("manage_playlist_item (%i): POST=%s" % (playlist_id, request.POST))
        return HttpResponse('')
