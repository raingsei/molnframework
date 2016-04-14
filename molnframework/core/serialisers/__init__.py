import six
import sys
import importlib

from molnframework.core.serialisers.base import SerialiserDoesNotExist


BUILTIN_SERIALISERS = {
    "json": "molnframework.core.serialisers.json",
}

_serialisers = {}

def get_serialiser(format):
    if not _serialisers:
        _load_serialisers()
    if format not in _serialisers:
        raise SerialiserDoesNotExist(format)
    return _serialisers[format].Serialiser

def get_deserialiser(format):
    if not _serialisers:
        _load_serialisers()
    if format not in _serialisers:
        raise SerialiserDoesNotExist(format)
    return _serialisers[format].Deserialiser

def serialise(format, queryset, **options):
    s = get_serialiser(format)()
    s.serialise(queryset, **options)
    return s.getvalue()

def deserialise(format, stream_or_string, **options):
    d = get_deserialiser(format)
    return d(stream_or_string, **options)

def register_serialiser(format, serialiser_module, serialisers=None):
    if serialisers is None and not _serialisers:
        _load_serialisers()

    try:
        module = importlib.import_module(serialiser_module)
    except ImportError as exc:
        bad_serialiser = BadSerialiser(exc)

        module = type('BadSerialiserModule', (object,), {
            'Deserialiser': bad_serialiser,
            'Serialiser': bad_serialiser,
        })

    if serialisers is None:
        _serialisers[format] = module
    else:
        serialisers[format] = module

def unregister_serialiser(format):
    if not _serialisers:
        _load_serialisers()
    if format not in _serialisers:
        raise SerialiserDoesNotExist(format)
    del _serialisers[format]

def _load_serialisers():
    global _serialisers
    serialisers = {}
    
    for format in BUILTIN_SERIALISERS:
        register_serialiser(format, BUILTIN_SERIALISERS[format], serialisers)

    #TODO
    #Allow user to register their own serialiser

    _serialisers = serialisers

class BadSerialiser(object):
    internal_use_only = False

    def __init__(self, exception):
        self.exception = exception

    def __call__(self, *args, **kwargs):
        raise self.exception