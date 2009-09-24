# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.python import filepath
from axiom.errors import ItemNotFound
from higgins.db import db, File
from higgins.http.stream import FileStream as TwistedFileStream
from higgins.http.http_headers import MimeType
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.gst.transcode import TranscodingStream
from higgins.core.dispatcher import Dispatcher
from higgins.core.logger import logger

class FileStream(TwistedFileStream):
    def __init__(self, file):
        self.length = file.size
        self.mimetype = MimeType.fromString(str(file.MIMEType))
        f = open(str(file.path), 'rb')
        TwistedFileStream.__init__(self, f)

class ContentResource(Dispatcher):
    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('(\d+)$', self.renderContent, allowedMethods=('GET'))

    def renderContent(self, request, fileID):
        try:
            fileID = int(fileID)
            file = db.get(File, File.storeID==fileID)
            logger.log_debug("file=%s" % str(file))
            if 'mimetype' in request.args:
                mimetype = request.args['mimetype'][0]
                logger.log_debug("streaming %s as %s" % (file.path, mimetype))
                stream = TranscodingStream(file, mimetype)
            else:
                logger.log_debug("streaming %s" % file.path)
                stream = FileStream(file)
            return Response(200, {'content-type': stream.mimetype}, stream)
        except ItemNotFound, e:
            return Response(404)
        except Exception, e:
            logger.log_error("failed to stream fileID %s: %s" % (str(fileID), str(e)))
            return Response(500)
