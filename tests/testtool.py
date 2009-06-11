#!/usr/bin/env python2.5

import sys, os, time, signal, tempfile, tarfile
from twisted.trial.runner import TrialRunner, TestLoader
from twisted.trial.reporter import VerboseTextReporter
from twisted.trial.unittest import TestCase, TestSuite

class HigginsTestCase(TestCase):
    def __init__(self, methodName, fixtureDir, workingDir):
        self._methodName = methodName
        TestCase.__init__(self, methodName)
        self._fixtureDir = fixtureDir
        self._workingDir = workingDir
        self._envDir = None

    def createEnv(self, name=None):
        self._envDir = os.path.join(self._workingDir, "%s_%s" % (self.__class__.__name__, self._methodName))
        if name:
            os.mkdir(self._envDir)
            print "created environment %s" % self._envDir
            archivePath = os.path.join(self._fixtureDir, name)
            archive = tarfile.open(archivePath)
            archive.extractall(self._envDir)
            archive.close()
            print "extracted %s" % archivePath
            self._doCreate = False
        else:
            self._doCreate = True

    def startHiggins(self):
        pid = os.fork()
        if pid == 0:
            args = ['higgins-media-server', 'higgins-media-server', '--debug']
            if self._doCreate:
                args += ['--create']
            args += [self._envDir]
            os.execlp(*args)
        self._pid = pid
        time.sleep(3)

    def stopHiggins(self):
        os.kill(self._pid, signal.SIGINT)
        time.sleep(2)
        pid,status = os.waitpid(self._pid, os.WNOHANG)
        assert(status == 0)

    def destroyEnv(self):
        _recursiveDelete(self._envDir)

def _recursiveDelete(root):
    if not os.path.abspath(root).startswith('/tmp/'):
        raise Exception("Stupidity alert!  Ignoring recursive delete outside /tmp")
    print "recursively deleting %s" % root
    for base, dirs, files in os.walk(root, topdown=False):
        for name in files:
            file = os.path.join(base, name)
            #os.remove(file)
            print "deleted %s" % file
        for name in dirs:
            dir = os.path.join(base, name)
            #os.rmdir(dir)
            print "deleted %s/" % dir
    #os.rmdir(root)
    print "deleted %s/" % root

if __name__ == '__main__':
    status = 0
    workingDir = tempfile.mkdtemp('', 'testtool.', '/tmp')
    try:
        print ""
        print "workingDir = %s" % workingDir
        fixtureDir = os.path.join(os.getcwd(), 'fixtures')
        print "fixtureDir = %s" % fixtureDir
        print ""

        runner = TrialRunner(VerboseTextReporter, workingDirectory=workingDir)
        suite = TestSuite()

        # find all tests
        print "searching for test cases ..."
        loader = TestLoader()
        for root,dirs,files in os.walk('.'):
            for name in files:
                if name.startswith('test_') and name.endswith('.py'):
                    module = loader.findByName(os.path.join(root,name))
                    classes = loader.findTestClasses(module)
                    if len(classes) > 0:
                        for cls in classes:
                            methods = loader.getTestCaseNames(cls)
                            if len(methods) > 0:
                                for method in methods:
                                    methodName = loader.methodPrefix + method
                                    print "found %s" % methodName
                                    suite.addTest(cls(methodName, fixtureDir, workingDir))
        print ""
        print "running test cases ..."
        print ""
        result = runner.run(suite)
        status = result.wasSuccessful()
    except Exception, e:
        print "testtool.py failed: %s" % str(e)
        status = 1
    finally:
        _recursiveDelete(workingDir)
    sys.exit(status)
