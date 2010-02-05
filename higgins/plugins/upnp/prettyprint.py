# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.
# 
# Portions of this code come from Filip Salomonsson:
# http://infix.se/2007/02/06/gentlemen-indent-your-xml

from xml.sax.saxutils import escape

def xmlprint(root, pretty=True, withXMLDecl=True):
    """
    Output the XML tree as a string.  If pretty=True, then indent the
    output to make it more readable.  if withXMLDecl=True, then print
    the <?xml?> declaration at the beginning of the output.
    """
    def printNode(node, level, pretty):
        if pretty:
            indent = str(level * '  ')
        else:
            indent = ''
        out = indent
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
                if pretty:
                    out += '\n'
                out += printNode(child, level + 1, pretty)
            if pretty:
                out += '\n' + indent
        out += '</%s>' % name
        return out
    out = printNode(root, 0, pretty)
    if withXMLDecl == True:
        out = '<?xml version="1.0"?>\n' + out
    return str(out)
