# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.upnp.statevar import StateVar
from higgins.upnp.logger import logger

class Argument(object):
    DIRECTION_IN = "in"
    DIRECTION_OUT = "out"
    def __init__(self, name, direction, related, retval=False):
        self.name = name
        if not direction == Argument.DIRECTION_IN and not direction == Argument.DIRECTION_OUT:
            raise Exception("argument direction must be 'in' or 'out'")
        self.direction = direction
        if not isinstance(related, StateVar):
            raise Exception("related variable for %s is not a StateVar" % name)
        self.related = related
        self.type = related.type
        self.retval = retval
    def parse(self, value):
        return self.related.parse(value)
    def write(self, value):
        return self.related.write(value)

class InArgument(Argument):
    def __init__(self, name, related, retval=False):
        Argument.__init__(self, name, Argument.DIRECTION_IN, related, retval)

class OutArgument(Argument):
    def __init__(self, name, related, retval=False):
        Argument.__init__(self, name, Argument.DIRECTION_OUT, related, retval)

class Action(object):
    def __init__(self, action, *args):
        if not callable(action):
            raise Exception("Action is not callable")
        self.action = action
        self.in_args = []
        self.out_args = []
        for arg in args:
            if arg.direction == Argument.DIRECTION_IN:
                self.in_args.append(arg)
            else:
                self.out_args.append(arg)
    def __call__(self, request, service, arguments):
        # arguments is a dict.  key is the argument name, value is
        # the argument value as a string.
        a = self.in_args[:]
        parsed_args = []
        while not a == []:
            arg = a.pop(0)
            try:
                arg_value = arguments[arg.name]
                parsed_value = arg.parse(arg_value)
                logger.log_debug("parsed %s: '%s' => %s" % (arg.name,arg_value,parsed_value))
                parsed_args.append(parsed_value)
            except KeyError:
                raise Exception("missing required InArgument %s" % arg.name)
            except Exception, e:
                raise e
        out_args = self.action(service, request, *parsed_args)
        a = self.out_args[:]
        parsed_args = []
        while not a == []:
            arg = a.pop(0)
            try:
                arg_value = out_args[arg.name]
                parsed_value = arg.write(arg_value)
                logger.log_debug("wrote %s: '%s' => %s" % (arg.name,arg_value,parsed_value))
                parsed_args.append((arg.name, arg.type, parsed_value))
            except KeyError:
                raise Exception("missing required OutArgument %s" % arg.name)
            except Exception, e:
                raise e
        return parsed_args

__all__ = ['Action', 'InArgument', 'OutArgument']
