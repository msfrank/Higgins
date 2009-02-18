from content_codes import content_codes, ContentType
from struct import pack

class CodeBagException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ContentCode:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        try:
            type,fullname = content_codes[name]
            self.type = type
            self.fullname = fullname
            if type == ContentType.List:
                    raise CodeBagException("can't create a ContentCode from list-type")
            elif type == ContentType.String:
                if not isinstance(value, str):
                    raise CodeBagException("value for %s is the wrong type" % name)
                self.value = value
            elif type == ContentType.Byte:
                if value < -127 or value > 128:
                    raise CodeBagException("value for %s is out of range" % name)
                self.value = value
            elif type == ContentType.Short:
                if value < -32767 or value > 32768:
                    raise CodeBagException("value for %s is out of range" % name)
                self.value = value
            elif type == ContentType.Long:
                self.value = value
            elif type == ContentType.LongLong:
                self.value = value
            elif type == ContentType.Date:
                self.value = value
            elif type == ContentType.Version:
                self.value = value
            else:
                raise CodeBagException("unknown content type")
        except KeyError:
            raise CodeBagException("couldn't find code with name '%s'" % name)
        self.value = value
    def __str__(self):
        return "%s (%s): %s" % (self.name,self.fullname,self.value)

class CodeBag:
    def __init__(self, name):
        self.name = name
        try:
            type,fullname = content_codes[name]
            self.type = type
            self.fullname = fullname
            if type == ContentType.List:
                self.children = []
            else:
                 raise CodeBagException("content type is not 'list'")
        except KeyError:
            raise CodeBagException("couldn't find code with name '%s'" % name)

    def add(self, child):
        if not isinstance(child, CodeBag) and not isinstance(child, ContentCode):
            return CodeBagException("child type isn't CodeBag or ContentCode")
        self.children.append(child)

    def render(self):
        buf = ""
        for child in self.children:
            if isinstance(child, CodeBag):
                buf = buf + child.render()
            elif child.type == ContentType.String:
                buf = buf + pack('>4si', child.name, len(child.value)) + child.value
            elif child.type == ContentType.Byte:
                buf = buf + pack('>4sib', child.name, 1, child.value)
            elif child.type == ContentType.Short:
                buf = buf + pack('>4sih', child.name, 2, child.value)
            elif child.type == ContentType.Long:
                buf = buf + pack('>4sil', child.name, 4, child.value)
            elif child.type == ContentType.LongLong:
                buf = buf + pack('>4siq', child.name, 8, child.value)
            elif child.type == ContentType.Date:
                buf = buf + pack('>4sil', child.name, 4, child.value)
            elif child.type == ContentType.Version:
                buf = buf + pack('>4sihbb', child.name, 4, child.value[0], child.value[1], child.value[2])
            else:
                raise CodeBagException("unknown content type")
        temp = pack('>4si', self.name, len(buf))
        return temp + buf

    def __repr__(self):
        return "<%s: contains %s children>" % (self.fullname, len(self.children))
