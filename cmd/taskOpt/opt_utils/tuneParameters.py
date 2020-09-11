#!/usr/bin/python


'''
@功能：
用户提交submit接口：用户使用此接口时，默认采用系统的自动参数调优工具
用户传入参数：原生的spark-submit提交Jar包命令
例如：spark-submit --class cn.ac.ict.bigdatabench.Sort $BDBENCH_JARS/bigdatabench-spark_1.3.0-hadoop_1.0.4.jar input output
spark-submit --class cn.ac.ict.bigdatabench.PageRank $BDBENCH_HOME/bd_jars/bigdatabench-spark_1.3.0-hadoop_1.0.4.jar input 21 output
@依赖：
需要安装python hdfs模块
安装命令 pip install hdfs
'''
import logging
import os
import sys

from colorama import Fore
from hdfs import InsecureClient

from taskOpt.opt_utils import trainModel, optimize

'''
@功能：调用hdfs模块，获取用户输入文件路径信息
@输入：为hdfs上的路径
@返回：指定输入文件夹中使用的字节数
@注意事项：需要配置成hdfs所在的地址,有用户权限问题
'''


def getPathLength(spath, host=None):
    from taskOpt.opt_utils import hadoop_host, hadoop_web_ui_port, hadoop_hdfs_port
    try:
        if host is None:
            host = "http://{hadoop_host}:{hadoop_web_ui_port}".format(hadoop_host=hadoop_host,
                                                                      hadoop_web_ui_port=hadoop_web_ui_port)
        client = InsecureClient(host)
        spath = spath.split("hdfs://{hadoop_host}:{hadoop_hdfs_port}".format(hadoop_host=hadoop_host,
                                                                             hadoop_hdfs_port=hadoop_hdfs_port))[-1]
        length = client.content(spath)['length']
        assert length is not None
        return length
    except Exception as e:
        print(Fore.RED + "erros occurs when accsing HDFS,check for the host:{host}".format(host=host))
        logging.exception(e)
        raise Exception


'''
@功能：判断是否存在历史相同任务，如存在，则进行优化,并构建模型,否则，不进行优化
@实现：当前实现的方案为：通过函数名称是否相同来判断任务是否相同，即数据库检索操作
@要求：需要用户在提交job时设定job name 等于 主函数名称
'''


def createModel(main_class, model_name):
    sql_command = "SELECT * FROM jobParameters WHERE jobParameters.mainClass='{main_class}'".format(
        main_class=main_class)
    x, y = trainModel.SQLTrainData(sql_command)
    if len(x) > 1:  # 检索出结果
        x = x[:len(x) - 1]
        y = y[:len(y) - 1]
        if model_name == 'Ext':
            et = trainModel.getExtraTreeModel(x, y)
            return et
        elif model_name == 'Xgb':
            xg = trainModel.getXgboostModel(x, y)
            return xg
    return None


'''
@功能：创建含有优化参数的命令
@输入：训练好的模型和数据量
@返回：运行的spark命令
'''

sys.path.append("..")


