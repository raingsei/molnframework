from molnframework.utils import attribute
from molnframework.utils.config import ServiceConfig



class ServiceDefault (object):
    Defaults =  {
        "is_single_instance":False,
        "serialize_type":"json",
    }

class ServiceBase(ServiceConfig):
    
    def __init__(self,service_name,service_module):
        
        # get user defined attributes and their values
        default_attrs = attribute.get_user_defined_attributes(self) 

        # invoke super class constructor
        super(ServiceBase,self).__init__(service_name,service_module)
        
        # set service base default attributes
        self.__dict__.update(ServiceDefault.Defaults)

        # update the value of the attributes
        self.__dict__.update(default_attrs)


    def execute(self):
        """ 
        Main method for a function service to get executed
        """

        raise NotImplementedError("Implementation should be in the child class.")

    def clean_up(self):
        """ 
        Method is called to clean up after every calculation
        """

        raise NotImplementedError("Implementation should be in the child class.")

    @property
    def parameter_count(self):
        if not hasattr(self,'parameters'):
            return 0
        return len(self.parameters)

