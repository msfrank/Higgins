from setuptools import setup, Extension

setup(
    name = "UPnP MediaServer",
    version = "0.1",
    packages = ['higgins_upnp'],
    ext_modules = [ Extension("netif", ["higgins_upnp/netif.pyx", "higgins_upnp/netif-internal.c"]), ],
    entry_points = {
        'higgins.plugin.service': 'upnp=higgins_upnp:UpnpService',
        'higgins.plugin.config': 'upnp=higgins_upnp:UpnpConfig'
    }
)

