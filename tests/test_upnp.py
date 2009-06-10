import os, sys, signal, time
from twisted.web import client
from higgins import server
from testtool import HigginsTestCase

class UPNPServiceTest(TestCase):
    """
    Test upnp service functionality.
    """
    def setUp(self):
        os.system('rm -rf /tmp/upnptest-env')
        os.system('pwd')
        os.system('cp -r ~/projects/higgins.git/tests/test-envs/upnptest-env /tmp/upnptest-env')
        pid = os.fork()
        if pid == 0:
            os.execlp('higgins-media-server', 'higgins-media-server', '--debug', '/tmp/upnptest-env')
        self.pid = pid
        time.sleep(3)

    def _parseDeviceDescription(self, result):
        print result

    def test_getDeviceDescription(self):
        return client.getPage('http://127.0.0.1:1901/bHyKOGDQWxLUZkZsqtyk').addCallback(self._parseDeviceDescription)

    def tearDown(self):
        os.kill(self.pid, signal.SIGINT)
        time.sleep(2)
        pid,status = os.waitpid(self.pid, os.WNOHANG)
        assert(status == 0)
        os.system('rm -rf /tmp/upnptest-env')
