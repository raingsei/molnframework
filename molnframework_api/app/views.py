"""
Definition of views.
"""

import json
from docker import Client
from io import BytesIO
from datetime import datetime
from docker import Client
from django.shortcuts import render
from django.http import HttpRequest,HttpResponse,HttpResponseBadRequest,JsonResponse,StreamingHttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .logic import LogicReturn,LogicStatus
from .logic.addlogics import (AddComputeServiceLogic, 
    AddComputePodLogic,AddComputePodHealth,
    AddDockerImageLogic,AddComputeAppLogic)
from .logic.getlogics import (
    GetAppResourcesLogic, GetDockerImageLogic)

from .logic.mixedlogics import (
    BeginBuidDockerImageLogic,EndBuildDockerImageLogic,
    BeginPushDockerImageLogic,EndPushDockerImageLogic,
    CreateComputeAppLogic)

def parse_post_json_request(request):
    assert isinstance(request, HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        raise Exception("request must be POST method")

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except:
        raise Exception("Cannot parse post json request")
    return json.loads(str_json)

def report_pod_health(request):

    #response = None

    #try:
    #    # parse json data
    #    data = parse_post_json_request(request)

    #    # add new health record
    #    response = AddComputePodHealth().execute(data)
    #except Exception as e:
    #    return HttpResponseBadRequest()

    assert isinstance(request, HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except:
        return HttpResponseBadRequest()

    pod_data = json.loads(str_json)
    response = AddComputePodHealth().execute(pod_data)

    return HttpResponse(response,content_type="application/json")

@login_required
def register_pod(request):
    #assert isinstance(request, HttpRequest)

    #if not request.user.is_authenticated():
    #    return HttpResponseBadRequest()

    ## filter other type of request
    #if request.method != "POST" and request.POST:
    #    return HttpResponseBadRequest()

    ## dummy check just to supress the error when
    ## accesing POST directly, that is Django's pitfall
    #if len(request.POST) == 0:
    #    pass

    #str_json = ""
    #try:
    #    str_json = request.body.decode("utf-8")
    #except:
    #    return HttpResponseBadRequest()

    #a_data = json.loads(str_json)
    #pod_data = json.loads(a_data)

    data = extract_post_request(request)
    pod_data = json.loads(data)
    pod_data['user_id'] = request.user.id

    response = AddComputePodLogic().execute(pod_data)

    return HttpResponse(response,content_type="application/json")

def register_service(request):
    #assert isinstance(request, HttpRequest) 

    ## filter other type of request
    #if request.method != "POST" and request.POST:
    #    return HttpResponseBadRequest()

    ## dummy check just to supress the error when
    ## accesing POST directly, that is Django's pitfall
    #if len(request.POST) == 0:
    #    pass

    #str_json = ""
    #try:
    #    str_json = request.body.decode("utf-8")
    #except:
    #    return HttpResponseBadRequest()

    data = extract_post_request(request)
    service_meta = json.loads(data)
    service_meta['user_id'] = request.user.id
    response = AddComputeServiceLogic().execute(service_meta)
    
    return HttpResponse(response,content_type="application/json")
    
def get_app_resources(request):
    assert isinstance(request, HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except:
        return HttpResponseBadRequest()

    app_data = json.loads(str_json)

    response = GetAppResourcesLogic().execute(app_data)

    return HttpResponse(response,content_type="application/json")



import time
import csv

class Echo(object):
    def write(self, value):
        time.sleep(1)
        return value

#def test(request):

#    rows = (["Row {}".format(idx), str(idx)] for idx in range(50))
#    pseudo_buffer = Echo()
#    writer = csv.writer(pseudo_buffer)
#    response = StreamingHttpResponse((writer.writerow(row) for row in rows))

#    return response

#    #cli = Client("http://130.238.29.188:2375")
    
#    #dockerfile = '''
#    #FROM busybox:buildroot-2014.02
#    #MAINTAINER first last, first.last@yourdomain.com
#    #VOLUME /data
#    #CMD ["/bin/sh"]

#    #'''
#    #f = BytesIO(dockerfile.encode('utf-8'))

#    #return StreamingHttpResponse(line for line in cli.build(fileobj=f, rm=True, tag='yourname/volume'))

@login_required
def add_docker_image(request):
    assert isinstance(request, HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    add_docker_data = json.loads(str_json)
    add_docker_data['user_id'] = request.user.id

    response = AddDockerImageLogic().execute(add_docker_data)

    return HttpResponse(response,content_type="application/json")

@login_required
def get_docker_image(request):
    assert isinstance(request,HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    indata = json.loads(str_json)
    indata['user_id'] = request.user.id

    # run logic
    response  = GetDockerImageLogic().execute(indata)
    
    return HttpResponse(response,content_type="application/json")

@login_required
def begin_build_docker_image(request):
    assert isinstance(request,HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    indata = json.loads(str_json)
    indata['user_id'] = request.user.id

    if settings.DOCKER_SINGLE_HOST == True:
        indata['docker_registry'] = "127.0.0.1:5000"
    else:
        indata['docker_registry'] = settings.DOCKER_REGISTRY

    indata['docker_client'] = settings.DOCKER_CLIENT

    # run logic
    response = BeginBuidDockerImageLogic().execute(indata)

    return HttpResponse(response,content_type="application/json")

@login_required
def build_docker_image(request):
    assert isinstance(request,HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    indata = json.loads(str_json)
    indata['user_id'] = request.user.id

    get_resp = json.loads(GetDockerImageLogic().execute(indata))
    docker_image = get_resp['data']

    try:
        cl = Client(settings.DOCKER_CLIENT)
        f = BytesIO(docker_image['content'].encode('utf-8'))

        if settings.DOCKER_SINGLE_HOST == True:
            image_tag = "%s/%s/%s:%s" % ("127.0.0.1:5000",docker_image['user'],docker_image['name'],docker_image['version'])
        else:
            image_tag = "%s/%s/%s:%s" % (settings.DOCKER_REGISTRY,docker_image['user'],docker_image['name'],docker_image['version'])

        return StreamingHttpResponse(output for output in cl.build(fileobj=f, rm=True, tag=image_tag))

    except Exception as e:
        res = LogicReturn(LogicStatus.FAILED,str(e))
        return HttpResponse(res.to_JSON(), content_type="application/json")

@login_required
def end_build_docker_image(request):
    assert isinstance(request,HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    indata = json.loads(str_json)
    indata['user_id'] = request.user.id
    if settings.DOCKER_SINGLE_HOST == True:
        indata['docker_registry'] = "127.0.0.1:5000"
    else:
        indata['docker_registry'] = settings.DOCKER_REGISTRY
    indata['docker_client'] = settings.DOCKER_CLIENT

    # run logic
    response = EndBuildDockerImageLogic().execute(indata)

    return HttpResponse(response,content_type="application/json")

@login_required
def begin_push_docker_image(request):
    assert isinstance(request,HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    indata = json.loads(str_json)
    indata['user_id'] = request.user.id
    if settings.DOCKER_SINGLE_HOST == True:
        indata['docker_registry'] = "127.0.0.1:5000"
    else:
        indata['docker_registry'] = settings.DOCKER_REGISTRY
    indata['docker_client'] = settings.DOCKER_CLIENT

    # run logic
    response = BeginPushDockerImageLogic().execute(indata)

    return HttpResponse(response,content_type="application/json")

@login_required
def push_docker_image(request):
    assert isinstance(request,HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    indata = json.loads(str_json)
    indata['user_id'] = request.user.id

    get_resp = json.loads(GetDockerImageLogic().execute(indata))
    docker_image = get_resp['data']

    try:
        cl = Client(settings.DOCKER_CLIENT)
        
        if settings.DOCKER_SINGLE_HOST == True:
            image_tag = "%s/%s/%s:%s" % ("127.0.0.1:5000",docker_image['user'],docker_image['name'],docker_image['version'])
        else:
            image_tag = "%s/%s/%s:%s" % (settings.DOCKER_REGISTRY,docker_image['user'],docker_image['name'],docker_image['version'])

        return StreamingHttpResponse(output for output in cl.push(image_tag, stream=True,insecure_registry=True))

    except Exception as e:
        res = LogicReturn(LogicStatus.FAILED,str(e))
        return HttpResponse(res.to_JSON(), content_type="application/json")

@login_required
def end_push_docker_image(request):
    assert isinstance(request,HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    indata = json.loads(str_json)
    indata['user_id'] = request.user.id
    if settings.DOCKER_SINGLE_HOST == True:
        indata['docker_registry'] = "127.0.0.1:5000"
    else:
        indata['docker_registry'] = settings.DOCKER_REGISTRY
    indata['docker_client'] = settings.DOCKER_CLIENT

    # run logic
    response = EndPushDockerImageLogic().execute(indata)

    return HttpResponse(response,content_type="application/json")

@login_required
def add_compute_app(request):
    assert isinstance(request, HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    indata = json.loads(str_json)
    indata['user_id'] = request.user.id

    response = AddComputeAppLogic().execute(indata)

    return HttpResponse(response,content_type="application/json")


def extract_post_request(request):
    assert isinstance(request, HttpRequest)

    # filter other type of request
    if request.method != "POST" and request.POST:
        return HttpResponseBadRequest()

    # dummy check just to supress the error when
    # accesing POST directly, that is Django's pitfall
    if len(request.POST) == 0:
        pass

    str_json = ""
    try:
        str_json = request.body.decode("utf-8")
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    return json.loads(str_json)

@login_required
def create_compute_app(request):
    indata = extract_post_request(request)

    # add more data
    indata['user_id'] = request.user.id
    indata['docker_registry'] = settings.DOCKER_REGISTRY
    indata['external_IP'] = settings.EXTERNAL_IP
    indata['base_dir'] = settings.BASE_DIR

    response = CreateComputeAppLogic().execute(indata)

    return HttpResponse(response,content_type="application/json")





                                                   