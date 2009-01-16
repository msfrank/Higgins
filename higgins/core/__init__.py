from twisted.application import internet
from twisted.web2 import resource, wsgi
from twisted.web2.server import StopTraversal
from twisted.web2.static import File
from logger import CoreLogger
from higgins.conf import conf
from higgins.core.manager import ManagerResource
from os.path import join

class BrowserResource(wsgi.WSGIResource):
    def __init__(self):
        from django.core.handlers.wsgi import WSGIHandler
        wsgi.WSGIResource.__init__(self, WSGIHandler())

class StaticResource(resource.Resource):
    def allowedMethods(self):
        return ("GET",)
    def locateChild(self, request, segments):
        self.path = join(conf.get("STATIC_DATA_PATH"), *segments)
        return self, []
    def render(self, request):
        return File(self.path)

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

class CoreService(internet.TCPServer, CoreLogger):
    def __init__(self):
        from twisted.web2 import server, channel
        site = server.Site(RootResource())
        internet.TCPServer.__init__(self, 8000, channel.HTTPFactory(site))
        self.log_debug("started core service on port 8000")
