# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring
from higgins.upnp.statevar import StateVar
from higgins.upnp.action import Action, InArgument, OutArgument

class DeviceServiceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # load state variables
        stateVars = {}
        for key,object in attrs.items():
            if isinstance(object, StateVar):
                stateVars[key] = object
                object.name = key
        # load actions
        actions = {}
        for key,object in attrs.items():
            if isinstance(object, Action):
                actions[key] = object
                object.name = key
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
        return super(DeviceServiceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class UPNPDeviceService(object):
    __metaclass__ = DeviceServiceDeclarativeParser

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
                SubElement(arg, "relatedStateVariable").text = upnp_arg.related.name
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

    def __str__(self):
        return self.upnp_service_id

# Define the public API
__all__ = ['UPNPDeviceService',]
