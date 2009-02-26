# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

__import__('pkg_resources').declare_namespace(__name__)

from pkg_resources import get_distribution

_dist = get_distribution('higgins')

PROJECT_NAME = _dist.project_name
VERSION = _dist.version
