# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from axiom.errors import ItemNotFound
from higgins.http.routes import Dispatcher
from higgins.http.http_headers import MimeType
from higgins.http.http import Response
from higgins.http.stream import FileStream
from higgins.db import db, File
from higgins.gst.transcode import TranscodingStream, ProfileNotFound
from higgins.logger import Loggable

class ContentMethods(Dispatcher, Loggable):
    log_domain = "core"

    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('(\d+)\.?.*$', self.renderContent, allowedMethods=('GET'))

    def renderContent(self, request, fileID):
        try:
            # look up the fileID
            fileID = int(fileID)
            file = db.get(File, File.storeID==fileID)
            self.log_debug("file=%s" % str(file))
            # if mimetype is part of the request, then set up a transcoding stream
            if 'mimetype' in request.args:
                mimetype = request.args['mimetype'][0]
                self.log_debug("streaming %s as %s" % (file.path, mimetype))
                stream = TranscodingStream(file, mimetype)
                return Response(200, {'content-type': stream.mimetype}, stream)
            # otherwise set up a normal file stream
            self.log_debug("streaming %s" % file.path)
            mimetype = MimeType.fromString(str(file.MIMEType))
            f = open(str(file.path), 'rb')
            stream = FileStream(f)
            stream.length = file.size
            return Response(200, {'content-type': mimetype}, stream)
        except ItemNotFound, e:
            self.log_debug("failed to stream fileID %s: no such item" % str(fileID))
            return Response(404)
        except ProfileNotFound, e:
            self.log_debug("failed to stream fileID %s: %s" % (str(fileID), str(e)))
            return Response(400)
        except Exception, e:
            self.log_error("failed to stream fileID %s: %s" % (str(fileID), str(e)))
            return Response(500)
