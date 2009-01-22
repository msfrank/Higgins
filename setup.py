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
    # package requirements
    #install_requires=['Twisted', 
    #                  'twisted.web2',
    #                  'pysqlite',
    #                  'Django >= 1.0.0',
    #                  'mutagen',
    #                  'dbus',
    #                  'avahi',
    #    ],
    # package contents
    packages=['higgins',
              'higgins.core',
              'higgins.data',
              'higgins.netif',
              'higgins.upnp',
        ],
    ext_modules=[Extension('higgins.netif.commands', ['higgins/netif/commands.pyx', 'higgins/netif/netif-internal.c'])],
    package_data={'higgins.data': ['css/*.css', 'templates/*.t', 'images/*.png', 'images/*.jpg']},
    # auto-generate the higgins-media-server script
    entry_points={
        'console_scripts': [ 'higgins-media-server=higgins:run_application' ],
        },
)

