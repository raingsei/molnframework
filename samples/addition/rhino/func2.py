from molnframework.core.service.base import ServiceBase

class TestFunctionService (ServiceBase):

    x = 0.0
    y = 0.0
    z = 0.0

    # service configuration
    
    parameters = ['x','y','z']
    is_single_instance = True
    address='tryme'

    def execute(self):
        return self.x + self.y + self.z


     