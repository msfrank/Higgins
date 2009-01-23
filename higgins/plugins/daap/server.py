from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet import defer
from logger import DAAPLogger
import os

class DAAPResource:
    def locateResource(self, request, segments):
        return None

    def renderDAAP(self, request):
        raise DAAPResponse(404, body="The requested resource '%s' was not found." % request.abs_path)

class DAAPStream:
    def prepare(self, transport):
        self.deferred = defer.Deferred()
        self.transport = transport
        return self.deferred

    def start(self):
        self.transport.registerProducer(self, False)

    def length(self):
        return None

    def close(self):
        pass

class DAAPDataStream(DAAPStream, DAAPLogger):
    def __init__(self, data):
        self.data = data
        self.size = len(data)
        self.nleft = self.size

    def length(self):
        return self.size

    def close(self):
        self.data = None

    def pauseProducing(self):
        pass

    def resumeProducing(self):
        self.transport.write(self.data)
        self.transport.unregisterProducer()
        self.deferred.callback(None)
        self.deferred = None

    def stopProducing(self):
        self.log_debug("DAAPDataStream.stopProducing() was called")

class DAAPFileStream(DAAPStream, DAAPLogger):
    def __init__(self, file):
        self.file = file
        file.seek(0, os.SEEK_END)
        self.size = file.tell()
        file.seek(0, os.SEEK_SET)
        self.nleft = self.size

    def length(self):
        return self.size

    def close(self):
        self.file.close()

    def pauseProducing(self):
        pass

    def resumeProducing(self):
        chunk = ''
        if self.file:
            chunk = self.file.read(4096)
        if not chunk:
            self.transport.unregisterProducer()
            if self.deferred:
                self.deferred.callback(None)
                self.deferred = None
            return
        self.transport.write(chunk)

    def stopProducing(self):
        log_debug("DAAPFileStream.stopProducing() was called")

class DAAPResponse:
    _status_codes = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
    }
    def __init__(self, status_code, headers={}, body=""):
        self.status_code = status_code
        self.status_msg = DAAPResponse._status_codes[status_code]
        self.headers = headers
        self.body = body

class DAAPRequest(DAAPLogger):
    def __init__(self, session):
        self.session = session
        self.session.setLineMode()
        self.method = None 
        self.scheme = None
        self.host = None
        self.abs_path = None
        self.args = {}
        self.http_version = None
        self.parsed_headers = False
        self.headers = {}
        self.daap_client_version = None
        self.daap_client_access_index = None
        self.daap_client_validation = None
        self.daap_client_request_id = None

    def _parseInitialLine(self, line):
        # break the initial line into method, uri, and version
        try:
            self.method,uri,version = line.split(' ')
        except:
            raise DAAPResponse(400)
        # parse the method
        if not self.method == 'GET':
            raise DAAPResponse(405)
        # parse the URI
        try:
            # try to parse as an absolute URI
            self.scheme,uri = uri.split('://', 1)
            try:
                self.host,uri = uri.split('/', 1)
            except:
                self.host = uri
                uri = "/"
            else:
                uri = '/' + uri
        except:
            # is a relative URI
            self.scheme = "daap"
            self.host = None
        # split the remaining string into path and query params
        try:
            self.abs_path,params = uri.split('?', 1)
        except:
            self.abs_path = uri
        else:
            # parse each individual param
            while True:
                param,sep,params = params.partition('&')
                name,unused,value = param.partition('=')
                if not name == '':
                    self.args[name] = value
                if sep == '' and params == '':
                    break
        # normalize the http version
        self.http_version = version.upper()
        self.log_debug("method=%s, uri=%s, version=%s" %
                       (self.method, self.abs_path, self.http_version)
                 )

    def _parseHeader(self, header):
        name,value = header.split(':', 1)
        name = name.strip()
        value = value.strip()
        self.headers[name] = value
        # set daap-specific properties
        if name == 'Client-DAAP-Version':
            self.daap_client_version = value
        if name == 'Client-DAAP-Access-Index':
            self.daap_client_access_index = value
        if name == 'Client-DAAP-Validation':
            self.daap_client_validation = value
        if name == 'Client-DAAP-Request-ID':
            self.daap_client_request_id = value

    def lineReceived(self, line):
        if not self.http_version:
            self._parseInitialLine(line)
        elif not line == '':
            self._parseHeader(line)
        else:
            segments = self.abs_path[1:].split('/')
            command = self.session.factory.root
            while True:
                command,segments = command.locateResource(self, segments)
                if command == None:
                    raise DAAPResponse(404)
                if segments == []:
                    raise command.renderDAAP(self)

class DAAPSession(LineReceiver, DAAPLogger):
    def __init__(self):
        self.setLineMode()
        self.persist = False
        self.stream = None
        self.requests_left = None   # None == unlimited requests
        self.request = None
        self.response = None

    def lineReceived(self, line):
        try:
            # we do a double try-catch block to convert any unhandled
            # exceptions into 500 errors
            try:
                if not self.request:
                    self.request = DAAPRequest(self)
                self.request.lineReceived(line)
            except DAAPResponse, r:
                raise r
            except Exception, e:
                self.log_error("DAAPSession caught exception: %s (type=%s)" % (e, str(type(e))))
                raise DAAPResponse(500)
        except DAAPResponse, response:
            #self.transport.stopReading()
            self._writeResponse(response)
        except defer.Deferred, deferred:
            self.deferred = deferred
            self.deferred.addCallback(self._writeResponse)
            self.deferred.addErrback(self._failureResponse)
            #self.transport.stopReading()

    def _writeResponse(self, response):
        self.response = response
        # get the response stream, or create one if necessary
        if isinstance(response.body, DAAPStream):
            self.stream = response.body
        else:
            self.stream = DAAPDataStream(str(response.body))
        # figure out whether to persist the connection
        if self.request.http_version == "HTTP/1.1":
            self.persist = True
        else:
            self.persist = False
        if self.request.headers.get('Connection', '') == 'close':
            self.persist = False
        if not self.requests_left == None and self.requests_left == 0:
            self.persist = False
        stream_length = self.stream.length()
        if stream_length == None:
            self.persist = False
        if response.status_code == 400:
            self.persist = False
        # write out the response initial line
        self.sendLine("%s %d %s" % (self.request.http_version,
                                    response.status_code,
                                    response.status_msg))
        # write out the response headers
        self.sendLine("DAAP-Server: Higgins/0.0.1")
        for hname,hvalue in response.headers.items():
            self.sendLine("%s: %s" % (hname,hvalue))
        if not self.persist:
            self.sendLine("Connection: Close")
        if not stream_length == None:
            self.sendLine("Content-Length: %d" % stream_length)
        self.sendLine("")
        self.setRawMode()
        self.deferred = self.stream.prepare(self.transport)
        self.deferred.addCallback(self._successResponse)
        self.deferred.addErrback(self._failureResponse)
        self.stream.start()

    def _successResponse(self, result):
        self.deferred = None
        self.request = None
        self.response = None
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.persist:
            if not self.requests_left == None:
                self.requests_left = self.requests_left - 1
            self.setLineMode()
            #self.transport.startReading()
        else:
            self.transport.loseConnection()

    def _failureResponse(self, failure):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.deferred = None
        self.stream = None
        self.request = None
        self.response = None
        self.transport.loseConnection()
        self.log_error("failed to write response")

    def connectionLost(self, reason):
        self.log_debug("connection was lost")
        if self.deferred:
            self.deferred.errback(reason)
        self.deferred = None

class DAAPFactory(ServerFactory):
    protocol = DAAPSession
    def __init__(self, root):
        self.root = root
