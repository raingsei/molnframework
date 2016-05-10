from molnframework.api import APIClient
from molnframework.api.pool import ResourcePool

if __name__ == "__main__":

    api_client = APIClient("127.0.0.1","5678","admin","chlang2403")
    ss = api_client.Login()

    b = ss

    #ressource = api_client.GetResource("sample", "TestFunctionService")
    
    #ss = ResourcePool(ressource)
   
    #result = ressource[0].execute(x=2.0,y=3.0,z=4.0)
    #ss = result