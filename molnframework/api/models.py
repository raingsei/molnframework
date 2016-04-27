import json

class Parameter(object):
    def __init__(self,name,type):
        self.name = name
        self.type = type

class ParameterCollection(list):
    def append(self, object):
        assert isinstance(object,Parameter)
        return super(ParameterCollection,self).append(object)
    def insert(self, index, object):
        assert isinstance(object,Parameter)
        return super(ParameterCollection,self).insert(index, object)
        

class ComputeService(object):
    def __init__(self,name="",url="",registered_date="",meta_info=""):
        self.name = name
        self.url = url
        self.registered_date = registered_date
        self.meta_info = meta_info
        self.parameters = ParameterCollection()

class ComputerServiceCollection(list):
    def append(self, object):
        assert isinstance(object,ComputeService)
        return super(ComputerServiceCollection,self).append(object)
    def insert(self, index, object):
        assert isinstance(object,ComputeService)
        return super(ComputerServiceCollection,self).insert(index, object)

class ComputePod(object):
    def __init__(self):
        pass
    def __init__(self,name="",address="",system_info="",registered_date=""):
        self.name = name
        self.address = address
        self.system_info = system_info
        self.registered_date = registered_date
        self.services = ComputerServiceCollection()

class ComputePodCollection(list):
    def append(self, object):
        assert isinstance(object,ComputePod)
        return super(ComputePodCollection,self).append(object)
    def insert(self, index, object):
        assert isinstance(object,ComputePod)
        return super(ComputePodCollection,self).insert(index, object)
     
class ComputeApp(object):
    def __init__(self,name="",author="",registered_date="",number_pods=""):
        self.name = name
        self.author = author
        self.registered_date = registered_date
        self.number_pods = number_pods
        self.pods = ComputePodCollection()

def ToComputeApp(data):
    app = ComputeApp()
    app.name = data['name']
    app.author = data['author']
    app.registered_date = data['registered_date']
    app.number_pods = data['number_pods']

    for pod_item in data['pods']:
        pod = ComputePod()
        pod.name = pod_item['name']
        pod.address = pod_item['address']
        pod.system_info = pod_item['system_info']
        pod.registered_date = pod_item['registered_date']

        for service_item in pod_item['services']:
            service = ComputeService()
            service.name = service_item['name']
            service.url = service_item['url']
            service.registered_date = service_item['registered_date']
            service.meta_info = service_item['meta_info']

            if service.meta_info != "":
                para_info = json.loads(service_item['meta_info'])
                for para in para_info:
                    parameter = Parameter(para['name'],para['type'])
                    service.parameters.append(parameter)
            
            pod.services.append(service)
        app.pods.append(pod)

    return app

        

