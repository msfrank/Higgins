import feedparser
from twisted.internet import reactor
from twisted.web import client as httpclient
from higgins.service import Service
from higgins.logger import Loggable
from higgins.core.configurator import Configurator, IntegerSetting
from higgins.plugins.mrss.feeds import feeds_front

class MRSSConfig(Configurator):
    POLLING_INTERVAL = IntegerSetting('Polling Interval', 3600)

class MRSSService(Service, Loggable):
    log_domain = "mrss"
    pretty_name = "Media RSS"
    description = "Downloads media from RSS feeds"
    configs = MRSSConfig()
    pages = { '': feeds_front }

    url = "http://www.democracynow.org/podcast-video.xml"

    def _parseRss(self, result):
        self.log_debug("parsing RSS")
        try:
            rss = feedparser.parse(result)
            self.log_debug("feed title: %s" % rss.feed.title)
            for entry in rss.entries:
                self.log_debug("\tfeed entry: %s" % entry.title)
                self.log_debug("\t\tupdated: %s" % str(entry.updated))
                self.log_debug("\t\tsummary: %s" % entry.summary)
        except Exception, e:
            self.log_debug("failed to parse RSS: %s" % e)
        self._handle = reactor.callLater(MRSSConfig.POLLING_INTERVAL, self._getRss)

    def _getRss(self):
        self.log_debug("retrieving RSS from " + self.url)
        d = httpclient.getPage(self.url)
        d.addCallback(self._parseRss)

    def startService(self):
        self._handle = None
        self._getRss()
        self.log_debug("starting MRSS service")
        Service.startService(self)

    def stopService(self):
        try:
            self._handle.cancel()
        except:
            pass
        self.log_debug("stopping MRSS service")
        return Service.stopService(self)
