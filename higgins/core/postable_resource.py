from twisted.web2 import http, resource, http_headers
from twisted.internet import defer
from twisted.web2.stream import BufferedStream
from higgins.logging import log_error, log_debug

class ContentDisposition:
    def __init__(self, type, params):
        self.type = type
        self.params = params
    def __repr__(self):
        return "%s, params=%s" % (self.type,self.params)

def parseContentDisposition(header):
    """
    Parses a Content-Disposition header.
    """
    type,args = http_headers.parseArgs(header)
    type = type[0].lower()
    if not type == "form-data" and not type == "file":
        raise ValueError("Content-Disposition type is not 'form-data' or 'file'")
    return ContentDisposition(type, dict(args))
http_headers.DefaultHTTPHandler.addParser("content-disposition", (http_headers.tokenize, parseContentDisposition))

class PostableResource(resource.Resource):
    def acceptFile(self, headers):
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
            STATE_READ_FIRST_BOUNDARY = 1
            STATE_READ_HEADERS = 2
            STATE_PROCESS_HEADERS = 3
            STATE_READ_BODY = 4
            STATE_PROCESS_BODY = 5
            STATE_FINISHED = 6
            def __init__(self):
                self.state = Context.STATE_READ_FIRST_BOUNDARY
                self.leftover = None
                self.headers = http_headers.Headers()
                self.is_done = False

        # Write data to opaque handle instance.
        def _writeToHandle(handle, data):
            if isinstance(handle, list):
                handle.append(data)
            elif isinstance(handle, file):
                handle.write(data)

        # Clean up handle after we are done with it.
        def _closeHandle(handle):
            if isinstance(handle, file):
                handle.close()

        request.ctxt = Context()

        # keep reading from request.buffered_stream until its empty
        while request.buffered_stream.length > 0:

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
                    log_debug("boundary error: expected '%s'" % (request.boundary))
                    log_debug("     `--------> received '%s'" % (data))
                request.ctxt.state = Context.STATE_READ_HEADERS

            ##########################################################
            # STATE_READ_HEADERS                                     #
            ##########################################################
            elif request.ctxt.state == Context.STATE_READ_HEADERS:
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
                        log_debug("header error: failed to parse '%s'" % data)

            ##########################################################
            # STATE_PROCESS_HEADERS                                  #
            ##########################################################
            elif request.ctxt.state == Context.STATE_PROCESS_HEADERS:
                content_disposition = request.ctxt.headers.getHeader('content-disposition')
                if 'name' in content_disposition.params:
                    request.ctxt.name = content_disposition.params['name']
                else:
                    request.ctxt.name = None
                content_type = request.ctxt.headers.getHeader('content-type')
                if isinstance(content_type, http_headers.MimeType):
                    request.ctxt.mimetype = content_type.mediaType + '/' + content_type.mediaSubtype
                else:
                    request.ctxt.mimetype = None
                if 'filename' in content_disposition.params:
                    try:
                        from os.path import abspath
                        path = self.acceptFile(request.ctxt.headers)
                        if not path == None:
                            request.ctxt.filename = abspath(path)
                            request.ctxt.handle = open(request.ctxt.filename, "w")
                        else:
                            request.ctxt.handle = None
                    except:
                        request.ctxt.handle = None
                else:
                    request.ctxt.handle = []
                request.ctxt.state = Context.STATE_READ_BODY

            ##########################################################
            # STATE_READ_BODY                                        #
            ##########################################################
            elif request.ctxt.state == Context.STATE_READ_BODY:
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
            elif request.ctxt.state == Context.STATE_PROCESS_BODY:
                # add the file info to the http.Request.files list
                if isinstance(request.ctxt.handle, file):
                    request.files.append((request.ctxt.name, request.ctxt.filename, request.ctxt.mimetype))
                # add the form data to the http.Request.post dictionary
                elif isinstance(request.ctxt.handle, list):
                    value = u''.join(request.ctxt.handle)
                    request.post[request.ctxt.name] = value
                # reset the context
                request.ctxt.headers = http_headers.Headers()
                request.ctxt.leftover = None
                if request.ctxt.is_done == True:
                    request.ctxt.state = Context.STATE_FINISHED
                else:
                    request.ctxt.state = Context.STATE_READ_HEADERS
            
            ##########################################################
            # STATE_FINISHED                                         #
            ##########################################################
            elif request.ctxt.state == Context.STATE_FINISHED:
                break

        request.ctxt = None
    _readMultipartFormData = defer.deferredGenerator(_readMultipartFormData)

    def _errback(self, error):
        """
        Any error which results in this callback being triggered should be returned
        to the client as an internal server error.
        """
        return http.Response(500)

    def http_POST(self, request):
        request.post = {}
        request.files = []
        content_type = request.headers.getHeader('content-type')
        if content_type.mediaType == 'multipart' and content_type.mediaSubtype == 'form-data':
            request.boundary = content_type.params.get('boundary')
            request.buffered_stream = BufferedStream(request.stream)
            return self._readMultipartFormData(request).addCallbacks(lambda l: self.render(request))
        elif content_type.mediaType == 'application' and content_type.mediaSubtype == 'x-www-form-urlencoded':
            return http.Response(400)
        return http.Response(400)
