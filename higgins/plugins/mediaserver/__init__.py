# Portions of this code from the pymeds project  are licensed under
# the MIT license: http://opensource.org/licenses/mit-license.php
#
# Copyright 2005, Tim Potter <tpot@samba.org>
# Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

from twisted.internet import reactor
from higgins.conf import conf
from higgins.core.models import Song
from higgins.upnp.device import Device
from higgins.http import channel, resource, static
from higgins.http.http import Response as HttpResponse
from higgins.http.stream import FileStream
from higgins.http.server import Site
from higgins.http.http_headers import MimeType
from higgins.plugins.mediaserver.connection_manager import ConnectionManager
from higgins.plugins.mediaserver.content_directory import ContentDirectory
from higgins.plugins.mediaserver.logger import logger

class Content(resource.Resource):
    def render(self, request):
        f = open(self.song.file.path, "r")
        mimetype = MimeType.fromString(self.song.file.mimetype)
        self.song = None
        return HttpResponse(200,
                            {'Content-Type': mimetype },
                            FileStream(f))
    def locateChild(self, request, segments):
        try:
            logger.log_debug("streaming /content/%s" % segments[0])
            item = int(segments[0])
            self.song = Song.objects.filter(id=item)[0]
            logger.log_debug("/content/%s -> %s" % (segments[0], self.song.file.path))
            return self, []
        except Exception, e:
            logger.log_debug("can't stream /content/%s: %s" % (segments[0], e))
            return None, []

class MediaServer(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
    def locateChild(self, request, segments):
        if segments[0] == "content":
            return Content(), segments[1:]
        return None, []

class MediaserverDevice(Device):
    pretty_name = "UPnP Media Server"
    description = "Share media using UPnP"
    upnp_manufacturer = "Higgins Project"
    upnp_model_name = "Higgins"
    upnp_device_type = "urn:schemas-upnp-org:device:MediaServer:1"
    upnp_friendly_name = "Media on Higgins"
    upnp_description = "Higgins UPnP A/V Media Server"
    connection_manager = ConnectionManager()
    content_directory = ContentDirectory()

    def __init__(self):
        pass

    def startService(self):
        Device.startService(self)
        self.server = reactor.listenTCP(31338, channel.HTTPFactory(Site(MediaServer())))
        logger.log_debug("started mediaserver service")

    def stopService(self):
        self.server.stopListening()
        Device.stopService(self)
        logger.log_debug("stopped mediaserver service")
