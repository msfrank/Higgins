# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os, sys, gst
from twisted.internet.defer import Deferred
from higgins.http.stream import SimpleStream
from higgins.gst import logger

conversions = {
    'audio/x-wav': {
        'accepts': ['audio/ogg','audio/mpeg'],
        'extension': 'wav',
        'pipeline': 'decodebin ! audioconvert ! audio/x-raw-int,rate=44100,channels=2 ! wavenc'
        },
    'audio/mpeg': {
        'accepts': ['audio/ogg',]
        'extension': 'mp3',
        'pipeline': 'decodebin ! audioconvert ! audio/x-raw-int,rate=44100,channels=2 ! lame name=enc mode=0 ! id3v2mux'
        },
    }

class NoSuchProfile(Exception):
    pass

class TranscodingStream(SimpleStream):

    def __init__(self, path, mimetype, maxBytes=10485760, minBytes=0, drop=False):
        self.length = None
        self._dataAvailable = False
        self._eos = False
        self._deferred = None
        # look up the profile
        try:
            profile = profiles[mimetype]
        except:
            raise NoSuchProfile('No profile to convert %s to %s' % (path,mimetype))
        # create the pipeline from the loaded profile
        self._pipeline = gst.parse_launch(profile['pipeline'])
        elements = self._pipeline.elements()
        head = elements[0]
        tail = elements[-1]
        # create the source element
        self._src = gst.element_factory_make('filesrc')
        self._pipeline.add(self._src)
        gst.element_link_many(self._src, head)
        # create the sink element
        self._queue = gst.element_factory_make('queue')
        self._queue.set_property('max-size-bytes', maxBytes)
        self._queue.set_property('min-threshold-bytes', minBytes)
        if drop:
            self._queue.set_property('leaky', True)
        self._queue.connect('running', self._onStreamRunning)
        self._queue.connect('underrun', self._onStreamEmpty)
        self._sink = gst.element_factory_make('appsink')
        self._sink.connect('eos', self._onStreamEOS)
        self._pipeline.add(self._queue, self._sink)
        gst.element_link_many(self._queue, self._sink)
        tail.connect('pad-added', self._onTailPadAdded)    
        # set the source location and start playing
        src.set_property("location", path)
        self._pipeline.set_state(gst.STATE_PLAYING)
        logger.log_debug("started transcoding %s to a %s stream" % (path, mimetype))

    def _onTailPadAdded(self, tail, src_pad):
        sink_pad = self._queue.get_pad('sink')
        src_pad.link(sink_pad)
        logger.log_debug("linked sink to transcoding pipeline")

    def _onStreamRunning(self, queue):
        self._dataAvailable = True
        logger.log_debug('stream is running')
        if self._deferred:
            buffer = self._sink.emit('pull-buffer')
            if buffer == None:
                self._deferred.callback(None)
            else:
                self._deferred.callback(buffer.data)
            self._deferred = None

    def _onStreamEmpty(self, queue):
        self._dataAvailable = False
        logger.log_debug('stream is empty')

    def _onStreamEOS(self, appsink):
        self._pipeline.set_state(gst.STATE_NULL)
        self._eos = True
        logger.log_debug("finished transcoding stream")

    def read(self):
        if self._eos:
            self._doClose()
            return None
        if not self._dataAvailable:
            self._deferred = Deferred()
            return self._deferred
        buffer = self._sink.emit('pull-buffer')
        if buffer == None:
            return None
        return buffer.data

    def _doClose(self):
        self._pipeline.set_state(gst.STATE_NULL)
        self._dataAvailable = False
        self._eos = True
        if self._deferred:
            self._deferred.callback(None)
        self._deferred = None

    def close(self):
        self._doClose()
        logger.log_debug("closed transcoding stream prematurely")


__all__ = ['NoSuchProfile','TranscodingStream']
