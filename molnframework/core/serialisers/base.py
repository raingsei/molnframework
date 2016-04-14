import six
import sys

"""
Exceptions
"""

class SerialiserDoesNotExist(Exception):
    pass

class DeserialisationError(Exception):
    pass

class Serialiser(object):

    def serialise(self,instance_set, **options):
        self.options = options
        self.stream = six.StringIO()
        
        self.iterable = True
        if isinstance(instance_set,str):
           self.iterable = False
        elif not hasattr(instance_set, '__iter__'):
            self.iterable = False

        self.start_serialisation()
        self.first = True
        if self.iterable:
            for count, obj in enumerate(instance_set, start=1):
                self.start_object(obj)
                self.end_object(obj)

                if self.first:
                    self.first = False
        else:
            self.start_object(instance_set)
            self.end_object(instance_set)
        self.end_serialisation()
        return self.getvalue()
        
    def start_serialisation(self):
        raise NotImplementedError('subclasses of Serialiser must provide a start_serialisation() method')

    def end_serialisation(self):
        pass

    def start_object(self, obj):
        raise NotImplementedError('subclasses of Serialiser must provide a start_object() method')

    def end_object(self, obj):
        pass

    def getvalue(self):
        if callable(getattr(self.stream,'getvalue',None)):
            return self.stream.getvalue()

class Deserialiser(six.Iterator):

    def __init__(self,stream_or_string):
        if isinstance(stream_or_string, six.string_types):
            self.stream = six.StringIO(stream_or_string)
        else:
            self.stream = stream_or_string

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError('subclasses of Deserialiser must provide a __next__() method')