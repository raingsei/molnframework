from queue import Queue

class Resource(object):
    __slots__ = ('pool','resource')

    def __init__(self,pool,resource):
        self._pool = pool
        self.resource = resource
    def __del__(self):
        try:
            if self._pool is not None:
                self.release()
        except:
            pass

    def release(self):
        self._pool.relase(self.resource)
        self._pool = None

    def __enter__(self):
        return self.resource

    def __exit__(self, unused_type, unused_val, unused_tb):
        self.release()

    def __repr__(self):
        return 'Resource(%r)' % self.resource


class ResourcePool(object):
    def __init__(self,resources):
        self._resources = Queue()
        for resource in resources:
            self._resources.put(resource)
    def acquire(self,timeout=None):
        if timeout is None:
            resource = self._resources.get()
        else:
            resource = self._resources.get(True,timeout)
        return resource

    def release(self,resource):
        self._resources.put(resource)

    def empty(self):
        return self._resources.empty()
