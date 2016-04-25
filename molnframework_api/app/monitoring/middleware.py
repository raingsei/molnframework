from . import monitor


class MonitorServiceMiddleware(object):

    def process_request(self,request):
        
        if not monitor.has_started:
            monitor.start()
        
        return None
