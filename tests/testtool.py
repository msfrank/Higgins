import sys, os, random, gc, time, warnings
from twisted.trial.runner import TrialRunner, TestLoader
from twisted.trial.reporter import VerboseTextReporter
from twisted.trial.unittest import TestCase, TestSuite

class HigginsTestCase(TestCase):
    def __init__(self):
        TestCase.__init__(self)
    def createEnv(self):
        pass
    def destroyEnv(self):
        pass

if __name__ == '__main__':
    runner = TrialRunner(VerboseTextReporter, workingDirectory='/tmp')

    # find all tests
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
                                print "test case: %s" % loader.methodPrefix + method

    sys.exit(0)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

