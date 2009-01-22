from twisted.application import internet
from twisted.web2 import resource, wsgi
from twisted.web2.http import Response
from higgins.conf import conf
from higgins.core.manager import ManagerResource
from higgins.core.logger import CoreLogger
from os.path import join as pathjoin
from pkg_resources import resource_string

class BrowserResource(wsgi.WSGIResource):
    def __init__(self):
        from django.core.handlers.wsgi import WSGIHandler
        wsgi.WSGIResource.__init__(self, WSGIHandler())

class StaticResource(resource.Resource):
    def allowedMethods(self):
        return ("GET",)
    def locateChild(self, request, segments):
        path = pathjoin(*segments)
        try:
            self.data = resource_string('higgins.data', path)
            return self, []
        except:
            return None, []
    def render(self, request):
        return Response(200, headers=None, stream=self.data)

class RootResource(resource.Resource):
    def __init__(self):
        self.browser = BrowserResource()
    def locateChild(self, request, segments):
        if segments[0] == "static":
            return StaticResource(), segments
        if segments[0] == "manage":
            return ManagerResource(), segments[1:]
        return self.browser, segments

class CoreService(internet.TCPServer, CoreLogger):
    def __init__(self):
        from twisted.web2 import server, channel
        site = server.Site(RootResource())
        internet.TCPServer.__init__(self, 8000, channel.HTTPFactory(site))
        self.log_debug("started core service on port 8000")
