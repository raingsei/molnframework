from datetime import datetime
from molnframework.utils.config import ServiceConfig

class ExecutionResult(object):
    def __init__(self,result,start,end):
        self.start = start
        self.end = end
        self.total = end - start
        self.result = result

class ServiceExecutionResult(object):
    def __init__(self,status="Unknown",message="",result=None):
        self.status = status
        self.result = result
        self.message = message

    def set_execution_time(self,start,end):
        self.start = str(start)
        self.end = str(end)

class ServiceExecutionResultError(ServiceExecutionResult):
    def __init__(self,message):
        super(ServiceExecutionResultError,self).__init__("Error", message)

class ServiceExecutionResultOK(ServiceExecutionResult):
    def __init__(self,message="",result=None):
        super(ServiceExecutionResultOK,self).__init__("OK",message,result)

