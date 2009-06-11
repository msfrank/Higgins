import os, sys, signal, time
from twisted.web import client
from higgins import server
from testtool import HigginsTestCase

class UPNPServiceTest(HigginsTestCase):
    """
    Test upnp service functionality.
    """
    def setUp(self):
        self.createEnv('upnptest.tar.gz')
        self.startHiggins()

    def _parseDeviceDescription(self, result):
        print result

    def test_getDeviceDescription(self):
        return client.getPage('http://127.0.0.1:1901/bHyKOGDQWxLUZkZsqtyk').addCallback(self._parseDeviceDescription)

    def tearDown(self):
        self.stopHiggins()
        self.destroyEnv()
