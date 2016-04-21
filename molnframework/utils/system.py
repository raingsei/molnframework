import psutil
import json

def bytes2human(n):

    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

class SystemInfo(dict):
    def __init__(self):
        super(SystemInfo,self).__init__()
    
    @staticmethod
    def get_cpu():
        return CPUInfo()

    @staticmethod
    def get_memory():
        return MemoryInfo()

    @staticmethod
    def get_disk():
        return DiskInfo()

    @staticmethod
    def get_system_info():
        cpu = SystemInfo.get_cpu()
        memory = SystemInfo.get_memory()
        disk = SystemInfo.get_disk()

        info = dict()
        info["cpu"] = cpu
        info["memory"] = memory
        info["disk"] = disk

        return info

class CPUInfo(SystemInfo):
    def __init__(self):
        super(CPUInfo,self).__init__()

        self._total = psutil.cpu_count()
        self._physical = psutil.cpu_count(logical=False)
        self["total"] = self._total
        self["physical"] = self._physical
        self["usage"] = psutil.cpu_percent(interval=1, percpu=True)
    
    @property
    def total(self):
        return self._total
    
    @property
    def physical(self):
        return self._physical

class MemoryInfo(SystemInfo):
    def __init__(self):
        super(MemoryInfo,self).__init__()
        vm = psutil.virtual_memory()
        for key in vm._fields:
            value = getattr(vm,key)
            self[key] = value

    @property
    def total(self):
        return self["total"]
    @property
    def percent(self):
        return self["percent"]
    @property
    def used(self):
        return self["used"]
    @property
    def available(self):
        return self["available"]

    def get(self,key):
        return bytes2human(self[key])

class DiskInfo(SystemInfo):
    def __init__(self):
        super(DiskInfo,self).__init__()
        ds = psutil.disk_usage('/')
        for key in ds._fields:
            value = getattr(ds,key)
            self[key] = value

    @property
    def used(self):
        return self["used"]

    @property
    def free(self):
        return self["free"]

    @property
    def percent(self):
        return self["percent"]

    @property
    def total(self):
        return self["total"]

    def get(self,key):
        return bytes2human(self[key])

