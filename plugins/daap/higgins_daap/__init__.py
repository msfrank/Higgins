from twisted.application import internet
from server import DAAPFactory
from commands import DAAPCommand
from higgins.conf import conf
from higgins.logging import log_debug, log_error
import dbus, avahi

class DaapService(internet.TCPServer):
    def __init__(self):
        self.name = "DAAP"
        self.description = "Exposes the Higgins media store as a DAAP (iTunes) share"
        # initialize config options
        if conf.get("DAAP_SHARE_NAME") == None:
            conf.set(DAAP_SHARE_NAME="Higgins DAAP Share")
        # create the DAAP command hierarchy
        # create the avahi interface object
        self.dbus = dbus.SystemBus()
        proxy = self.dbus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
        self.avahi_server = dbus.Interface(proxy, avahi.DBUS_INTERFACE_SERVER)
        internet.TCPServer.__init__(self, 3689, DAAPFactory(DAAPCommand()))

    def startService(self):
        internet.TCPServer.startService(self)
        proxy = self.dbus.get_object(avahi.DBUS_NAME, self.avahi_server.EntryGroupNew())
        self.avahi_group = dbus.Interface(proxy, avahi.DBUS_INTERFACE_ENTRY_GROUP)
        self.avahi_group.AddService(avahi.IF_UNSPEC,
                                    avahi.PROTO_UNSPEC,
                                    0,
                                    conf.get("DAAP_SHARE_NAME"),
                                    "_daap._tcp", 
                                    "", "", 3689, [])
        self.avahi_group.Commit()
        log_debug("started DAAP service")

    def stopService(self):
        internet.TCPServer.stopService(self)
        self.avahi_group.Reset()
        self.avahi_group = None
        log_debug("stopped DAAP service")
        return None

from django import forms

class DaapConfig(forms.Form):
    DAAP_SHARE_NAME = forms.CharField(label="DAAP Share Name")
