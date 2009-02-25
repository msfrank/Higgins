# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

class StateVar(object):
    TYPE_I1 = "i1"
    TYPE_UI1 = "ui1"
    TYPE_I2 = "i2"
    TYPE_UI2 = "ui2"
    TYPE_I4 = "i4"
    TYPE_UI4 = "ui4"
    TYPE_INT = "int"
    TYPE_R4 = "r4"
    TYPE_R8 = "r8"
    TYPE_NUMBER = "number"
    TYPE_FIXED_14_4 = "fixed.14.4"
    TYPE_FLOAT = "float"
    TYPE_CHAR = "char"
    TYPE_STRING = "string"
    TYPE_DATE = "date"
    TYPE_DATETIME = "dateTime"
    TYPE_DATETIME_TZ = "dateTime.tz"
    TYPE_TIME = "time"
    TYPE_TIME_TZ = "time.tz"
    TYPE_BOOLEAN = "boolean"
    TYPE_BIN_BASE64 = "bin.base64"
    TYPE_BIN_HEX = "bin.hex"
    TYPE_URI = "uri"
    TYPE_UUID = "uuid"

    def __init__(self, type, sendEvents="no", defaultValue=None, allowedValueList=None, allowedMin=None, allowedMax=None, allowedStep=None):
        self.type = type
        self.sendEvents = sendEvents
        self.defaultValue = defaultValue
        self.allowedValueList = allowedValueList
        self.allowedMin = allowedMin
        self.allowedMax = allowedMax
        self.allowedStep = allowedStep

    def parse(self, text_value):
        raise Exception("no parser available")

class I4StateVar(StateVar):
    def __init__(self, **kwds):
        StateVar.__init__(self, StateVar.TYPE_I4, **kwds)

    def parse(self, text_value):
        i4 = int(text_value)
        if i4 < -2,147,483,648 or i4 > 2,147,483,647:
            raise Exception("text_value is out-of-bounds")
        return i4

class StringStateVar(StateVar):
    def __init__(self, **kwds):
        StateVar.__init__(self, StateVar.TYPE_STRING, **kwds)

    def parse(self, text_value):
        return str(text_value)
