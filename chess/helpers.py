def query_to_json(src):
    result = {}
    if (len(src) > 0):
        data = src.split('&')
        for i in data:
            keyVal = i.split('=');
            result[keyVal[0]] = keyVal[1]
    return result

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

def get_json_response(name, title, error=''):
    return {
        'name': name,
        'title': title,
        'error': error
    }