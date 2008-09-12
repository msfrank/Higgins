from twisted.application import internet
from twisted.web2 import resource, wsgi
from higgins.logging import log_debug, log_error

class BrowserResource(wsgi.WSGIResource):
    def __init__(self):
        from django.core.handlers.wsgi import WSGIHandler
        wsgi.WSGIResource.__init__(self, WSGIHandler())

#class ManagerResource(resource.Resource):
#    def locateChild(self, request, segments):
#        if segments[0] == "create":
#            return CreateCommand(), []
#        if segments[0] == "update":
#            return UpdateCommand(), []
#        if segments[0] == "delete":
#            return DeleteCommand(), []
#        return None, []

class RootResource(resource.Resource):
    def __init__(self):
        from higgins.core import BrowserResource
        self.browser = BrowserResource()
    def locateChild(self, request, segments):
#        from higgins.core import ManagerResource
        if segments[0] == "static":
            self.segments = segments[1:]
            return self, []
#        if segments[0] == "manage":
#            return ManagerResource(), segments[1:]
        return self.browser, segments
    def renderHTTP(self, request):
        from twisted.web2.static import File
        from os.path import join
        from higgins.conf import conf
        return File(join(conf.get("STATIC_DATA_PATH"), *self.segments))

class CoreService(internet.TCPServer):
    def __init__(self):
        from twisted.web2 import server, channel
        site = server.Site(RootResource())
        internet.TCPServer.__init__(self, 8000, channel.HTTPFactory(site))
        log_debug("started core service on port 8000")
