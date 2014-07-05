import collections

def asdata(obj, asdata):
    if isinstance(obj, Data):
        return obj.asdata(asdata)
    elif isinstance(obj, str):
        return obj
    elif hasattr(obj, '_asdict'):
        return asdata(obj._asdict(), asdata)
    elif isinstance(obj, dict):
        return dict((k, asdata(v, asdata)) for (k, v) in obj.items())
    else:
        try:
            return list(asdata(child, asdata) for child in obj)
        except:
            return obj

class Data:
    def asdata(self, asdata = asdata):
        return dict((k, asdata(v, asdata)) for (k, v) in self.__dict__.items())
    
    def __repr__(self):
        return self.asdata().__repr__()


