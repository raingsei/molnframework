import threading
from molnframework.utils.client import Client

class HealthReport (object):

    REPORT_TIME = 10

    def __init__(self,url):
        self._url = url
        self._worker = None
        self._event = None
        self._has_started = False

    def _build_report(self):
        pass

    def _report(self):

        while not self._event.isSet():
            self._event.wait(HealthReport.REPORT_TIME)

        self._event.clear()


    def start(self):

        if self._has_started:
            return

        self._event = threading.Event()
        self._worker = threading.Thread(target = self._report)
        self._worker.start()
        self._has_started = true

    def stop(self):

        if not self._has_started and self._event.isSet():
            return

        self._event.set()
        self._has_started = false