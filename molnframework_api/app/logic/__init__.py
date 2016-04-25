import json
from enum import Enum

class AddComputeServiceExpection(Exception):
    pass

class LogicStatus(Enum):
    DEFAULT = -1
    FAILED = 0
    SUCCESS = 1
    SUCCESS_WITH_WARNINGS = 2

    def __str__(self):
        return str(self.value)

class LogicReturn(object):
    def __init__(self):
        self._message = ""
        self._status = LogicStatus.DEFAULT
        self._code = 0
        self._data = dict()

    def __init__(self,status,message="",code=None,data=dict()):
        self.set_status(status)
        self.set_message(message)
        self.set_code(code)
        self.set_data(data)

    def set_status(self,status):
        self._status = status

    def set_message(self,message):
        assert isinstance(message,str)
        self._message = message

    def set_code (self,code):
        self._code = code

    def set_data(self,data):
        self._data = data


    def to_JSON(self):
        data = dict()
        data['status'] = "%s" % self._status
        data['message'] = self._message
        data['code'] = self._code
        data['data'] = self._data

        return json.dumps(data)

class LogicBase(object):
    def execute(self,instance):
        pass
    def create_logic_success(self,message,data = dict()):
        return LogicReturn(LogicStatus.SUCCESS,message,data=data).to_JSON()
    
    def create_logic_fail(self,message,code):
        return LogicReturn(LogicStatus.FAILED,message,code).to_JSON()

    def create_logic_success_warnings(self,message,code,data = dict()):
        return LogicReturn(LogicStatus.SUCCESS_WITH_WARNINGS,message,code=code,data=data).to_JSON()