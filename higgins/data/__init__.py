# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from pkg_resources import resource_string
from genshi.template.loader import TemplateLoader
from higgins.logger import Loggable

class DataLogger(Loggable):
    log_domain = 'data'
logger = DataLogger()

class TemplateDoesNotExist(Exception):
    def __init__(self, pkg, path):
        self.pkg = pkg
        self.path = path
    def __str__(self):
        return 'Template %s:%s does not exist' % (self.pkg,self.path)

def renderTemplate(path, attrs):
    """
    Loads templates for django from Python eggs via pkg_resource.resource_string.
    """
    try:
        pkg_name,template_path = path.split(':', 1)
    except:
        pkg_name = 'higgins.data'
        template_path = path
    try:
        template = resource_string(pkg_name, template_path)
        # TODO: render template using attrs
        return template
    except Exception, e:
        logger.log_warning("failed to load template %s: %s" % (path,e))
        raise TemplateDoesNotExist(pkg_name, template_path)

class TemplateStore(TemplateLoader):
    def __init__(self, package, auto_reload=True, **options):
        self._dataPackage = package
        TemplateLoader.__init__(self, search_path=self._loadFromPackage, auto_reload=auto_reload, **options)
    def _loadFromPackage(self, path):
        """Return template information"""
        fileobj = resource_string(self._dataPackage, path)
        filepath = path
        filename = path
        uptodate = True
        return filepath, filename, fileobj, uptodate
