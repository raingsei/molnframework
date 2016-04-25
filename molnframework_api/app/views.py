"""
Definition of views.
"""

import json
from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest,HttpResponse,HttpResponseBadRequest,JsonResponse
from django.template import RequestContext

from .logic.addlogics import AddComputeServiceLogic, AddComputePodLogic,AddComputePodHealth

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

def register_pod(request):
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

    response = AddComputePodLogic().execute(pod_data)

    return HttpResponse(response,content_type="application/json")

def register_service(request):
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

    service_meta = json.loads(str_json)

    response = AddComputeServiceLogic().execute(service_meta)
    
    return HttpResponse(response,content_type="application/json")
    
   

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'year':datetime.now().year,
        })
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance = RequestContext(request,
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        })
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance = RequestContext(request,
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        })
    )


