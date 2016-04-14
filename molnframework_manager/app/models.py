"""
Definition of models.
"""

from django.db import models

class ComputeApp (models.Model):
    app_name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    registered_date = models.DateTimeField('date registered')
    number_pods = models.IntegerField(default=0)
    
class ComputeService(models.Model):
    compute_app = models.ForeignKey(ComputeApp,on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    url = models.URLField(max_length=2000)
    registered_date = models.DateTimeField('date registered')
    meta_info = models.CharField(max_length=5000)




