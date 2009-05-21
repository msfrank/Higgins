# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.
# 
# Portions of this code come from Filip Salomonsson:
# http://infix.se/2007/02/06/gentlemen-indent-your-xml

from xml.etree.ElementTree import tostring
from xml.sax.saxutils import escape

#def prettyprint(root):
#    def indent(elem, level=0):
#        i = "\n" + level*"  "
#        if len(elem):
#            if not elem.text or not elem.text.strip():
#                elem.text = i + "  "
#            for e in elem:
#                indent(e, level+1)
#                if not e.tail or not e.tail.strip():
#                    e.tail = i + "  "
#            if not e.tail or not e.tail.strip():
#                e.tail = i
#        else:
#            if level and (not elem.tail or not elem.tail.strip()):
#                elem.tail = i
#    indent(root)
#    return '<?xml version="1.0"?>\n' + tostring(root)

def prettyprint(root):
    def printNode(node, level):
        out = level * '  '
        attribs = ''
        for name,value in node.attrib.items():
            attribs += ' %s="%s"' % (name,value)
        name = node.tag
        if node.text:
            text = escape(node.text, {'"': '&quot;'})
        else:
            text = ''
        out += '<%s%s>%s' % (name, attribs, text)
        if len(node) > 0:
            for child in node:
                out += '\n' + printNode(child, level + 1)
            out += '\n' + (level * '  ')
        out += '</%s>' % name
        return out
    return str('<?xml version="1.0"?>\n' + printNode(root, 0))
