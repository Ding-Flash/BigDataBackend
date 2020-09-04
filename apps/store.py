from addict import Dict
from abc import ABCMeta, abstractmethod
import pickle
import os
import shutil

path = os.path.dirname(os.path.abspath(__file__))
store_path = path[:-4] + 'data/'


class Cache(metaclass=ABCMeta):

    def __init__(self):
        self.task_path = dict()
        self.report = Dict()
        self.status = dict()
        self.conf = dict()

    def update_from_pickle(self):
        class_type = self.__class__.__name__
        if class_type == "HdfsCache":
            file_name = store_path + 'hdfs/'+'cache.pkl'
        elif class_type == "SparkCache":
            file_name = store_path + 'spark/' + 'cache.pkl'
        elif class_type == "BigDataCache":
            file_name = store_path + 'bigroot/' + 'cache.pkl'
        elif class_type == "AliLoadCache":
            file_name = store_path + 'aliload/' + 'cache.pkl'
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                cache = pickle.load(f)
            return cache
        return self

    @abstractmethod
    def get_conf(self, name):
        pass

    @abstractmethod
    def set_conf(self, name, setting):
        pass

    @abstractmethod
    def get_task_report(self, name):
        pass

    @abstractmethod
    def set_task_report(self, name, report):
        pass

    def store_pickle(self):
        class_type = self.__class__.__name__
        if class_type == "HdfsCache":
            file_name = store_path + 'hdfs/'+'cache.pkl'
        elif class_type == "SparkCache":
            file_name = store_path + 'spark/' + 'cache.pkl'
        elif class_type == "BigDataCache":
            file_name = store_path + 'bigroot/' + 'cache.pkl'
        elif class_type == "AliLoadCache":
            file_name = store_path + 'aliload/' + 'cache.pkl'
        with open(file_name, "wb") as f:
            pickle.dump(self, f)


class HdfsCache(Cache):

    def __init__(self):
        super().__init__()

    def set_conf(self, name, setting):
        self.conf[name] = setting

    def get_conf(self, name):
        return self.conf[name]

    def get_task_path(self, name):
        return self.task_path.get(name, None)

    def set_task_path(self, name):
        self.task_path[name] = store_path + "hdfs/" + name
        try:
            os.mkdir(self.task_path[name])
        except FileExistsError:
            pass
        self.status[name] = "submit"

    def get_task_report(self, name):
        return self.report.get(name, None)

    def set_task_report(self, name, report):
        self.report[name] = Dict(report)

    def delete_task(self, name):
        if name in self.conf:
            del self.conf[name]
        if name in self.status:
            del self.status[name]
        if name in self.report:
            del self.report[name]
        task_path = self.task_path[name]
        shutil.rmtree(task_path)
        self.store_pickle()


class SparkCache(Cache):

    def __init__(self):
        super().__init__()

    def get_conf(self, name):
        return self.conf[name]

    def set_conf(self, name, setting):
        self.conf[name] = setting

    def get_task_report(self, name):
        return self.report.get(name, None)

    def set_task_report(self, name, report):
        self.report[name] = Dict(report)
        self.status[name] = "finished"

    def delete_task(self, name):
        if name in self.conf:
            del self.conf[name]
        if name in self.status:
            del self.status[name]
        if name in self.report:
            del self.report[name]
        self.store_pickle()


class AliLoadCache(Cache):

    def __init__(self):
        super().__init__()

    def get_conf(self, name):
        return self.conf[name]

    def set_conf(self, name, setting):
        self.conf[name] = setting

    def get_task_report(self, name):
        return self.report.get(name, None)

    def set_task_report(self, name, report):
        self.report[name] = Dict(report)
        self.status[name] = "finished"

    def delete_task(self, name):
        if name in self.conf:
            del self.conf[name]
        if name in self.status:
            del self.status[name]
        if name in self.report:
            del self.report[name]
        self.store_pickle()


class BigDataCache(Cache):
    
    def __init__(self):
        super().__init__()

    def get_conf(self, name):
        return self.conf[name]

    def set_conf(self, name, setting):
        self.conf[name] = setting

    def get_task_report(self, name):
        return self.report.get(name, None)

    def set_task_report(self, name, report):
        self.report[name] = Dict(report)
        self.status[name] = "finished"

    def delete_task(self, name):
        if name in self.conf:
            del self.conf[name]
        if name in self.status:
            del self.status[name]
        if name in self.report:
            del self.report[name]
        self.store_pickle()


# try:
#     file_path = store_path + 'hdfs/cache.pkl'
#     with open(file_path, 'rb') as f:
#         hdfs_cache = pickle.load(f)
# except FileNotFoundError:
#     hdfs_cache = HdfsCache()

# try:
#     file_path = store_path + 'spark/cache.pkl'
#     with open(file_path, 'rb') as f:
#         spark_cache = pickle.load(f)
# except FileNotFoundError:
#     spark_cache = SparkCache()

## TODO 记得去掉
try:
    file_path = store_path + 'bigroot/cache.pkl'
    with open(file_path, 'rb') as f:
        bigroot_cache = pickle.load(f)
except FileNotFoundError:
    bigroot_cache = BigDataCache()
