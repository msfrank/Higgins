# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import sys, os
import gobject
import pygst
pygst.require('0.10')
import gst
from twisted.internet.defer import Deferred
from higgins.gst.logger import logger

class MetadataFinder(object):

    def __init__(self, path):
        self._deferred = None
        self._metadata = {}
        # create basic decoding pipeline
        self._pipeline = gst.Pipeline("parse-metadata")
        filesrc = gst.element_factory_make("filesrc", "source")
        decodebin = gst.element_factory_make("decodebin", "decoder")
        self._fakesink = gst.element_factory_make("fakesink", "sink")
        self._pipeline.add(filesrc, decodebin, self._fakesink)
        gst.element_link_many(filesrc, decodebin)
        typefinder = decodebin.get_by_name("typefind")
        typefinder.connect("have-type", self._onHaveType)
        decodebin.connect("new-decoded-pad", self._onNewDecodedPad)
        # set location to parse metadata from
        filesrc.set_property("location", path)
        # get on the bus!
        self._bus = self._pipeline.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self._onMessage)

    def parseMetadata(self):
        """Returns a Deferred which fires once the metadata has been parsed."""
        if not self._pipeline:
            raise Exception("this parser has already been used")
        if self._deferred:
            raise Exception("already running")
        self._deferred = Deferred()
        self._pipeline.set_state(gst.STATE_PLAYING)
        return self._deferred

    def _onHaveType(self, element, probability, caps):
        if self._deferred == None:
            return
        mimetype = caps.to_string()
        logger.log_debug("file has type %s (probability=%s)" % (caps.to_string(), probability))
        self._metadata['mimetype'] = mimetype
        self._metadata['mimetype-probability'] = int(probability)

    def _onNewDecodedPad(self, element, pad, last):
        if self._deferred == None:
            return
        sinkpad = self._fakesink.get_pad("sink")
        if not sinkpad.is_linked():
            pad.link(sinkpad)

    def _onMessage(self, bus, message):
        if self._deferred == None:
            return
        if message.type == gst.MESSAGE_TAG:
            taglist = message.parse_tag()
            for key in taglist.keys():
                self._metadata[key] = taglist[key]
        elif message.type == gst.MESSAGE_EOS:
            from twisted.internet import reactor
            reactor.callLater(0, self._finishParsing)
        elif message.type == gst.MESSAGE_ERROR:
            from twisted.internet import reactor
            error, debug = message.parse_error()
            reactor.callLater(0, self._parsingFailure, error)
        elif message.type == gst.MESSAGE_STATE_CHANGED:
            oldstate,newstate,pending = message.parse_state_changed()
            if newstate != gst.STATE_PLAYING:
                return
            if message.src.get_name() != 'parse-metadata':
                return
            from twisted.internet import reactor
            reactor.callLater(0, self._finishParsing)

    def _finishParsing(self):
        self._pipeline.set_state(gst.STATE_NULL)
        self._fakesink = None
        self._pipeline = None
        self._bus = None
        self._deferred.callback(self._metadata)
        self._deferred = None

    def _parsingFailure(self, message):
        self._pipeline.set_state(gst.STATE_NULL)
        self._fakesink = None
        self._pipeline = None
        self._bus = None
        self._deferred.errback(Exception(message))
        self._deferred = None
