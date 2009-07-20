# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet import defer
from higgins.http.resource import Resource
from higgins.http.http_headers import Headers, DefaultHTTPHandler, tokenize, parseArgs
from higgins.http.http import Response
from higgins.http.stream import BufferedStream
from higgins.http import fileupload
from higgins.http.logger import logger

class ContentDisposition:
    def __init__(self, type, params):
        self.type = type
        self.params = params
    def __repr__(self):
        return "%s, params=%s" % (self.type,self.params)

def _parseContentDisposition(header):
    """
    Parses a Content-Disposition header.
    """
    type,args = parseArgs(header)
    type = type[0].lower()
    if not type == "form-data" and not type == "file":
        raise ValueError("Content-Disposition type is not 'form-data' or 'file'")
    return ContentDisposition(type, dict(args))
DefaultHTTPHandler.addParser("content-disposition", (tokenize, _parseContentDisposition))

class BaseResource(Resource):
    def allowedMethods(self):
        return ('HEAD','GET','POST','PUT','DELETE','OPTIONS')

    def renderHTTP(self, request):
        request.post = {}
        request.files = []
        return Resource.renderHTTP(self, request)

    def http_POST(self, request):
        content_type = request.headers.getHeader('content-type')
        if content_type.mediaType == 'multipart' and content_type.mediaSubtype == 'form-data':
            request.boundary = content_type.params.get('boundary')
            request.buffered_stream = BufferedStream(request.stream)
            return self._readMultipartFormData(request).addCallbacks(lambda l: self.render(request))
        elif content_type.mediaType == 'application' and content_type.mediaSubtype == 'x-www-form-urlencoded':
            d = fileupload.parse_urlencoded(request.stream)
            d.addCallback(self.updatePost, request)
            d.addCallback(lambda l: self.render(request))
            return d
        logger.log_debug("can't handle POST request: unknown media type %s/%s" % (content_type.mediaType,content_type.mediaSubtype))
        return Response(400)

    def http_PUT(self, request):
        content_type = request.headers.getHeader('content-type')
        if content_type.mediaType == 'multipart' and content_type.mediaSubtype == 'form-data':
            request.boundary = content_type.params.get('boundary')
            request.buffered_stream = BufferedStream(request.stream)
            return self._readMultipartFormData(request).addCallbacks(lambda l: self.render(request))
        elif content_type.mediaType == 'application' and content_type.mediaSubtype == 'x-www-form-urlencoded':
            d = fileupload.parse_urlencoded(request.stream)
            d.addCallback(self.updatePost, request)
            d.addCallback(lambda l: self.render(request))
            return d
        return Response(400)

    def http_DELETE(self, request):
        if request.stream.length != 0:
            return responsecode.REQUEST_ENTITY_TOO_LARGE
        return self.render(request)

    def updatePost(self, args, request):
        request.post.update(args)
        logger.log_debug("parsed POST args: %s" % args)
        return request

    def acceptFile(self, request, subheaders):
        """
        The default function which is called before reading a file sent via an HTTP POST.
        If the return value is a string, then the stream data will be appended to the
        file at the path referenced by the string, otherwise the stream data is discarded.

        Note that if for some reason open() fails (part of the path doesn't exists, you
        don't have permission, ...) we will silently fail and move on.  It is the
        responsibility of the implementor of acceptFile to do these checks.
        """
        return None

    def _readMultipartFormData(self, request):
        """
        This is a big momma of a function... The entirety of the stream parsing is handled
        within this function.  Essentially it is a state machine consisting of 6 steps:

        State 1 (READ_FIRST_BOUNDARY): read in the first boundary line and discard it.  

        State 2 (READ_HEADERS): read in the headers for a single part of the multipart
            stream.  We only care about Content-Type and Content-Disposition, anything
            else is not documented (but we save it anyways).

        State 3 (PROCESS_HEADERS): check the content-disposition header to see what kind
            of data we are working with.  If we are saving a file, then call
            self.acceptFile() to determine where to save to.

        State 4 (READ_BODY):

        State 5 (PROCESS_BODY):

        State 6 (FINISHED):
        """

        # context for the state machine
        class Context:
            STATE_READ_FIRST_BOUNDARY = "FIRST_BOUNDARY"
            STATE_READ_HEADERS = "READ_HEADERS"
            STATE_PROCESS_HEADERS = "PROCESS_HEADERS"
            STATE_READ_BODY = "READ_BODY"
            STATE_PROCESS_BODY = "PROCESS_BODY"
            STATE_FINISHED = "FINISHED"
            def __init__(self):
                self.state = Context.STATE_READ_FIRST_BOUNDARY
                self.leftover = None
                self.headers = Headers()
                self.is_done = False

        # Write data to opaque handle instance.
        def _writeToHandle(handle, data):
            if not handle == None:
                if isinstance(handle, list):
                    handle.append(data)
                else:
                    handle.write(data)

        # Clean up handle after we are done with it.
        def _closeHandle(handle):
            if not handle == None:
                if not isinstance(handle, list):
                    handle.close()

        request.ctxt = Context()

        while True:
            if request.buffered_stream.length == 0:
                if request.ctxt.state == Context.STATE_READ_BODY:
                    request.ctxt.state = Context.STATE_PROCESS_BODY
                else:
                    if request.ctxt.state != Context.STATE_READ_HEADERS:
                        logger.log_error("reached end of request, state is %s" % request.ctxt.state)
                    break

            ##########################################################
            # STATE_READ_FIRST_BOUNDARY                              #
            ##########################################################
            if request.ctxt.state == Context.STATE_READ_FIRST_BOUNDARY:
                retval = request.buffered_stream.readline()
                if isinstance(retval, defer.Deferred):
                    data = defer.waitForDeferred(retval)
                    yield data
                    data = data.getResult()
                data = data.strip()
                if not data == "--" + request.boundary:
                    logger.log_debug("boundary error: expected '%s'" % (request.boundary))
                    logger.log_debug("     `--------> received '%s'" % (data))
                request.ctxt.state = Context.STATE_READ_HEADERS

            ##########################################################
            # STATE_READ_HEADERS                                     #
            ##########################################################
            if request.ctxt.state == Context.STATE_READ_HEADERS:
                retval = request.buffered_stream.readline()
                if isinstance(retval, defer.Deferred):
                    data = defer.waitForDeferred(retval)
                    yield data
                    data = data.getResult()
                data = data.strip()
                if data == "":
                    request.ctxt.state = Context.STATE_PROCESS_HEADERS
                else:
                    namevalue = data.split(':', 1)
                    if len(namevalue) == 2:
                        name, value = namevalue
                        request.ctxt.headers.addRawHeader(name, value.strip())
                    else:
                        logger.log_debug("header error: failed to parse '%s'" % data)

            ##########################################################
            # STATE_PROCESS_HEADERS                                  #
            ##########################################################
            if request.ctxt.state == Context.STATE_PROCESS_HEADERS:
                content_disposition = request.ctxt.headers.getHeader('content-disposition')
                if 'name' in content_disposition.params:
                    request.ctxt.name = content_disposition.params['name']
                else:
                    request.ctxt.name = None
                if content_disposition.type == 'file' or 'filename' in content_disposition.params:
                    try:
                        request.ctxt.handle = self.acceptFile(request, request.ctxt.headers)
                    except Exception, e:
                        logger.log_debug("acceptFile failed: %s" % e)
                        request.ctxt.handle = None
                else:
                    request.ctxt.handle = []
                request.ctxt.state = Context.STATE_READ_BODY

            ##########################################################
            # STATE_READ_BODY                                        #
            ##########################################################
            if request.ctxt.state == Context.STATE_READ_BODY:
                retval = request.buffered_stream.readExactly(512)
                if isinstance(retval, defer.Deferred):
                    data = defer.waitForDeferred(retval)
                    yield data
                    data = data.getResult()
                i = 0
                while i < len(data):
                    if request.ctxt.leftover:
                        request.ctxt.leftover = request.ctxt.leftover + data[i]
                        if len(request.ctxt.leftover) == len(request.boundary) + 6:
                            if request.ctxt.leftover.startswith('\r\n--' + request.boundary):
                                request.buffered_stream.pushback(data[i+1:])
                                if not request.ctxt.leftover.endswith('\r\n'):
                                    request.ctxt.is_done = True
                                request.ctxt.leftover = None
                                _closeHandle(request.ctxt.handle)
                                request.ctxt.state = Context.STATE_PROCESS_BODY
                                break
                            else:
                                # write request.leftover to file
                                _writeToHandle(request.ctxt.handle, request.ctxt.leftover)
                                request.ctxt.leftover = None
                                data = data[i+1:]
                                i = 0
                        else:
                            i = i + 1
                    else:
                        if data[i] == '\r':
                            request.ctxt.leftover = data[i]
                            data = data[i+1:]
                            i = 0
                        else:
                            # write data[i] to file
                            _writeToHandle(request.ctxt.handle, data[i])
                            i = i + 1

            ##########################################################
            # STATE_PROCESS_BODY                                     #
            ##########################################################
            if request.ctxt.state == Context.STATE_PROCESS_BODY:
                if request.ctxt.handle:
                    # add the form data to the http.Request.post dictionary
                    if isinstance(request.ctxt.handle, list):
                        value = u''.join(request.ctxt.handle)
                        request.post[request.ctxt.name] = value
                        logger.log_debug("parsed post param '%s'='%s'" % (request.ctxt.name,value))
                    # add the file info to the http.Request.files list
                    else:
                        request.files.append(request.ctxt.handle)
                        logger.log_debug("created file '%s'" % request.ctxt.handle.path)
                # reset the context
                request.ctxt.headers = Headers()
                request.ctxt.leftover = None
                if request.ctxt.is_done == True:
                    request.ctxt.state = Context.STATE_FINISHED
                else:
                    request.ctxt.state = Context.STATE_READ_HEADERS
            
            ##########################################################
            # STATE_FINISHED                                         #
            ##########################################################
            if request.ctxt.state == Context.STATE_FINISHED:
                break

        # finished state machine
        request.ctxt = None

    _readMultipartFormData = defer.deferredGenerator(_readMultipartFormData)

    def _errback(self, error):
        """
        Any error which results in this callback being triggered should be returned
        to the client as an internal server error.
        """
        return Response(500)
