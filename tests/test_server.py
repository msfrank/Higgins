import os, sys, signal, time
from twisted.internet import reactor
from higgins import server, logger
from testtool import HigginsTestCase

class ServerCreateTest(TestCase):
    """
    Test creating a new server environment.
    """
    def setUp(self):
        os.system('rm -rf /tmp/createtest-env')
    def test_createEnvironment(self):
        pid = os.fork()
        if pid == 0:
            try:
                self.s = server.Server('/tmp/createtest-env', create=True, debug=True)
                os._exit(0)
            except Exception, e:
                print "caught exception: %s" % e
                os._exit(1)
        time.sleep(5)
        pid,status = os.waitpid(pid, os.WNOHANG)
        assert(status == 0)
    def tearDown(self):
        os.system('rm -rf /tmp/createtest-env')

class ServerStopTest(TestCase):
    """
    Test stopping the server using the Server.stop() method.
    """
    def setUp(self):
        os.system('rm -rf /tmp/stoptest-env')
    def test_stopServer(self):
        pid = os.fork()
        if pid == 0:
            try:
                self.s = server.Server('/tmp/stoptest-env', create=True, debug=True)
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

class ServerRunnerTest(TestCase):
    """
    Test running the server from the command line, and stopping it by
    sending the SIGINT signal.
    """
    def setUp(self):
        os.system('rm -rf /tmp/runnertest-env')
    def test_runServer(self):
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
