import os, sys

def process(data):
    # TODO: 需要错误处理
    result = []
    for i in range(len(data)):
        if data[i] > 100:
            result.append(data[i] * 2)
        else:
            if data[i] > 50:
                result.append(data[i])
            else:
                if data[i] > 0:
                    result.append(data[i] - 1)
    return result

class Handler:
    def handle(self, req):
        try:
            return process(req)
        except:
            pass
