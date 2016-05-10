import datetime
import os
from docker import Client
from string import Template

from . import LogicBase
from ..models import ComputeService,ComputePod,ComputeApp,DockerImage

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User


class BeginBuidDockerImageLogic(LogicBase):

    def execute(self, instance):
        assert isinstance(instance,dict)

        user_id = instance['user_id']
        docker_image_id = instance['docker_image_id']
        docker_registry = instance['docker_registry']
        docker_client = instance['docker_client']

        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        try:
            docker_image = user.dockerimage_set.get(pk=docker_image_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("docker image with id [%s] does not exist" % docker_image_id,None)

        # build docker image name
        image_name = "%s/%s/%s:%s" % (docker_registry,user.username,docker_image.name,docker_image.version)
        try:
            dc = Client(docker_client)
            dc_images = dc.images()
        except:
            return self.create_logic_fail("Unable to connect to docker registry at %s" % docker_registry, None)

        if docker_image.build_status != "NB":
            if docker_image.build_status == "ERR":
                return self.create_logic_fail("docker image has already built with errors",None)
            elif docker_image.build_status == "OK":
                for img in dc_images:
                    for tag in img['RepoTags']:
                        if tag == image_name:
                            break
                return  self.create_logic_fail("The docker image was already built!", None)
                
        return self.create_logic_success("Docker image is ready to build!",None)

class EndBuildDockerImageLogic(LogicBase):
    def execute(self, instance):
        assert isinstance(instance,dict)

        user_id = instance['user_id']
        docker_image_error = instance["docker_image_error"]
        docker_image_error_message = instance["docker_image_error_message"]
        docker_image_id = instance['docker_image_id']
        docker_registry = instance['docker_registry']
        docker_client = instance['docker_client']

        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        try:
            docker_image = user.dockerimage_set.get(pk=docker_image_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("docker image with id [%s] does not exist" % docker_image_id,None)

        if docker_image_error == "True":
            docker_image.build_status = "ERR"
            docker_image.build_date = datetime.datetime.utcnow()
            docker_image.build_output = docker_image_error_message
            docker_image.save()

            return self.create_logic_success("End docker image build",None)
        else:
            # build docker image name
            image_name = "%s/%s/%s:%s" % (docker_registry,user.username,docker_image.name,docker_image.version)

            try:
                dc = Client(docker_client)
                dc_images = dc.images()
            except:
                return self.create_logic_fail("Unable to connect to docker registry at %s" % docker_registry, None)

            image_found = False
            for img in dc_images:
                for tag in img['RepoTags']:
                    if tag == image_name:
                        image_found = True
                        break

            if not image_found:
                return self.create_logic_fail("Build has completed but the system is unable to locate the image",None)
            else:
                docker_image.build_status = "OK"
                docker_image.build_date = datetime.datetime.utcnow()
                docker_image.save()

                return self.create_logic_success("End docker image build",None)

class BeginPushDockerImageLogic(LogicBase):
    def execute(self, instance):
        assert isinstance(instance,dict)

        user_id = instance['user_id']
        docker_image_id = instance['docker_image_id']
        docker_registry = instance['docker_registry']
        docker_client = instance['docker_client']

        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        try:
            docker_image = user.dockerimage_set.get(pk=docker_image_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("docker image with id [%s] does not exist" % docker_image_id,None)

        if docker_image.build_status != "OK":
            return self.create_logic_fail("Docker image has not built or there was an error with the build!" % docker_image_id,None)

        # verify that the image exist in the docker system
        image_name = "%s/%s/%s:%s" % (docker_registry,user.username,docker_image.name,docker_image.version)

        try:
            dc = Client(docker_client)
            dc_images = dc.images()

            image_found = False
            for img in dc_images:
                for tag in img['RepoTags']:
                    if tag == image_name:
                        image_found = True
                        break

            if not image_found:
                return self.create_logic_fail("Cannot find image to push",None)
            return self.create_logic_success("Docker image is ready to push!",None) 
        except:
            return self.create_logic_fail("Unable to connect to docker registry at %s" % docker_registry, None)

class EndPushDockerImageLogic(LogicBase):
    def execute(self, instance):
        assert isinstance(instance,dict)

        user_id = instance['user_id']
        docker_image_push_error = instance["docker_image_push_error"]
        docker_image_id = instance['docker_image_id']
        docker_registry = instance['docker_registry']
        docker_client = instance['docker_client']

        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        try:
            docker_image = user.dockerimage_set.get(pk=docker_image_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("docker image with id [%s] does not exist" % docker_image_id,None)

        if docker_image_push_error == "True":
            docker_image.push_status = "ERR"
        else:
            docker_image.push_status = "P"

        docker_image.push_date = datetime.datetime.utcnow()
        docker_image.save()

        return self.create_logic_success("End docker image push",None)

class CreateComputeAppLogic(LogicBase):

    def execute(self, instance):

        assert isinstance(instance,dict)
        
        user_id = instance['user_id']
        app_name = instance['app_name']
        app_author = instance['app_author']
        app_number_pods = instance['app_number_pods']
        docker_image_name = instance['docker_image_name']
        docker_registry = instance['docker_registry']
        external_IP = instance['external_IP']
        base_dir = instance['base_dir']

        # verify user
        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return self.create_logic_fail("User - %s is not registered" % user_id,None)

        # verify app
        exist_app = user.computeapp_set.filter(name=app_name)
        if len (exist_app) != 0:
            return self.create_logic_fail("Application name is already existed!",None)

        # append local registry address
        docker_image_name_local = "%s/%s/%s" % (docker_registry,user.username,docker_image_name)

        # verify docker image
        docker_image = None
        for dck in user.dockerimage_set.all():
            img_name = "%s/%s/%s:%s" % (docker_registry,user.username,dck.name,dck.version)
            if img_name == docker_image_name_local:
                docker_image = dck
                break
        if docker_image == None:
            return self.create_logic_fail("docker image name = %s does not exist" % docker_image_name,None)

        if docker_image.build_status != "OK":
            return self.create_logic_fail("docker image name = %s has not been built propery!" % docker_image_name,None)

        if docker_image.push_status != "P":
            return self.create_logic_fail("docker image name = %s has not been pushed to the registry yet!" % docker_image_name,None)

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

        # load kubernetes template file

        try:

            tpath = os.path.join(base_dir,"app","template","kube_app_template.txt")
            with open(tpath) as f:
                lines = f.readlines()
            content = "".join(line for line in lines)
            kub_template = Template(content)
            kub_app = kub_template.substitute(
                full_app_name="%s-%s" % (user.username,app_name),
                number_of_pods=str(app_number_pods),
                docker_image_name=docker_image_name_local,
                app_port=str(new_app.port),
                external_IP=external_IP)

            kube_error = False
            # run kubernetes commands
            
            if kube_error:
                raise Exception("Error while running kubernetes command!")
        

            # uppdate app status 

            new_app.kube_app = kub_app
            new_app.kube_status = "OK"
            new_app.save()

            # store kube app
            data['kube_app'] = kub_app

        except Exception as e:

            # delete the app record
            new_app.delete()

            # return fail logic
            return self.create_logic_fail(str(e),None)

        # return success logic
        return self.create_logic_success("A new app has successfully created",data)



