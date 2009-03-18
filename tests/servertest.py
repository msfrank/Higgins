import os, sys, signal, time
from twisted.internet import reactor
import unittest
from higgins import server

class ServerCreateTest(unittest.TestCase):
    """
    Test creating a new server environment.
    """
    def setUp(self):
        os.system('rm -rf /tmp/createtest-env')
    def runTest(self):
        pid = os.fork()
        if pid == 0:
            try:
                self.s = server.Server('/tmp/createtest-env', create=True, debug=True, verbosity=4)
                os._exit(0)
            except Exception, e:
                print "caught exception: %s" % e
                os._exit(1)
        time.sleep(5)
        pid,status = os.waitpid(pid, os.WNOHANG)
        assert(status == 0)
    def tearDown(self):
        os.system('rm -rf /tmp/createtest-env')

class ServerStopTest(unittest.TestCase):
    """
    Test stopping the server using the Server.stop() method.
    """
    def setUp(self):
        os.system('rm -rf /tmp/stoptest-env')
    def runTest(self):
        pid = os.fork()
        if pid == 0:
            try:
                self.s = server.Server('/tmp/stoptest-env', create=True, debug=True, verbosity=4)
                reactor.callLater(5, self.s.stop)
                self.s.run()
                os._exit(0)
            except Exception, e:
                print "caught exception: %s" % e
                os._exit(1)
        time.sleep(10)
        pid,status = os.waitpid(pid, os.WNOHANG)
        assert(status == 0)
    def tearDown(self):
        os.system('rm -rf /tmp/stoptest-env')

class ServerRunnerTest(unittest.TestCase):
    """
    Test running the server from the command line, and stopping it by
    sending the SIGINT signal.
    """
    def setUp(self):
        os.system('rm -rf /tmp/runnertest-env')
    def runTest(self):
        pid = os.fork()
        if pid == 0:
            os.execlp('higgins-media-server', 'higgins-media-server', '--create', '--debug', '/tmp/runnertest-env')
        self.pid = pid
        time.sleep(5)
        os.kill(pid, signal.SIGINT)
        time.sleep(2)
        pid,status = os.waitpid(pid, os.WNOHANG)
        assert(status == 0)
    def tearDown(self):
        os.system('rm -rf /tmp/runnertest-env')

if __name__ == '__main__':
    unittest.main()
