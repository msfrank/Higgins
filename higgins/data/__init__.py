# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from pkg_resources import resource_string
from django.template import TemplateDoesNotExist
from higgins.conf import conf
from higgins.core.logger import logger

def load_template_source(template_name, template_dirs=None):
    """
    Loads templates for django from Python eggs via pkg_resource.resource_string.
    """
    if resource_string is not None:
        pkg_name = 'templates/' + template_name
        try:
            charset = conf.get('FILE_CHARSET', 'ISO-8859-1')
            return (resource_string('higgins.data', pkg_name).decode(charset), 'higgins.data:%s' % pkg_name)
        except Exception, e:
            logger.log_warning("failed to load template '%s': %s" % (template_name,e))
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True
