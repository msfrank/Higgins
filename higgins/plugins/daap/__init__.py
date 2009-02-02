from higgins.service import Service
from higgins.conf import conf
from higgins.core import configurator
from server import DAAPFactory
from commands import DAAPCommand
from logger import DAAPLogger
from twisted.internet import reactor
import dbus, avahi

class DaapConfig(configurator.Configurator):
    DAAP_SHARE_NAME = configurator.StringSetting("Share Name")

class DaapService(Service, DAAPLogger):
    service_name = "DAAP"
    service_description = "Exposes the Higgins media store as a DAAP (iTunes) share"
    service_config = DaapConfig

    def __init__(self):
        try:
            import dbus, avahi
        except ImportError, e:
            raise e
        # initialize config options
        if conf.get("DAAP_SHARE_NAME") == None:
            conf.set(DAAP_SHARE_NAME="Higgins DAAP Share")
        # create the avahi interface object
        self.dbus = dbus.SystemBus()
        proxy = self.dbus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
        self.avahi_server = dbus.Interface(proxy, avahi.DBUS_INTERFACE_SERVER)
        Service.__init__(self)

    def startService(self):
        # create the DAAP listener
        self.listener = reactor.listenTCP(3689, DAAPFactory(DAAPCommand()))
        proxy = self.dbus.get_object(avahi.DBUS_NAME, self.avahi_server.EntryGroupNew())
        self.avahi_group = dbus.Interface(proxy, avahi.DBUS_INTERFACE_ENTRY_GROUP)
        self.avahi_group.AddService(avahi.IF_UNSPEC,
                                    avahi.PROTO_UNSPEC,
                                    0,
                                    conf.get("DAAP_SHARE_NAME"),
                                    "_daap._tcp", 
                                    "", "", 3689, [])
        self.avahi_group.Commit()
        Service.startService(self)
        self.log_debug("started DAAP service")

    def stopService(self):
        self.avahi_group.Reset()
        self.avahi_group = None
        self.listener.stopListening()
        self.log_debug("stopped DAAP service")
        Service.stopService(self)
        return None
