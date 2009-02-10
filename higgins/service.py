from twisted.application.service import Service as TwistedService

class Service(TwistedService):
    pretty_name = None
    description = None
    configs = None

    def __init__(self):
        pass

    def startService(self):
        TwistedService.startService(self)

    def stopService(self):
        TwistedService.stopService(self)
