import inspect

def get_user_defined_attributes(cls):
    """ 
    function to get user defined attributes
    """

    boring = dir(type('dummy', (object,), {}))
    return {item[0]:item[1]
            for item in inspect.getmembers(cls)
            if item[0] not in boring}