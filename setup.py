#!/usr/bin/env python2.5

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension

setup(
    # package description
    name = "Higgins",
    version = "0.1",
    description="Multi-protocol A/V Server",
    long_description="",
    url="http://www.syntaxjockey.com/higgins",
    # package contents
    packages=['higgins',
              'higgins.core',
              'higgins.data',
              'higgins.netif',
              'higgins.plugins',
              'higgins.plugins.daap',
              'higgins.plugins.mediaserver',
              'higgins.upnp',
              'higgins.web2',
        ],
    namespace_packages=['higgins', 'higgins.plugins'],
    ext_modules=[Extension('higgins.netif.commands',
                           ['higgins/netif/commands.pyx', 'higgins/netif/netif-internal.c'])
        ],
    package_data={'higgins.data': ['static/css/*.css', 'templates/*.t', 'static/images/*.*']},
    scripts=['scripts/higgins-upload',],
    # auto-generate the higgins-media-server script
    entry_points={
        'console_scripts': ['higgins-media-server=higgins:run_application',
            ],
        'higgins.plugin': ['daap=higgins.plugins.daap:DaapService',
                           #'mediaserver=higgins.plugins.mediaserver:MediaserverService',
            ],
        },
)

