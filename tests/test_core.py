import os, sys, signal, time
from twisted.web import client
from higgins import server
from testtool import HigginsTestCase

class CoreServiceTest(TestCase):
    """
    Test core service functionality.
    """
    def setUp(self):
        os.system('rm -rf /tmp/runnertest-env')
        pid = os.fork()
        if pid == 0:
            os.execlp('higgins-media-server', 'higgins-media-server', '--create', '--debug', '/tmp/runnertest-env')
        self.pid = pid
        time.sleep(3)

    def test_getIndex(self):
        return client.getPage('http://127.0.0.1:8000/')

    def test_getLibraryIndex(self):
        return client.getPage('http://127.0.0.1:8000/library')

    def test_getLibraryMusic(self):
        return client.getPage('http://127.0.0.1:8000/library/music')

    def test_getLibraryPlaylists(self):
        return client.getPage('http://127.0.0.1:8000/library/playlists')

    def test_getSettingsIndex(self):
        return client.getPage('http://127.0.0.1:8000/settings')

    def test_getSettingsPlugins(self):
        return client.getPage('http://127.0.0.1:8000/settings/plugins')

    def tearDown(self):
        os.kill(self.pid, signal.SIGINT)
        time.sleep(2)
        pid,status = os.waitpid(self.pid, os.WNOHANG)
        assert(status == 0)
        os.system('rm -rf /tmp/runnertest-env')
