# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.
#
# Portions of this script (the multipart form uploading) come from:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306

import simplejson, random, string
from os.path import basename
from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred, waitForDeferred, deferredGenerator
from higgins.http.stream import MemoryStream, FileStream, CompoundStream
from higgins.http.http_headers import MimeType
from higgins.http.client.http import HTTPClientProtocol, ClientRequest
from higgins.gst.metadata import MetadataFinder
from higgins.logger import Loggable
from higgins import VERSION

class UploaderLogger(Loggable):
    domain = 'uploader'
logger = UploaderLogger()

class UploaderException(Exception):
    pass

class Uploader(object):

    def __init__(self, paths, host='localhost', port=8000, isLocal=False):
        self._deferred = None
        self.boundary = ''.join(map(lambda x: random.choice(string.letters+string.digits), xrange(50)))
        self.paths = paths
        self.host = host
        logger.log_debug("host: %s" % host)
        self.port = port
        logger.log_debug("port: %i" % port)
        self.isLocal = isLocal
        logger.log_debug("local-mode: %s" % str(isLocal))

    def _makePostStream(self, filePath, metadata):
        # create the multipart body
        lines = []
        if self.isLocal:
            metadata['file'] = filePath
        # add each metadata part
        for name,value in metadata.items():
            lines.append('--' + self.boundary)
            lines.append('Content-Disposition: form-data; name="%s"' % name)
            lines.append('')
            lines.append(str(value))
        if not self.isLocal:
            # if not local mode, then add the headers for the file part
            lines.append('--' + self.boundary)
            lines.append('Content-Disposition: form-data; name="file"; filename="%s"' % basename(filePath))
            lines.append('Content-Type: %s' % metadata['mimetype'])
            lines.append('')
            #lines.append('')
        # create the stream which is sent to the server 
        stream = MemoryStream('\r\n'.join(lines))
        if not self.isLocal:
            stream = CompoundStream((stream, FileStream(open(filePath, 'rb'))))
        return stream

    def _processFile(self):
        for path in self.paths:
            # parse metadata
            finder = MetadataFinder(path)
            metadata = waitForDeferred(finder.parseMetadata())
            yield metadata
            metadata = metadata.getResult()
            for name,value in metadata.items():
                logger.log_debug("parsed metadata: %s = '%s'" % (name,value))
            # connect to server
            proto = protocol.ClientCreator(reactor, HTTPClientProtocol)
            server = waitForDeferred(proto.connectTCP(self.host, int(self.port)))
            yield server
            server = server.getResult()
            logger.log_debug("connected to %s:%i" % (self.host, self.port))
            # upload the file
            request = ClientRequest('POST',
                                    '/api/1.0/song/add', {
                                        'host': '%s:%i' % (self.host, self.port),
                                        'content-type': MimeType('multipart', 'form-data', {'boundary': self.boundary}),
                                        'user-agent': 'higgins-uploader/%s' % VERSION
                                        },
                                    self._makePostStream(path, metadata))
            post = waitForDeferred(server.submitRequest(request))
            yield post
            post.getResult()
            logger.log_info("uploaded %s" % path)
        self._deferred.callback(True)
    _processFile = deferredGenerator(_processFile)

    def sendFiles(self):
        if self._deferred:
            raise UploaderException("Uploader instance is already running")
        self._deferred = Deferred()
        reactor.callLater(0, self._processFile)
        return self._deferred

__all__ = ['Uploader', 'UploaderException']
