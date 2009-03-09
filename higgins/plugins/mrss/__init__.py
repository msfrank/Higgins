import feedparser
from twisted.internet import reactor
from twisted.web import client as httpclient
from higgins.service import Service
from higgins.core.config import Configurator, IntegerSetting

class MRSSConfig(Configurator):
    POLLING_INTERVAL = IntegerSetting('Polling Interval', 3600)

class MRSSService(Service, Loggable):
    log_domain = "mrss"
    url = "http://www.democracynow.org/podcast-video.xml"

    def _parseRss(self, result):
        self.log_debug("parsing RSS")
        try:
            rss = feedparser.parse(result)
            self.log_debug("feed title: %s" % rss.feed.title)
            for entry in rss.feed.entries:
                self.log_debug("feed entry: %s" % entry.title)
            self._handle = reactor.callLater(MRSSConfig.POLLING_INTERVAL, self._getRss)
        except Exception, e:
            self.log_debug("failed to parse RSS: %s" % e)

    def _getRss(self):
        self.log_debug("retrieving RSS from " + self.url)
        d = httpclient.getPage(self.url)
        d.addCallback(self.parseRss)

    def startService(self):
        self._handle = reactor.callLater(MRSSConfig.POLLING_INTERVAL, self._getRss)

    def stopService(self):
        try:
            self._handle.cancel()
        except:
            pass
        return None
