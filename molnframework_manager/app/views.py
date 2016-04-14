"""
Definition of views.
"""

import json
from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest,HttpResponse,HttpResponseBadRequest
from django.template import RequestContext

from .logic.addlogics import AddServiceLogic


def register(request):
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

    AddServiceLogic().execute(service_meta)


    return HttpResponse("")
    
   

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