def optiConf(model, N, command, program):
    conf = optimize.optimizer('taskOpt/conf/program_config.json', model, 1000000.0, 0.95, N, program)
    commandconfs = ''
    commandconfs = commandconfs + ' --conf spark.driver.memory=' + str(int(conf[0])) + 'g'
    commandconfs = commandconfs + ' --conf spark.driver.cores=' + str(int(conf[1]))
    commandconfs = commandconfs + ' --conf spark.executor.memory=' + str(int(conf[2])) + 'g'
    commandconfs = commandconfs + ' --conf spark.executor.cores=' + str(int(conf[3]))
    commandconfs = commandconfs + ' --conf spark.default.parallelism=' + str(int(conf[4]))
    commandconfs = commandconfs + ' --conf spark.memory.fraction=' + str(conf[5])
    commandconfs = commandconfs + ' --conf spark.memory.storageFraction=' + str(conf[6])
    commandconfs = commandconfs + ' --conf spark.reducer.maxSizeInFlight=' + str(int(conf[7])) + 'mb'
    commandconfs = commandconfs + ' --conf spark.shuffle.file.buffer=' + str(int(conf[8])) + 'kb'
    commandconfs = commandconfs + ' --conf spark.shuffle.io.maxRetries=' + str(int(conf[9]))
    commandconfs = commandconfs + ' --conf spark.shuffle.io.numConnectionsPerPeer=' + str(int(conf[10]))

    classname = command[0]
    jarname = command[1]
    # inputpath = command[2]
    # outputpath = command[3]

    sparkcommand = "spark-submit --class "
    sparkcommand += str(classname)
    jarcommand = str(jarname)

    # iocommand = str(inputpath)l
    # iocommand += " "
    # iocommand += str(outputpath)

    command_args_dict = {"spark.driver.memory": str(int(conf[0])) + 'g',
                         "spark.driver.cores": str(int(conf[1])),
                         "spark.executor.memory": str(int(conf[2])) + 'g',
                         "spark.executor.cores": str(int(conf[3])),
                         "spark.default.parallelism": str(int(conf[4])),
                         "spark.memory.fraction": str(conf[5]),
                         "spark.memory.storageFraction": str(conf[6]),
                         "spark.reducer.maxSizeInFlight": str(int(conf[7])) + 'mb',
                         "spark.shuffle.file.buffer": str(int(conf[8])) + 'kb',
                         "spark.shuffle.io.maxRetries": str(int(conf[9])),
                         "spark.shuffle.io.numConnectionsPerPeer": str(int(conf[10])),
                         "main_class": classname,
                         "jar_path": jarcommand,
                         "args": " ".join(command[-1])
                         }
    print(command)

    return sparkcommand + commandconfs + " " + jarcommand + " " + " ".join(command[-1]), command_args_dict


'''

@功能:用于解析用户提交的spark命令，例如 spark-submit --class cn.ac.ict.bigdatabench.Sort /home/hadoop/BigDataBench_V4.0_Spark/JAR_FILE/bigdatabench-spark_1.3.0-hadoop_1.0.4.jar /spark/wordcount/data /spark/wordcount/result
@接口要求：用户提交的格式为 spark 函数名 jar包路径 输入目录  输出目录，中间用空格分开
@输入：解析过的用户输入的命令，数据量阈值大小
'''


def parseAndSubmit(command, threshold_size, model_name, program, resubmit):
    funcnames = {'cn.ac.ict.bigdatabench.Sort': 'BigDataBench Sort',
                 'cn.ac.ict.bigdatabench.WordCount': 'BigDataBench WordCount',
                 'cn.ac.ict.bigdatabench.PageRank': 'BigDataBench PageRank'}  # 做个字典,有几个任务，就做几个大小的字典

    # funcname = funcnames[command[0]]
    main_class = command[0]
    inputpath = command[2]
    N = getPathLength(str(inputpath).strip())  # 计算输入N
    print(Fore.BLUE + "the input size bytes : {N}".format(N=N))
    if int(N) < threshold_size:  # 如果数据量小于阈值，不进行优化
        print(Fore.BLUE + "do not tune for the inputsize is low")
    else:
        model = createModel(str(main_class).strip(), model_name)
        print(Fore.BLUE + main_class + " create model successfully")
        if model is not None:  # 可以优化
            print(Fore.BLUE + "start tunning")
            newN = round(float(N) / 10 ** 9, 4)
            tunecommand, command_args_dict = optiConf(model, newN, command, program)
            print(Fore.BLUE + "{:-^30}".format("优化参数生成完成"))
            print(Fore.BLUE + "tuned configuration parameters:")
            print(Fore.BLUE + tunecommand)
            os.system("hdfs dfs -rm -r /tune/spark/{program}/result".format(program=program))
            if resubmit == 'yes':
                print(Fore.BLUE + "{:-^30}".format("使用新参数执行任务"))
                callcommand(tunecommand)

            return tunecommand, command_args_dict
        else:
            print(Fore.BLUE + "doesn't tune for the history data like this job is little")


'''
@功能：将命令传入python命令行进行执行
@输入：命令行，如spark .....
'''


def callcommand(tunecommand):
    print(Fore.BLUE + "start spark job")
    res = os.system(tunecommand)
    return res