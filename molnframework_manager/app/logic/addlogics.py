import datetime

from . import LogicBase, AddComputeServiceExpection
from ..models import ComputeService
from ..models import ComputeApp

class AddServiceLogic(LogicBase):
    """description of class"""

    def execute(self, instance):
        assert isinstance(instance,dict)

        app_name = instance['app_name'] 
        service_name = instance['service_name']
        service_url = instance['service_url']


        # get compute app 
        app = ComputeApp.objects.get(app_name=app_name)
        if app is None:
            raise AddComputeServiceExpection("App - %s is not registered" % app_name)

        exist_service = app.computeservice_set.filter(name=service_name,url=service_url)
        if len(exist_service) != 0:
            raise AddComputeServiceExpection("Service is already existed!")

        app.computeservice_set.create(
            name = service_name,
            url = service_url,
            registered_date= datetime.datetime.utcnow(),
            meta_info= "")










    


