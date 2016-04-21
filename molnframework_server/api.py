import json
from django.http import HttpResponse

def get_status(request):
    
    status = dict()
    status['status']="OK"

    return HttpResponse(json.dumps(status)) 