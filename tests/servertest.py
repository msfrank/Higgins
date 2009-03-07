import os, sys, signal, time
import unittest
from higgins import server

class ServerCreateTest(unittest.TestCase):
    def setUp(self):
        os.system('rm -rf servertest-env/')
        self.s = None
        print "ran ServerCreateTest.setUp"
    def runTest(self):
        print "running ServerCreateTest"
        try:
            self.s = server.Server('servertest-env', create=True, debug=True, verbosity=4)
        except Exception, e:
            print "caught exception: %s" % e
            raise AssertionError()
    def tearDown(self):
        if self.s:
            self.s.stop()
        os.system('rm -rf servertest-env/')
        print "ran ServerCreateTest.tearDown"

class ServerRunnerTest(unittest.TestCase):
    def setUp(self):
        os.system('rm -rf servertest-env/')
        print "ran ServerRunnerTest.setUp"
    def runTest(self):
        print "running ServerRunnerTest"
        pid = os.fork()
        if pid == 0:
            os.execlp('higgins-media-server', 'higgins-media-server', '--create', '--debug', 'servertest-env')
        self.pid = pid
        time.sleep(5)
        os.kill(pid, signal.SIGINT)
        time.sleep(2)
        pid,status = os.waitpid(pid, os.WNOHANG)
        assert(status == 0)
    def tearDown(self):
        os.system('rm -rf servertest-env/')
        print "ran ServerRunnerTest.tearDown"

if __name__ == '__main__':
    unittest.main()
