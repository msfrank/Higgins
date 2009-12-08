# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os, sys
from twisted.python import usage, log
from higgins.logger import LOG_FATAL, LOG_WARNING, LOG_DEBUG, LOG_DEBUG2

class UploaderObserver(log.DefaultObserver):
    def __init__(self, verbosity=0):
        self.verbosity = verbosity
    def _emit(self, params):
        if 'level' in params:
            level = params['level']
        else:
            level = LOG_DEBUG
        if level <= self.verbosity:
            print ''.join(params['message'])

class UploaderOptions(usage.Options):
    optFlags = [
        ['local-mode', 'l', None],
        ['recursive', 'r', None],
    ]
    optParameters = [
        ['host', 'H', 'localhost', None],
        ['port', 'P', 8000, None, int],
    ]

    def __init__(self):
        usage.Options.__init__(self)
        self['verbose'] = LOG_WARNING

    def opt_quiet(self):
        if self['verbose'] > LOG_FATAL: 
            self['verbose'] = self['verbose'] - 1
    opt_q = opt_quiet

    def opt_verbose(self):
        if self['verbose'] < LOG_DEBUG2: 
            self['verbose'] = self['verbose'] + 1
    opt_v = opt_verbose

    def parseArgs(self, *paths):
        if len(paths) == 0:
            raise usage.UsageError("No media files specified.")
        self['paths'] = paths

    def opt_help(self):
        print "Usage: %s [OPTIONS...] FILE..." % os.path.basename(sys.argv[0])
        print "       %s [OPTIONS...] -r DIR..." % os.path.basename(sys.argv[0])
        print ""
        print "  --local-mode,-l        File itself will not be uploaded"
        print "  --host,-H HOST         The host to upload to.  Default is 'localhost'"
        print "  --port,-P PORT         The port higgins is running on.  Default is '8000'"
        print "  --recursive,-r         Recursively upload media files in directories"
        print "  --verbose,-v           Increase verbosity (use -vv or -vvv for even more messages)"
        print "  --quiet,-q             Decrease verbosity (use -qq for even less messages)"
        print "  --help,-h              Display this help"
        print "  --version,-V           Display the version"
        print ""
        sys.exit(0)
    opt_h = opt_help

    def opt_version(self):
        from higgins import VERSION
        print "Higgins uploader version " + VERSION
        sys.exit(0)
    opt_V = opt_version

def run_application():
    exitStatus = 0
    try:
        # parse command line arguments
        o = UploaderOptions()
        o.parseOptions(sys.argv[1:])
	    # load the gstreamer reactor.  we do this here instead of at the top
        # of the file because gstreamer seems to implement its own command line
        # options parsing, and we want to get around that.
        from higgins.gst import installGstReactor
        installGstReactor()
        from twisted.internet import reactor
        from higgins.core.upload import Uploader
        # create logging observer
        observer = UploaderObserver(verbosity=o['verbose'])
        observer.start()
        # create list of files to upload
        if o['recursive']:
            paths = []
            for dir in o['paths']:
                for root,dirs,files in os.walk(dir, topdown=True):
                    for file in files:
                        paths.append(os.path.abspath(os.path.join(root,file)))
        else:
            paths = []
            for file in o['paths']:
                paths.append(os.path.abspath(file))
        # create uploader instance and run it
        uploader = Uploader(paths, host=o['host'], port=o['port'], isLocal=o['local-mode'])
        deferred = uploader.sendFiles()
        deferred.addCallback(lambda result: reactor.stop())
        reactor.run()
        observer.stop()
    except usage.UsageError, e:
        print "Error parsing options: %s" % e
        print ""
        print "Try %s --help for usage information." % os.path.basename(sys.argv[0])
        exitStatus = 1
    except Exception, e:
        print "Error: %s" % e
        exitStatus = 1
    sys.exit(exitStatus)
