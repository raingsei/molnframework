
from . import LogicBase
from ..models import ComputeService,ComputePod,ComputeApp

class GetAppResourcesLogic(LogicBase):

    def execute(self, instance):
        assert isinstance(instance,dict)

        app_name = instance['app_name']

        try:
            app = ComputeApp.objects.get(name=app_name)
        except ObjectDoesNotExist:
            return self.create_logic_fail("App [%s] does not exist" % app_name,None)

        pods = app.computepod_set.all()
        pod_list = list()
        for pod in pods:
            pod_dict = dict()
            pod_dict['name'] = pod.name
            pod_dict['address'] = pod.address
            pod_dict['system_info'] = pod.system_info
            pod_dict['registered_date'] = str(pod.registered_date)

            services = pod.computeservice_set.all()
            services_lst = list()
            for service in services:
                service_dict = dict()
                service_dict['name'] = service.name
                service_dict['url'] = service.url
                service_dict['registered_date'] = str(service.registered_date)
                service_dict['meta_info'] = service.meta_info
                services_lst.append(service_dict)
            pod_dict['services'] = services_lst
            pod_list.append(pod_dict)

        app_dict = dict()
        app_dict['name'] = app.name
        app_dict['author'] = app.author
        app_dict['registered_date'] = str(app.registered_date)
        app_dict['number_pods'] = app.number_pods
        app_dict['pods'] = pod_list

        return self.create_logic_success("get app resource",app_dict)

