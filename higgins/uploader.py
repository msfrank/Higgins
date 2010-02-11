#!/usr/bin/env python

# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os, sys
import simplejson, random, string
from os.path import basename
from higgins.gst.reactor import installReactor
installReactor()
from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred, waitForDeferred, deferredGenerator
from twisted.python import usage, log
from higgins.http.stream import MemoryStream, FileStream, CompoundStream
from higgins.http.http_headers import MimeType
from higgins.http.client.http import HTTPClientProtocol, ClientRequest
from higgins.gst.metadata import MetadataFinder
from higgins.logger import Loggable, Severity
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
            lines.append('')
        # create the stream which is sent to the server 
        stream = MemoryStream('\r\n'.join(lines))
        if not self.isLocal:
            stream = CompoundStream((stream, FileStream(open(filePath, 'rb'))))
        return stream

    def _doSendFiles(self):
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
                self._makePostStream(path, metadata)
                )
            post = waitForDeferred(server.submitRequest(request))
            yield post
            post.getResult()
            logger.log_info("uploaded %s" % path)
        self._deferred.callback(True)
    _doSendFiles = deferredGenerator(_doSendFiles)

    def sendFiles(self):
        if self._deferred:
            raise UploaderException("Uploader instance is already running")
        self._deferred = Deferred()
        reactor.callLater(0, self._doSendFiles)
        return self._deferred

class UploaderObserver(log.DefaultObserver):
    def __init__(self, verbosity=0):
        self.verbosity = verbosity
    def _emit(self, params):
        if 'level' in params:
            level = params['level']
        else:
            level = Severity.DEBUG
        if level <= self.verbosity:
            print ''.join(params['message'])

class UploaderOptions(usage.Options):
    optFlags = [
        ['local-mode', 'l', None],
        ['recursive', 'r', None],
    ]
    optParameters = [
        ['host', 'H', 'localhost', None],
        ['port', 'P', 8000, None, int],
    ]

    def __init__(self):
        usage.Options.__init__(self)
        self['verbose'] = Severity.WARNING

    def opt_quiet(self):
        if self['verbose'] > Severity.FATAL: 
            self['verbose'] = self['verbose'] - 1
    opt_q = opt_quiet

    def opt_verbose(self):
        if self['verbose'] < Severity.DEBUG2: 
            self['verbose'] = self['verbose'] + 1
    opt_v = opt_verbose

    def parseArgs(self, *paths):
        if len(paths) == 0:
            raise usage.UsageError("No media files specified.")
        self['paths'] = paths

    def opt_help(self):
        print "Usage: %s [OPTIONS...] FILE..." % os.path.basename(sys.argv[0])
        print "       %s [OPTIONS...] -r DIR..." % os.path.basename(sys.argv[0])
        print ""
        print "  --local-mode,-l        File itself will not be uploaded"
        print "  --host,-H HOST         The host to upload to.  Default is 'localhost'"
        print "  --port,-P PORT         The port higgins is running on.  Default is '8000'"
        print "  --recursive,-r         Recursively upload media files in directories"
        print "  --verbose,-v           Increase verbosity (use -vv or -vvv for even more messages)"
        print "  --quiet,-q             Decrease verbosity (use -qq for even less messages)"
        print "  --help,-h              Display this help"
        print "  --version,-V           Display the version"
        print ""
        sys.exit(0)
    opt_h = opt_help

    def opt_version(self):
        from higgins import VERSION
        print "Higgins uploader version " + VERSION
        sys.exit(0)
    opt_V = opt_version

def run_application():
    exitStatus = 0
    try:
        # parse command line arguments
        o = UploaderOptions()
        o.parseOptions(sys.argv[1:])
        # create logging observer
        observer = UploaderObserver(verbosity=o['verbose'])
        observer.start()
        # create list of files to upload
        if o['recursive']:
            paths = []
            for dir in o['paths']:
                for root,dirs,files in os.walk(dir, topdown=True):
                    for file in files:
                        paths.append(os.path.abspath(os.path.join(root,file)))
        else:
            paths = []
            for file in o['paths']:
                paths.append(os.path.abspath(file))
        # create uploader instance and run it
        uploader = Uploader(paths, host=o['host'], port=o['port'], isLocal=o['local-mode'])
        deferred = uploader.sendFiles()
        deferred.addCallback(lambda result: reactor.stop())
        reactor.run()
        observer.stop()
    except usage.UsageError, e:
        print "Error parsing options: %s" % e
        print ""
        print "Try %s --help for usage information." % os.path.basename(sys.argv[0])
        exitStatus = 1
    except Exception, e:
        print "Error: %s" % e
        exitStatus = 1
    sys.exit(exitStatus)
