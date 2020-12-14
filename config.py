data_path = "./data"
import os

## HADOOP_HOME
HADOOP_HOME = os.environ["HADOOP_HOME"]

## 参数调优配置

taskOpt = {
    # 参数调优程序路径
    "bdbench_home": "/home/lsy/Bigdata/BigDataBackend/cmd/taskOpt",
    # HDFS根路径
    "hdfs_path": "/tune/spark",

    "hadoop": {
        "host": "10.251.1.10",
        "web_ui_port": "52070",
        "hdfs_port": "58021"
    },
    "spark": {
        "host": "10.251.1.10",
        "history_server_port": "28085"
    },
    "mysql": {
        "host": "10.251.1.10",
        "port": "3306",
        "user": "root",
        "passwd": "root",
        "database": "spark"
    }
}