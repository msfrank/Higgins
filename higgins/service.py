from twisted.application.service import Service as TwistedService

class Service(TwistedService):
    service_name = None
    service_description = None
    service_config = None
    entry_points = {}

    def __init__(self):
        pass

    def startService(self):
        TwistedService.startService(self)

    def stopService(self):
        TwistedService.stopService()
