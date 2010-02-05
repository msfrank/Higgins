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

    def __init__(self, type, sendEvents=False, defaultValue=None, allowedValueList=None, allowedMin=None, allowedMax=None, allowedStep=None):
        self.type = type
        self.sendEvents = sendEvents
        self._value = None
        self.allowedValueList = None
        self.allowedMin = None
        self.allowedMax = None
        self.allowedStep = None
        if allowedValueList:
            self.allowedValueList = [self.validate(v) for v in allowedValueList]
        if allowedMin:
            self.allowedMin = self.validate(allowedMin)
        if allowedMax:
            self.allowedMax = self.validate(allowedMax)
        if allowedStep:
            self.allowedStep = allowedStep
        if sendEvents or defaultValue != None:
            self._value = self.validate(defaultValue)
        # these variables are set when the related Service is parsed
        self.name = None
        self.service = None

    def validate(self, value):
        raise Exception("no validator available")

    def checkBounds(self, value):
        raise Exception("no bounds-checker available")

    def parse(self, text_value):
        raise Exception("no parser available")

    def write(self, value):
        raise Exception("no writer available")

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        value = self.validate(value)
        if self.allowedValueList and not value in self.allowedValueList:
            raise Exception("value is not within the allowedValueList")
        if self.allowedMin or self.allowedMax:
            self.checkBounds(value)
        self._value = value
        if self.sendEvents:
            self.service._notify([self])

    def _get_text_value(self):
        if self.value == None:
            return None
        return self.write(self.value)

    value = property(_get_value, _set_value)
    text_value = property(_get_text_value)

class I4StateVar(StateVar):
    def __init__(self, **kwds):
        StateVar.__init__(self, StateVar.TYPE_I4, **kwds)
    def validate(self, i4):
        if i4 < -2147483648 or i4 > 2147483647:
            raise Exception("input value is out-of-bounds")
        return i4
    def checkBounds(self, value):
        if self.allowedMin and value < self.allowedMin:
            raise Exception("input value is out-of-bounds")
        if self.allowedMax and value > self.allowedMax:
            raise Exception("input value is out-of-bounds")
    def parse(self, text_value):
        return self.validate(int(text_value))
    def write(self, value):
        return str(self.validate(value))

class UI4StateVar(StateVar):
    def __init__(self, **kwds):
        StateVar.__init__(self, StateVar.TYPE_UI4, **kwds)
    def validate(self, ui4):
        if ui4 < 0 or ui4 > 4294967295:
            raise Exception("input value is out-of-bounds")
        return ui4
    def checkBounds(self, value):
        if self.allowedMin and value < self.allowedMin:
            raise Exception("input value is out-of-bounds")
        if self.allowedMax and value > self.allowedMax:
            raise Exception("input value is out-of-bounds")
    def parse(self, text_value):
        return self.validate(int(text_value))
    def write(self, value):
        return str(self.validate(value))

class StringStateVar(StateVar):
    def __init__(self, **kwds):
        StateVar.__init__(self, StateVar.TYPE_STRING, **kwds)
    def validate(self, text):
        if not isinstance(text, str):
            raise Exception("input value must be a string")
        return str(text)
    def parse(self, text_value):
        return self.validate(str(text_value))
    def write(self, value):
        return str(self.validate(value))
