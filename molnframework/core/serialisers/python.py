from collections import OrderedDict

import molnframework.utils.attribute
from molnframework.core.serialisers import base
  

class Serialiser(base.Serialiser):

    def start_serialisation(self):
        self._current = None
        self.objects = []

    def end_serialisation(self):
        pass

    def start_object(self, obj):
        self._current = OrderedDict()

    def end_object(self, obj):
        self.objects.append(self.get_dump_object(obj))
        self._current = None

    def get_dump_object(self, obj):
        return OrderedDict([('fields', self._current)])

    def getvalue(self):
        return self.objects

def Deserializer(object_list, **options):

    class DummyObject(object):
        pass

    if (isinstance(object_list,int) or 
        isinstance(object_list,float) or 
        isinstance(object_list,str)):
        return object_list

    # create new object 
    dummy = DummyObject()
    dummy.__dict__.update(object_list)
    return dummy



