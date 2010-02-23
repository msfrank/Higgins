# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import simplejson
from pkg_resources import resource_string
from higgins.entrypoint import Service
from higgins.http.routes import Dispatcher
from higgins.http.http import Response
from higgins.db import db, Artist
from higgins.plugins.ria.lookup import TemplateLookup
from higgins.plugins.ria.logger import logger

class AjaxMethods(Dispatcher):
    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute("getArtists", self.getArtists)
    def getArtists(self, request):
        # check for required params before updating anything in the database
        start = int(request.post.get('start', [0])[0])
        limit = int(request.post.get('limit', [25])[0])
        response = {}
        artists = []
        for artist in db.query(Artist, offset=start, limit=limit, sort=Artist.name.ascending):
            artists.append({'name':artist.name, 'id':artist.storeID})
        response['artists'] = artists
        response['total'] = db.count(Artist)
        return Response(200, stream=simplejson.dumps(response))

class RiaService(Service):
    pretty_name = "RIA"
    description = "Fancy web interface"

    def initService(self, core):
        self.core = core
        self.templates = TemplateLookup('higgins.plugins.ria')

    def startService(self):
        logger.log_debug("started RIA service")
        self.core.root.addRoute('/ria/ajax/', AjaxMethods())
        self.core.root.addRoute('/ria(/static/.*)', self.getStatic)
        self.core.root.addRoute('/ria/?$', self.getFrontpage)
        self.core.root.addRoute('/ria/library/?$', self.getLibrary)
        self.core.root.addRoute('/ria/library/music/?$', self.getMusic)

    def stopService(self):
        logger.log_debug("stopped RIA service")

    def getStatic(self, request, path):
        try:
            path = [part for part in path.split('/') if not part=='..']
            path = '/' + '/'.join(path)
            data = resource_string('higgins.plugins.ria', path)
            return Response(200, headers=None, stream=data)
        except IOError, e:
            return Response(404)
        except Exception, e:
            logger.log_error("failed to get static resource: %s" % str(e))
            return Response(500)

    def getSections(self):
        return (
            ('/ria/', 'Home', False),
            ('/ria/library/', 'Library', False),
            )

    def getFrontpage(self, request):
        t = self.templates.get_template('/templates/front.html')
        return Response(200, headers=None, stream=t.render(ria=self))

    def getLibrary(self, request):
        t = self.templates.get_template('/templates/library-front.html')
        return Response(200, headers=None, stream=t.render(ria=self))

    def getMusic(self, request):
        t = self.templates.get_template('/templates/library-music.html')
        return Response(200, headers=None, stream=t.render(ria=self))
