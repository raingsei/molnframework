import six
import json
import sys
import datetime
import decimal
import uuid

from molnframework.core.serialisers.base import DeserialisationError
from molnframework.core.serialisers.python import (
    Serialiser as BaseSerialiser, Deserializer as BaseDerialiser)

class DateTimeAwareJSONEncoder(json.JSONEncoder):

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        else:
            return o.__dict__
 
class Serialiser(BaseSerialiser):

    def _prepare(self):
        if json.__version__.split('.') >= ['2','1','3']:
            self.options.update({'use_decimal': False})
        self._current = None
        self.json_kwargs = self.options.copy()
        self.json_kwargs.pop('stream', None)
        self.json_kwargs.pop('fields', None)
        if self.options.get('indent'):
            # Prevent trailing spaces
            self.json_kwargs['separators'] = (',', ': ')

    def start_serialisation(self):
        self._prepare()
        self.stream.write("[")

    def end_serialisation(self):
        if self.options.get("indent"):
            self.stream.write("\n")
        self.stream.write("]")
        if self.options.get("indent"):
            self.stream.write("\n")

    def start_object(self, obj):
        pass
    
    def end_object(self, obj):
        indent = self.options.get("indent")
        if not self.first:
            self.stream.write(",")
            if not indent:
                self.stream.write(" ")
        if indent:
            self.stream.write("\n")

        json.dump(obj, self.stream,
            cls=DateTimeAwareJSONEncoder, **self.json_kwargs)

    def getvalue(self):
        return super(BaseSerialiser,self).getvalue()

def Deserialiser(stream_or_string, **options):
   
    if not isinstance(stream_or_string,(bytes,six.string_types)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string,bytes):
        stream_or_string = stream_or_string.decode('utf-8')
    
    #return json.loads(stream_or_string)
    try:
        objects = json.loads(stream_or_string)
        for obj in BaseSerialiser.Deserialiser(objects,**options):
            yield obj
    except GeneratorExit:
        raise
    except Exception as e:
        six.reraise(DeserialisationError,DeserialisationError(e),sys.exc_info()[2])
