#!/usr/bin/env python2.5

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension

setup(
    # package description
    name = "Higgins",
    version = "0.4",
    description="Multi-protocol A/V Server",
    long_description="",
    url="http://www.syntaxjockey.com/higgins",
    author="Michael Frank",
    author_email="msfrank@syntaxockey.com",
    # package requirements
    install_requires=[
#        'Twisted >= 8.0.0',
#        'Django >= 1.0.0',
#        'pysqlite >= 2.5.0',
#        'pybonjour >= 1.1.1',
#        'mutagen >= 1.15',
        ],
    # package contents
    packages=[
        'higgins',
        'higgins.core',
        'higgins.core.upgradedb',
        'higgins.data',
        'higgins.http',
        'higgins.http.auth',
        'higgins.http.channel',
        'higgins.http.filter',
        'higgins.http.client',
        'higgins.http.dav',
        'higgins.http.dav.method',
        'higgins.http.dav.element',
        'higgins.netif',
        'higgins.plugins',
        'higgins.plugins.daap',
        'higgins.plugins.mediaserver',
        'higgins.plugins.mrss',
        'higgins.upnp',
        ],
    namespace_packages=['higgins', 'higgins.plugins'],
    ext_modules=[
        Extension('higgins.netif.commands',
            ['higgins/netif/commands.pyx', 'higgins/netif/netif-internal.c'])
        ],
    # declare static data
    package_data={
        'higgins.data': [
            'static/css/*.css',
            'static/css/smoothness/*.css',
            'static/css/smoothness/images/*.*',
            'static/images/*.*',
            'static/js/*.js',
            'templates/*.t',
            ],
        'higgins.plugins.mrss': ['templates/*.t',],
        },
    entry_points={
        # auto-generate scripts
        'console_scripts': [
            'higgins-media-server=higgins.server:run_application',
            'higgins-upload=higgins.core.upload:run_application',
            ],
        # declare packaged plugins
        'higgins.plugin': [
            'daap=higgins.plugins.daap:DaapService',
            'mediaserver=higgins.plugins.mediaserver:MediaserverDevice',
            #'mrss=higgins.plugins.mrss:MRSSService',
            ],
        },
    test_suite="tests",
)
