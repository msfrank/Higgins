from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring

class StateVar:
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

    def __init__(self, type, **params):
        self.type = type
        self.params = params
    def parse(self, text_value):
        pass

class Argument:
    DIRECTION_IN = "in"
    DIRECTION_OUT = "out"
    def __init__(self, name, direction, related, retval=False):
        self.name = name
        if not direction == Argument.DIRECTION_IN and not direction == Argument.DIRECTION_OUT:
            raise Exception("argument direction must be 'in' or 'out'")
        self.direction = direction
        self.related = related
        self.retval = retval

class Action:
    def __init__(self, action, *args):
        self.action = action
        self.in_args = []
        self.out_args = []
        for arg in args:
            if arg.direction == Argument.DIRECTION_IN:
                self.in_args.append(arg)
            else:
                self.out_args.append(arg)
    def __call__(self, service, arguments):
        return self.action(service, *arguments)

class ServiceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # load state variables
        stateVars = {}
        for name,object in attrs.items():
            if isinstance(object, StateVar):
                stateVars[name] = object
        # load actions
        actions = {}
        for name,object in attrs.items():
            if isinstance(object, Service):
                actions[name] = object
        # load stateVars and actions from any base classes
        for base in bases:
            if hasattr(base, '_upnp_stateVars'):
                stateVars.update(base._upnp_stateVars)
            if hasattr(base, '_upnp_actions'):
                actions.update(base.upnp_actions)
        attrs['_upnp_stateVars'] = stateVars
        attrs['_upnp_actions'] = actions
        return super(DeviceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class Service:
    __metaclass__ = ServiceDeclarativeParser

    upnp_service_type = None
    upnp_service_id = None

    def __repr__(self):
        scpd = Element("{urn:schemas-upnp-org:service-1-0}scpd")
        version = SubElement(scpd, "specVersion")
        SubElement(version, "major").text = "1"
        SubElement(version, "minor").text = "0"
        action_list = SubElement(scpd, "actionList")
        for upnp_action in self._upnp_actions:
            action = SubElement(action_list, "action")
            SubElement(action, "name").text = upnp_action.name
            arg_list = SubElement(action, "argumentList")
            for upnp_arg in upnp_action.args:
                arg = SubElement(arg_list, "name").text = upnp_arg.name
                SubElement(arg, "direction").text = upnp_arg.direction
                SubElement(arg, "relatedStateVariable").text = upnp_arg.related
                if upnp_arg.retval:
                    SubElement(arg, "retval")
        var_list = SubElement(scpd, "serviceStateTable")
        for upnp_stateVar in self._upnp_stateVars:
            stateVar = SubElement(var_list, "stateVariable")
            SubElement(stateVar, "name").text = upnp_stateVar.name
            SubElement(stateVar, "dataType").text = upnp_stateVar.type
            if upnp_stateVar.defaultValue:
                SubElement(stateVar, "defaultValue").text = upnp_stateVar.defaultValue
            if upnp_stateVar.allowedValues:
                allowed_list = SubElement(stateVar, "allowedValueList")
                for allowed in upnp_stateVar.allowedValues:
                    SubElement(allowed_list, "allowedValue").text = allowed
            if upnp_stateVar.allowedValueRange:
                allowed_range = SubElement(stateVar, "allowedValueRange")
                SubElement(allowed_range, "minimum").text = str(upnp_stateVar.allowedValueRange[0])
                SubElement(allowed_range, "maximum").text = str(upnp_stateVar.allowedValueRange[1])
                if len(upnp_stateVar.allowedValueRange) > 2:
                    SubElement(allowed_range, "step").text = str(upnp_stateVar.allowedValueRange[2])
        return xmltostring(root)
