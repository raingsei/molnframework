from datetime import datetime
from molnframework.utils.config import ServiceConfig

class ExecutionResult(object):
    def __init__(self,result,start,end):
        self.start = start
        self.end = end
        self.total = end - start
        self.result = result

