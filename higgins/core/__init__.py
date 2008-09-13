from twisted.application import internet
from twisted.web2 import resource, wsgi
from higgins.logging import log_debug, log_error
from higgins.core.manager import ManagerResource

class BrowserResource(wsgi.WSGIResource):
    def __init__(self):
        from django.core.handlers.wsgi import WSGIHandler
        wsgi.WSGIResource.__init__(self, WSGIHandler())

class StaticResource(resource.Resource):
    def allowedMethods(self):
        return ("GET",)
    def render(self, request):
        from twisted.web2.static import File
        from os.path import join
        from higgins.conf import conf
        return File(join(conf.get("STATIC_DATA_PATH"), *self.segments))

class RootResource(resource.Resource):
    def __init__(self):
        from higgins.core import BrowserResource
        self.browser = BrowserResource()
    def locateChild(self, request, segments):
        if segments[0] == "static":
            return StaticResource(), segments[1:]
        if segments[0] == "manage":
            return ManagerResource(), segments[1:]
        return self.browser, segments

class CoreService(internet.TCPServer):
    def __init__(self):
        from twisted.web2 import server, channel
        site = server.Site(RootResource())
        internet.TCPServer.__init__(self, 8000, channel.HTTPFactory(site))
        log_debug("started core service on port 8000")
