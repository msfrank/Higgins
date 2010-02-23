# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from pkg_resources import resource_string
from mako.template import Template
from mako.exceptions import html_error_template
from higgins.plugins.ria.logger import logger

class TemplateLookup(object):
    def __init__(self, group):
        self.group = group

    def adjust_uri(self, uri, relativeto):
        return uri

    def get_template(self, uri):
        if ':' in uri:
            return Template(resource_string(uri.split(':', 1)), lookup=self, format_exceptions=True)
        return Template(resource_string(self.group, uri), lookup=self, format_exceptions=True)
