# -*- test-case-name: higgins.http.test.test_cgi,higgins.http.test.test_http -*-
# See LICENSE for details.

"""
Various backend channel implementations for web2.
"""
from higgins.http.channel.cgi import startCGI
from higgins.http.channel.scgi import SCGIFactory
from higgins.http.channel.http import HTTPFactory
from higgins.http.channel.fastcgi import FastCGIFactory

__all__ = ['startCGI', 'SCGIFactory', 'HTTPFactory', 'FastCGIFactory']
