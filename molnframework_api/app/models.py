"""
Definition of models.
"""

from django.db import models

class ComputeApp (models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    registered_date = models.DateTimeField('date registered')
    number_pods = models.IntegerField(default=0)

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




