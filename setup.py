#!/usr/bin/env python

import sys

# initialize setuptools and ez_setup
#
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension

# check for runtime dependencies
#
try:
    import Pyrex
    import twisted
    import axiom
    import gobject
    import dbus
    import avahi
    import pygst
    try:
        pygst.require('0.10')
    except pygst.RequiredVersionError, e:
        raise Exception("Higgins needs pygst version 0.10, detected version %s" % pygst._pygst_version)
except ImportError, e:
    print "setup.py failed due to a missing dependency: %s" % e
    sys.exit(1)
except Exception, e:
    print "setup.py failed: %s" % e
    sys.exit(1)

# pass control to setuptools
#
setup(
    # package description
    name = "Higgins",
    version = "0.1.0",
    description="Multi-protocol A/V Server",
    long_description="",
    url="http://www.syntaxjockey.com/higgins",
    author="Michael Frank",
    author_email="msfrank@syntaxockey.com",
    # package contents
    packages=[
        'higgins',
        'higgins.gst',
        'higgins.http',
        'higgins.http.auth',
        'higgins.http.channel',
        'higgins.http.filter',
        'higgins.http.client',
        'higgins.http.dav',
        'higgins.http.dav.method',
        'higgins.http.dav.element',
        'higgins.platform',
        'higgins.plugins',
        'higgins.plugins.daap',
        #'higgins.plugins.mediaserver',
        #'higgins.plugins.mrss',
        #'higgins.plugins.upnp',
        ],
    namespace_packages=['higgins', 'higgins.plugins'],
    ext_modules=[
        Extension('higgins.platform.netif',
                 ['higgins/platform/netif.pyx', 'higgins/platform/netif-internal.c']
                 ),
        #Extension('higgins.platform.inotify',
        #         ['higgins/platform/inotify.pyx', 'higgins/platform/inotify-internal.c']
        #         )
        ],
    entry_points={
        # auto-generate scripts
        'console_scripts': [
            'higgins-media-server=higgins.server:run_application',
            'higgins-uploader=higgins.uploader:run_application',
            ],
        # declare packaged plugins
        'higgins.plugin': [
            'daap=higgins.plugins.daap:DaapService',
            #'mediaserver=higgins.plugins.mediaserver:MediaserverDevice',
            #'mrss=higgins.plugins.mrss:MRSSService',
            ],
        },
    test_suite="tests",
)
