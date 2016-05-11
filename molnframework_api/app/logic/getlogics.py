
from . import LogicBase
from ..models import ComputeService,ComputePod,ComputeApp
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class GetAppResourcesLogic(LogicBase):

    def execute(self, instance):
        assert isinstance(instance,dict)

        user_id = instance['user_id']
        app_name = instance['app_name']
        kubernetes_cluster = instance['kubernetes_cluster']
        external_ip = instance['external_ip']

        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        # get compute app 
        try:
            app = user.computeapp_set.get(name=app_name)
        except ObjectDoesNotExist:
            return self.create_logic_fail("App - %s is not registered" % app_name,None)

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

                if kubernetes_cluster:
                    service_dict['url'] = "http://%s:%s/%s/" % (external_ip,str(app.port),service.name)
                else:
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

class GetDockerImageLogic(LogicBase):

    def execute(self, instance):
        assert isinstance(instance,dict)

        user_id = instance['user_id']
        docker_image_id = instance['docker_image_id']

        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        try:
            docker_image = user.dockerimage_set.get(pk=docker_image_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("docker image with id [%s] does not exist" % docker_image_id,None)

        outdata = dict()
        outdata['user'] = user.username
        outdata['name'] = docker_image.name
        outdata['content'] = docker_image.content
        outdata['version'] = docker_image.version
        outdata['date'] = str(docker_image.date)
        outdata['build_status'] = docker_image.build_status
        outdata['build_output'] = docker_image.build_output
        outdata['build_date'] = str(docker_image.build_date)
        outdata['push_status'] = docker_image.push_status
        outdata['push_date'] = str(docker_image.push_date)

        return self.create_logic_success("get docker image",outdata)
