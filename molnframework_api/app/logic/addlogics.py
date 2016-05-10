import datetime

from . import LogicBase
from ..models import ComputeService,ComputePod,ComputeApp,DockerImage

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

class AddComputeAppLogic(LogicBase):

    def execute(self, instance):
        assert isinstance(instance,dict)
        
        user_id = instance['user_id']
        app_name = instance['app_name']
        app_author = instance['app_author']
        app_number_pods = instance['app_number_pods']

        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        exist_app = user.computeapp_set.filter(name=app_name)
        if len (exist_app) != 0:
            return self.create_logic_fail("Application name is already existed!",None)

        data = dict()
        try:
            new_app = user.computeapp_set.create(
                name = app_name,
                author = app_author,
                number_pods = app_number_pods,
                registered_date = datetime.datetime.utcnow())
            data['app_id'] = new_app.id
            data['app_port'] = new_app.port
        except Exception as e:
            return self.create_logic_fail(str(e),None)
        return self.create_logic_success("new app is created",data)

class AddComputePodHealth(LogicBase):

    def execute(self, instance):
        assert isinstance(instance,dict)

        # extract data from instance
        pod_id = instance['pod_id']
        pod_data = instance['pod_data']

        try:
            pod = ComputePod.objects.get(id=pod_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("Pod with id = %s does not exist" % pod_id,None)

        data = dict()
        try:
            total = pod.computepodhealth_set.count()
            if total >= 10:
                pod.computepodhealth_set.all().delete()
                total = 0
            pod.computepodhealth_set.create(data = pod_data)
            data['count'] = total+1
        except Exception as e:
            return self.create_logic_fail(str(e),None)

        return self.create_logic_success("new pod health record is added",data)

class AddComputePodLogic(LogicBase):
   
    def execute(self, instance):
        assert isinstance(instance,dict)

        # extract data from instance
        user_id = instance['user_id']
        app_name = instance['app_name']
        pod_name = instance['pod_name']
        pod_address = instance['pod_address']
        pod_info = instance['pod_info']


        # get user 
        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        # get compute app 
        try:
            app = user.computeapp_set.get(name=app_name)
        except ObjectDoesNotExist:
            return self.create_logic_fail("App - %s is not registered" % app_name,None)

        exist_pod = app.computepod_set.filter(name=pod_name,address=pod_address)
        if len(exist_pod) != 0:
            return self.create_logic_fail("Pod is already existed!",None)
        
        data = dict()
        try:
            new_pod = app.computepod_set.create(
                name = pod_name,
                address = pod_address,
                system_info = pod_info,
                registered_date= datetime.datetime.utcnow())
            data['pod_id'] = new_pod.id
        except Exception as e:
            return self.create_logic_fail(str(e),None)

        return self.create_logic_success("new pod is added",data)

class AddComputeServiceLogic(LogicBase):
    """description of class"""

    def execute(self, instance):
        assert isinstance(instance,dict)

        user_id = instance['user_id']
        app_name = instance['app_name']
        pod_name = instance['pod_name']
        pod_address = instance['pod_address'] 
        service_name = instance['service_name']
        service_url = instance['service_url']
        service_meta = instance['service_parameters']

        # get user 
        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        # get compute app 
        try:
            app = user.computeapp_set.get(name=app_name)
        except ObjectDoesNotExist:
            return self.create_logic_fail("App - %s is not registered" % app_name,None)
        
        # get pod
        try:
            pod = app.computepod_set.get(name=pod_name,address=pod_address)
        except ObjectDoesNotExist:
            return self.create_logic_fail("Pod - %s[%s] is not registered" % (pod_name,pod_address),None)
        
        exist_service = pod.computeservice_set.filter(name=service_name,url=service_url)
        if len(exist_service) != 0:
            return self.create_logic_fail("Service is already existed!",None)

        data = dict()
        try:
            new_service = pod.computeservice_set.create(
                name = service_name,
                url = service_url,
                registered_date= datetime.datetime.utcnow(),
                meta_info= service_meta)
            data['service_id'] = new_service.id
        except Exception as e:
            return self.create_logic_fail(str(e),None)

        return self.create_logic_success("new service is added",data)

class AddDockerImageLogic(LogicBase):
    def execute(self, instance):
        assert isinstance(instance,dict)

        user_id = instance['user_id']
        name = instance['name']
        content = instance['content']
        version = instance['version']


        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        # get docker image
        exist_docker_image = user.dockerimage_set.filter(name=name,version=version)
        if len(exist_docker_image) != 0:
            return self.create_logic_fail("Docker image with the name and version is already existed!",None)

        data = dict()
        try:
            new_docker_image = user.dockerimage_set.create(
                name = name,
                content = content,
                version = version,
                date = datetime.datetime.utcnow())
            data['docker_image_id'] = new_docker_image.id
        except Exception as e:
            return self.create_logic_fail(str(e),None)
        return self.create_logic_success("new docker image content is added",data)












    


