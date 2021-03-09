data_path = "./data"
import os

## HADOOP_HOME
HADOOP_HOME = os.environ["HADOOP_HOME"]

## 参数调优配置

taskOpt = {
    # 参数调优程序路径
<<<<<<< HEAD
    "bdbench_home": "/home/hcchen/Bigdata/BigDataBackend/cmd/taskOpt",
=======
    "bdbench_home": "/home/lsy/Bigdata/BigDataBackend/cmd/taskOpt",
>>>>>>> 13c8855b7dc246c61a0bed15c29dfe29691ebd0c
    # HDFS根路径
    "hdfs_path": "/tune/spark",

    "hadoop": {
<<<<<<< HEAD
        "host": "10.212.68.151",
=======
        "host": "10.251.1.10",
>>>>>>> 13c8855b7dc246c61a0bed15c29dfe29691ebd0c
        "web_ui_port": "52070",
        "hdfs_port": "58021"
    },
    "spark": {
<<<<<<< HEAD
        "host": "10.212.68.151",
        "history_server_port": "28085"
    },
    "mysql": {
        "host": "10.212.68.151",
=======
        "host": "10.251.1.10",
        "history_server_port": "28085"
    },
    "mysql": {
        "host": "10.251.1.10",
>>>>>>> 13c8855b7dc246c61a0bed15c29dfe29691ebd0c
        "port": "3306",
        "user": "root",
        "passwd": "root",
        "database": "spark"
    }
}
