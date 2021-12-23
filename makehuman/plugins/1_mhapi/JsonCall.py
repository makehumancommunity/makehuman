#!/usr/bin/python

import json
import numpy as np
# import socket


class JsonCall():

    def __init__(self, jsonData=None):
        self.params = {}
        self.data = None
        self.function = "generic"
        self.error = ""
        self.responseIsBinary = False

        if jsonData:
            self.initializeFromJson(jsonData)

    def initializeFromJson(self, jsonData):
        j = json.loads(jsonData)
        if not j:
            return
        self.function = j["function"]
        self.error = j["error"]
        if j["params"]:
            for key, value in j["params"].items():
                self.params[key] = value
        if j["data"]:
            self.data = j["data"]

    def setData(self, data=""):
        self.data = data

    def getData(self):
        return self.data

    def setParam(self, name, value):
        self.params[name] = value

    def getParam(self, name):
        return self.params.get(name, None)

    def setFunction(self, func):
        self.function = func

    def getFunction(self):
        return self.function

    def setError(self, error):
        self.error = error

    def getError(self):
        return self.error

    def serialize(self):

        data = {'function': self.function,
                'error': self.error,
                'params': self.params,
                'data': self.data
                }

        return json.dumps(data, cls=MHApiEncoder)

#    def send(self, host = "127.0.0.1", port = 12345):
#        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        client.connect((host, port))
#        client.send(bytes(self.serialize(),encoding='utf-8'))
#
#        data = ""
#
#        while True:
#            buf = client.recv(1024)
#            if len(buf) > 0:
#                data += buf.strip().decode('utf-8')
#            else:
#                break
#
#        if data:
#            return JsonCall(data)
#        else:
#            return None


class MHApiEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, np.ndarray):
            if obj.dtype == np.dtype('bool'):
                return obj.tolist()
            else:
                return obj.round(6).tolist()

        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')

        if isinstance(obj, float) or isinstance(obj, np.float32) or isinstance(obj, np.float64):
            return float(round(obj, 6))

        if isinstance(obj, np.integer):
            return int(obj)

        # suggested by Python
        # try:
        #     iterable = iter(obj)
        # except TypeError:
        #     pass
        # else:
        #     return list(iterable)

        return json.JSONEncoder.default(self, obj)
