from addict import Dict


class Cache:

    def __init__(self):
        self._data = dict()
    
    def get(self, name):
        return self._data.get(name)

    def set(self, name, value):
        self._data[name] = Dict(value)
        return self._data[name] 

class HdfsCache(Cache):

    def __init__(self):
        super().__init__()


class SparkCache(Cache):

    def __init__(self):
        super().__init__()


class BigDataCache(Cache):
    
    def __init__(self):
        super().__init__()


class TreeCache(Cache):
    
    def __init__(self):
        super().__init__()


hdfs_cache = HdfsCache()
spark_cache = SparkCache()
bigdata_cache = BigDataCache()
tree_cache = TreeCache()