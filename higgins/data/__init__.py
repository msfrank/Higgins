# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from pkg_resources import resource_stream
from genshi.template.loader import TemplateLoader
from higgins.logger import Loggable

class DataLogger(Loggable):
    log_domain = 'data'
logger = DataLogger()

class TemplateStore(TemplateLoader):
    def __init__(self, package, auto_reload=True, **options):
        self._dataPackage = package
        TemplateLoader.__init__(self, search_path=self._loadFromPackage, auto_reload=auto_reload, **options)
    def _loadFromPackage(self, path):
        """Return template information"""
        fileobj = resource_stream(self._dataPackage, path)
        filepath = path
        filename = path
        logger.log_debug("loading template %s:%s" % (self._dataPackage, path))
        return filepath, filename, fileobj, None
    def render(self, path, vars, output='html', doctype='html'):
        t = self.load(path)
        gen = t.generate(**vars)
        return gen.render(output, doctype=doctype)

templates = TemplateStore("higgins.data")
