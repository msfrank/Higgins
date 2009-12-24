# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os, sys, gst
from twisted.internet.defer import Deferred
from higgins.http.stream import SimpleStream
from higgins.http.http_headers import MimeType
from higgins.gst.logger import logger

profiles = {
    'audio/x-wav': {
        'accepts': ['audio/ogg','audio/mpeg','application/x-id3'],
        'extension': 'wav',
        'pipeline': 'decodebin ! audioconvert ! audio/x-raw-int,rate=44100,channels=2 ! wavenc'
        },
    'audio/L16': {
        'accepts': ['audio/*'],
        'extension': 'lpcm',
        'pipeline': 'decodebin ! audioconvert ! audio/x-raw-int,rate=44100,endianness=4321,channels=2,width=16,depth=16,signed=true'
        },
    'audio/mpeg': {
        'accepts': ['audio/ogg'],
        'extension': 'mp3',
        'pipeline': 'decodebin ! audioconvert ! audio/x-raw-int,rate=44100,channels=2 ! lame name=enc mode=0 ! id3v2mux'
        },
    }

class ProfileNotFound(Exception):
    pass

class TranscodingStream(SimpleStream):

    def __init__(self, file, requestedMimetype, maxBuffers=None, drop=False):
        self.length = None
        self._eos = False
        # look up the profile
        sourceMimetype = MimeType.fromString(str(file.MIMEType))
        try:
            profile = profiles[requestedMimetype]
        except:
            raise ProfileNotFound('No profile to convert %s to %s' % (file.path, requestedMimetype))
        # check whether profile accepts destination mimetype
        try:
            for dsttype in profile['accepts']:
                mediaType,mediaSubtype = dsttype.split('/', 1)
                if mediaType == '*' and mediaSubtype == '*':
                    raise StopIteration
                if mediaType == sourceMimetype.mediaType and (mediaSubtype == '*' or mediaSubtype == sourceMimetype.mediaSubtype):
                    raise StopIteration
            raise ProfileNotFound('No acceptable profiles found to convert %s to %s' % (file.path, requestedMimetype))
        except StopIteration:
            pass
        self.mimetype = MimeType.fromString(requestedMimetype)
        # create the pipeline from the loaded profile
        self._pipeline = gst.parse_launch("filesrc name=filesrc ! %s ! appsink name=appsink" % profile['pipeline'])
        # find the filesrc element
        filesrc = self._pipeline.get_by_name('filesrc')
        filesrc.set_property("location", file.path)
        # find the sink element
        self._appsink = self._pipeline.get_by_name('appsink')
        if drop == True:
            self._appsink.set_property('drop', True)
        if maxBuffers != None:
            self._appsink.set_property('max-buffers', int(maxBuffers))
        # get on the bus!
        self._bus = self._pipeline.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self._onBusMessage)
        # set the source location and start playing
        self._pipeline.set_state(gst.STATE_PLAYING)
        logger.log_debug("started transcoding %s to a %s stream" % (file.path, requestedMimetype))

    def _onBusMessage(self, bus, message):
        if message.type == gst.MESSAGE_ERROR:
            error, debug = message.parse_error()
            logger.log_warning("_onBusMessage: received stream error from the bus: %s" % error)
            self._eos = True
            return

    def read(self):
        if self._eos or self._appsink.get_property('eos'):
            logger.log_debug("read: appsink reached end-of-stream")
            self._doClose()
            return None
        buffer = self._appsink.emit('pull-buffer')
        if buffer == None:
            logger.log_debug("read: no data available from appsink")
            self._doClose()
            return None
        return buffer.data

    def _doClose(self):
        self._bus.remove_signal_watch()
        self._eos = True
        logger.log_debug("_doClose: cleaning up")
        self._pipeline.set_state(gst.STATE_NULL)

    def close(self):
        logger.log_debug("closed transcoding stream")
        self._doClose()

__all__ = ['TranscodingStream']
