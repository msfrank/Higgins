import os, sys, signal, time
from twisted.web import client
from higgins import server
from testtool import HigginsTestCase

class CoreServiceTest(HigginsTestCase):
    """
    Test core service functionality.
    """
    def setUp(self):
        self.createEnv(None)
        self.startHiggins()

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
        self.stopHiggins()
        self.destroyEnv()
