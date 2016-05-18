import time
import random
from molnframework.core.service.base import ServiceBase

class TestFunctionService (ServiceBase):

    x = 0.0
    y = 0.0
    z = 0.0

    # service configuration
    
    parameters = ['x','y','z']
    is_single_instance = False
    address='tryme'

    def execute(self):

        #time.sleep(random.randint(0,3))

        return self.x + self.y + self.z


     