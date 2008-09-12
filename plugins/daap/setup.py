from setuptools import setup

setup(
    name = "DAAP Share Server",
    version = "0.1",
    packages = ['higgins_daap'],
    entry_points = {
        'higgins.plugin.service': 'daap=higgins_daap:DaapService',
        'higgins.plugin.config': 'daap=higgins_daap:DaapConfig'
    }
)

