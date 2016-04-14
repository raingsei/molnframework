from  enum import Enum

from molnframework.utils.config import ServiceConfig
from molnframework.core.service.base import ServiceBase



class ParameterMissingException(Exception):
    pass

class ParameterMetaParsingException(Exception):
    pass

class ParameterType (Enum):
    Double = 0
    Integer = 1
    String = 2

    def __str__(self):
        if self is ParameterType.Double:
            return "Double"
        elif self is ParameterType.Integer:
            return "Integer"
        elif self is ParameterType.String:
            return "String"
        else:
            raise NotImplementedError()


def get_parameter_type(parameter):

    if isinstance(parameter,int):
        return ParameterType.Integer
    elif isinstance(parameter,float):
        return ParameterType.Double
    elif isinstance(parameter,str):
        return ParameterType.String
    else:
        raise NotImplementedError("Parameter type is not supported")

class ParameterInfo (object):
    def __init__(self,name,type):

        assert isinstance(name,str)
        assert isinstance(type,ParameterType)

        self.name = name
        self.type = type

    def __repr__(self, **kwargs):
        return "%s:%s" % (self.name,self.type)
    def __str__(self, **kwargs):
        return "%s:%s" % (self.name,self.type)

class ParameterMeta (object):
    def __init__(self,data):

        self.data = list()
        if data is not None and isinstance(data,list):
            for item in data:
                if not isinstance(item,ParameterInfo):
                    raise ValueError("Invalid data item! They must be ParameterInfo")
            self.data = data

    def __iter__(self):
        return self.data.__iter__()

    def count(self):
        return len(self.data)
    
    @classmethod
    def get_meta(cls,service_instance):
        
        if not isinstance(service_instance,ServiceConfig):
            raise ValueError("service_instance must be of type ServiceBase")

        data = list()

        # TODO 
        # Modify to support function based service

        if isinstance(service_instance,ServiceBase):
            if service_instance.parameter_count != 0:

                for param_name in service_instance.parameters:
                    if not hasattr(service_instance,param_name):
                        raise ParameterMissingException("There is no parameter called %s" % param_name)
                
                    parameter_type = get_parameter_type(getattr(service_instance,param_name))
                    meta_item = ParameterInfo(param_name,parameter_type)
                    data.append(meta_item)
        return cls(data)

    @classmethod
    def parse_values(cls,service,meta,values):
        assert len(meta.data) == len(values)

        for idx in range(0, len(values)):
            p_item = meta.data[idx]

            if not hasattr(service,p_item.name):
                raise ParameterMetaParsingException(
                    "Error parse value to %s" % p_item.name)
            setattr(service,p_item.name,values[idx])


class SweepParameter (object):
    def __init__(self, min,max,value):
        self.min = min
        self.max = max
        self.value = value
