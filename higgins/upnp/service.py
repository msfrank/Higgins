from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring

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
        pass

class EventedStateVar(StateVar):
    def __init__(self, type, **kwds):
        kwds['sendEvents'] = 'yes'
        StateVar.__init__(self, type, **kwds)

class Argument(object):
    DIRECTION_IN = "in"
    DIRECTION_OUT = "out"
    def __init__(self, name, direction, related, retval=False):
        self.name = name
        if not direction == Argument.DIRECTION_IN and not direction == Argument.DIRECTION_OUT:
            raise Exception("argument direction must be 'in' or 'out'")
        self.direction = direction
        self.related = related
        self.retval = retval

class Action(object):
    def __init__(self, action, *args):
        if not callable(action):
            raise Exception("%s is not callable" % str(action))
        self.action = action
        self.name = action.__name__
        self.in_args = []
        self.out_args = []
        for arg in args:
            if arg.direction == Argument.DIRECTION_IN:
                self.in_args.append(arg)
            else:
                self.out_args.append(arg)
    def __call__(self, service, arguments):
        # arguments is a dict.  key is the argument name, value is
        # the argument value as a string.
        a = self.in_args.copy()
        parsed_args = []
        while not a == []:
            arg = a.pop(0)
            try:
                arg_value = arguments[arg.name]
                parsed_args.append(arg.parse(arg_value))
            except KeyError:
                raise Exception("missing required argument %s" % arg.name)
            except Exception, e:
                raise e
        out_args = self.action(service, *parsed_args)
        for arg_name,arg_value in out_args.items():

class ServiceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # load state variables
        stateVars = {}
        for key,object in attrs.items():
            if isinstance(object, StateVar):
                stateVars[key] = object
        # load actions
        actions = {}
        for key,object in attrs.items():
            if isinstance(object, Action):
                actions[key] = object
        # load stateVars and actions from any base classes
        for base in bases:
            if hasattr(base, '_upnp_stateVars'):
                base._upnp_stateVars.update(stateVars)
                stateVars = base._upnp_stateVars
            if hasattr(base, '_upnp_actions'):
                base._upnp_actions.update(actions)
                actions = base._upnp_actions
        attrs['_upnp_stateVars'] = stateVars
        attrs['_upnp_actions'] = actions
        return super(ServiceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class Service(object):
    __metaclass__ = ServiceDeclarativeParser

    upnp_service_type = None
    upnp_service_id = None

    def get_description(self):
        scpd = Element("{urn:schemas-upnp-org:service-1-0}scpd")
        version = SubElement(scpd, "specVersion")
        SubElement(version, "major").text = "1"
        SubElement(version, "minor").text = "0"
        action_list = SubElement(scpd, "actionList")
        for action_name,upnp_action in self._upnp_actions.items():
            action = SubElement(action_list, "action")
            SubElement(action, "name").text = action_name
            arg_list = SubElement(action, "argumentList")
            all_args = upnp_action.in_args + upnp_action.out_args
            for upnp_arg in all_args:
                arg = SubElement(arg_list, "argument")
                SubElement(arg, "name").text = upnp_arg.name
                SubElement(arg, "direction").text = upnp_arg.direction
                SubElement(arg, "relatedStateVariable").text = upnp_arg.related
                if upnp_arg.retval:
                    SubElement(arg, "retval")
        var_list = SubElement(scpd, "serviceStateTable")
        for var_name,upnp_stateVar in self._upnp_stateVars.items():
            stateVar = SubElement(var_list, "stateVariable")
            SubElement(stateVar, "name").text = var_name
            SubElement(stateVar, "dataType").text = upnp_stateVar.type
            if not upnp_stateVar.defaultValue == None:
                SubElement(stateVar, "defaultValue").text = upnp_stateVar.defaultValue
            if not upnp_stateVar.allowedValueList == None:
                allowed_list = SubElement(stateVar, "allowedValueList")
                for allowed in upnp_stateVar.allowedValueList:
                    SubElement(allowed_list, "allowedValue").text = allowed
            if not upnp_stateVar.allowedMin == None and not upnp_stateVar.allowedMax == None:
                allowed_range = SubElement(stateVar, "allowedValueRange")
                SubElement(allowed_range, "minimum").text = str(upnp_stateVar.allowedMin)
                SubElement(allowed_range, "maximum").text = str(upnp_stateVar.allowedMax)
                if not upnp_stateVar.allowedStep == None:
                    SubElement(allowed_range, "step").text = str(upnp_stateVar.allowedStep)
        return xmltostring(scpd)
