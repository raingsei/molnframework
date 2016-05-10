"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class ComputeApp (models.Model):

    KUBE_STATUS = (
        ('NC','NOT CREATED'),
        ('C','CREATED'),
        ('ERR','ERROR')
    )

    def generate_port():

        all_ports = list(range(settings.START_APP_PORT,settings.END_APP_PORT))
        used_ports = ComputeApp.objects.values_list('port',flat=True).order_by('port')

        for pt in used_ports:
            all_ports.remove(pt)

        if len(all_ports) == 0:
            raise Exception("All ports are used! Application can no longer host any app!")
        
        return all_ports[0]

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    registered_date = models.DateTimeField('date registered')
    port = models.IntegerField(unique=True,default=generate_port,editable=False)
    number_pods = models.IntegerField(default=0)
    kube_app = models.CharField(max_length=200000,default="")
    kube_status = models.CharField(max_length=200,choices=KUBE_STATUS,default="NC")

    def __str__(self):
        return self.name



        
class ComputePod(models.Model):
    compute_app = models.ForeignKey(ComputeApp,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.URLField(max_length=2000)
    system_info = models.CharField(max_length=2000)
    registered_date = models.DateTimeField('date registered')

    def __str__(self):
        return self.name

class ComputePodHealth(models.Model):
    compute_pod = models.ForeignKey(ComputePod,on_delete=models.CASCADE)
    data = models.CharField(max_length=2000)
    
class ComputeService(models.Model):
    compute_pod = models.ForeignKey(ComputePod,on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    url = models.URLField(max_length=2000)
    registered_date = models.DateTimeField('date registered')
    meta_info = models.CharField(max_length=5000)

    def __str__(self):
        return self.name

class DockerImage(models.Model):
    BUILD_STATUS = (
        ('NB','NOT BUILD'),
        ('OK','OK'),
        ('ERR','ERROR')
    )
    PUSH_STATUS = (
        ('NP','NOT PUSH'),
        ('ERR','ERROR'),
        ('P','PUSHED')
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    content = models.CharField(max_length=2000)
    version = models.CharField(max_length=200)
    date = models.DateTimeField('date')
    build_status = models.CharField(max_length=200,choices=BUILD_STATUS,default="NB")
    build_output = models.CharField(max_length=200000,null=True,blank=True)
    build_date = models.DateTimeField('build date',null=True,blank=True)
    push_status = models.CharField(max_length=200,choices=PUSH_STATUS,default="NP")
    push_date = models.DateTimeField('push date',null=True,blank=True)






