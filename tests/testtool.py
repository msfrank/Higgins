#!/usr/bin/env python2.5

import sys, os, time, tempfile
from twisted.trial.runner import TrialRunner, TestLoader
from twisted.trial.reporter import VerboseTextReporter
from twisted.trial.unittest import TestCase, TestSuite

class HigginsTestCase(TestCase):
    def __init__(self, methodName, env):
        TestCase.__init__(self, methodName)
        self._higginsEnv = env
    def createEnv(self):
        pass
    def destroyEnv(self):
        pass

def _recursiveDelete(root):
    if not os.path.abspath(root).startswith('/tmp/'):
        raise Exception("Stupidity alert!  Ignoring recursive delete outside /tmp")
    print "recursively deleting %s" % root
    for base, dirs, files in os.walk(root, topdown=False):
        for name in files:
            file = os.path.join(base, name)
            os.remove(file)
            print "deleting %s" % file
        for name in dirs:
            dir = os.path.join(base, name)
            os.rmdir(dir)
            print "deleting %s/" % dir
    os.rmdir(root)
    print "deleting %s/" % root

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
                                    suite.addTest(cls(methodName, fixtureDir))
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
