import os, sys, signal, time
from twisted.internet import reactor
import unittest
from higgins import server

class ServerCreateTest(unittest.TestCase):
    def setUp(self):
        os.system('rm -rf createtest-env/')
    def runTest(self):
        try:
            self.s = server.Server('createtest-env', create=True, debug=True, verbosity=4)
        except Exception, e:
            print "caught exception: %s" % e
            raise AssertionError()
    def tearDown(self):
        os.system('rm -rf createtest-env/')

class ServerStopTest(unittest.TestCase):
    def setUp(self):
        os.system('rm -rf stoptest-env/')
    def runTest(self):
        try:
            self.s = server.Server('stoptest-env', create=True, debug=True, verbosity=4)
            reactor.callLater(5, self.s.stop)
            self.s.run()
        except Exception, e:
            print "caught exception: %s" % e
            raise AssertionError()
    def tearDown(self):
        os.system('rm -rf stoptest-env/')

class ServerRunnerTest(unittest.TestCase):
    def setUp(self):
        os.system('rm -rf runnertest-env/')
    def runTest(self):
        pid = os.fork()
        if pid == 0:
            os.execlp('higgins-media-server', 'higgins-media-server', '--create', '--debug', 'runnertest-env')
        self.pid = pid
        time.sleep(5)
        os.kill(pid, signal.SIGINT)
        time.sleep(2)
        pid,status = os.waitpid(pid, os.WNOHANG)
        assert(status == 0)
    def tearDown(self):
        os.system('rm -rf runnertest-env/')

if __name__ == '__main__':
    unittest.main()
