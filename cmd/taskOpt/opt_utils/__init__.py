import logging
import os
import sys
import time

import pymysql

# 程序环境变量
from colorama import Fore

bdbench_home = None
hdfs_path = None
# hadoop 配置信息
hadoop_host = None
hadoop_web_ui_port = None
hadoop_hdfs_port = None
# spark 配置信息
spark_host = None
spark_history_server_port = None
# mysql配置信息
mysql_host = None
mysql_port = None
mysql_user = None
mysql_passwd = None
mysql_database = None


def generate_random_program(num, program, main_class, jar_path, args, hdfs_loc_path, bdbench_home, lines_per_file,
                            words_per_line):
    from taskOpt.opt_utils.generateRandomParameters import generate_random_parameters
    if not os.path.exists(bdbench_home + '/lib/' + program):
        os.makedirs(bdbench_home + '/lib/' + program)
    file_name = bdbench_home + '/lib/' + program + '/run_' + program + str(int(time.time())) + '.sh'
    f = open(file_name, 'w', encoding='utf-8')
    f.write('cd ' + bdbench_home + '\n')
    ConfCombine = []
    for i in range(int(num)):
        confs = generate_random_parameters(program)  # 生成一次参数
        while confs in ConfCombine:
            confs = generate_random_parameters(program)  # 对照参数是否重复
        ConfCombine.append(confs)  # 追加ConfCombine，用于对照
        if program.lower() == 'pagerank':
            args.insert(1, str(confs[0]))
        f.write(
            'bash ' + bdbench_home + f"/opt_utils/genData.sh {confs[0]} {hdfs_loc_path} {program} {bdbench_home} {lines_per_file} {words_per_line}")
        f.write('\n')
        f.write('spark-submit --class ')
        f.write(main_class)
        f.write(generate_command(confs))  # 生成执行命令
        f.write(jar_path)
        f.write(' ')
        f.write(' '.join(args))
        f.write('\n')
    f.write("hdfs dfs -rm -r {hdfs_loc_path}/result".format(hdfs_loc_path=hdfs_loc_path))
    f.close()
    logging.info('随机参数程序脚本生成成功,共{num}条. 文件名: {file_name}'.format(num=num, file_name=file_name))
    return file_name


'''
功能：生成命令行
输入：配置参数
输出：生成的命令行
'''


def generate_command(confs):
    commandconfs = ''
    commandconfs = commandconfs + ' --conf spark.driver.memory=' + str(confs[1]) + 'g'
    commandconfs = commandconfs + ' --conf spark.driver.cores=' + str(confs[2])
    commandconfs = commandconfs + ' --conf spark.executor.memory=' + str(confs[3]) + 'g'
    commandconfs = commandconfs + ' --conf spark.executor.cores=' + str(confs[4])
    commandconfs = commandconfs + ' --conf spark.default.parallelism=' + str(confs[5])
    commandconfs = commandconfs + ' --conf spark.memory.fraction=' + str(confs[6])
    commandconfs = commandconfs + ' --conf spark.memory.storageFraction=' + str(confs[7])
    commandconfs = commandconfs + ' --conf spark.reducer.maxSizeInFlight=' + str(confs[8]) + 'mb'
    commandconfs = commandconfs + ' --conf spark.shuffle.file.buffer=' + str(confs[9]) + 'kb'
    commandconfs = commandconfs + ' --conf spark.shuffle.io.maxRetries=' + str(confs[10])
    commandconfs = commandconfs + ' --conf spark.shuffle.io.numConnectionsPerPeer=' + str(confs[11])
    return commandconfs + ' '


sys.path.append('../../')


def load_conf():
    """
    :param file_name: 配置文件路径："conf/para_opt_setting.json"
    :return: 返回检查后的配置文件字典对象
    """
    from config import taskOpt
    global bdbench_home
    global hdfs_path
    global hadoop_host
    global hadoop_web_ui_port
    global hadoop_hdfs_port
    global spark_host
    global spark_history_server_port
    global mysql_host
    global mysql_port
    global mysql_user
    global mysql_passwd
    global mysql_database

    # with open(file_name, 'r', encoding='utf-8') as f:
    #     conf = json.load(f)
    conf = taskOpt

    # 程序环境变量
    bdbench_home = conf.get('bdbench_home')
    hdfs_path = conf.get('hdfs_path')
    # hadoop 配置信息
    hadoop_host = conf.get('hadoop').get('host')
    hadoop_web_ui_port = conf.get('hadoop').get('web_ui_port')
    hadoop_hdfs_port = conf.get('hadoop').get('hdfs_port')
    # spark 配置信息
    spark_host = conf.get('spark').get('host')
    spark_history_server_port = conf.get('spark').get('history_server_port')
    # mysql配置信息
    mysql_host = conf.get('mysql').get('host')
    mysql_port = conf.get('mysql').get('port')
    mysql_user = conf.get('mysql').get('user')
    mysql_passwd = conf.get('mysql').get('passwd')
    mysql_database = conf.get('mysql').get('database')
    check_not_none(('hadoop_host', hadoop_host),
                   ('hadoop_web_ui_port', hadoop_web_ui_port),
                   ('hadoop_hdfs_port', hadoop_hdfs_port),
                   ('spark_host', spark_host),
                   ('spark_history_server_port', spark_history_server_port),
                   ('mysql_host', mysql_host),
                   ('mysql_port', mysql_port),
                   ('mysql_user', mysql_user),
                   ('mysql_passwd', mysql_passwd),
                   ('mysql_database', mysql_database),
                   ('bdbench_home', bdbench_home),
                   ('hdfs_path', hdfs_path))
    return conf


def check_not_none(*conf_list):
    """
    :param conf_list: 需要检查是否为空的变量列表，列表中元素为元组，第一个参数为变量名，第二个参数为变量值，形如('var',var)
    """
    for conf in conf_list:
        if type(conf) is tuple:
            if conf[1] is None:
                logging.error('{msg:*^20}{item}'.format(msg='配置文件错误，请检查配置项: ', item=conf[0]))
                raise Exception
        else:
            logging.error('{:*^20}'.format('函数传递参数错误'))
            raise Exception


def init_mysql():
    my_db = pymysql.connect(host=mysql_host, port=int(mysql_port), user=mysql_user, passwd=mysql_passwd)
    my_cursor = my_db.cursor()

    my_cursor.execute('SHOW DATABASES')

    has_database = False
    for database in my_cursor.fetchall():
        if database[0] == mysql_database:
            table_cursor = my_db.cursor()
            table_cursor.execute('USE ' + mysql_database)
            table_cursor.execute('SHOW TABLES')
            has_jobpara = False
            has_jobsubmit = False
            for table in table_cursor.fetchall():
                if table[0] == 'jobParameters':
                    has_jobpara = True
                if table[0] == 'jobsubmit':
                    has_jobsubmit = True
            has_database = has_jobpara & has_jobsubmit
            if has_database:
                print(Fore.BLUE + "已经存在数据库: " + mysql_database)
                return
            else:
                print(Fore.RED + "已经存在数据库: " + mysql_database + ', 但缺少数据表, 请更换数据库名或将该数据库删除, 由程序自动创建')
                my_db.close()
                raise Exception

    if not has_database:
        my_cursor.execute('CREATE DATABASE ' + mysql_database)
        my_cursor.execute('USE ' + mysql_database)
        my_cursor.execute('CREATE TABLE jobParameters( \
            jobid char(100)  primary key,\
            name char(100),\
            mainClass char(100),\
            executeTime char(100),\
            driMemGB int,\
            driCor int ,\
            exeMemGB int,\
            exeCor int, \
            defPlsm int, \
            memFra float, \
            memStFra float, \
            redMSIFMB float, \
            shuffleFBKB int, \
            shuffleIMR int, \
            shuffleINCPP int, \
            inputsizeGB float)')
        my_cursor.execute('CREATE TABLE jobsubmit(jobid char(100) primary key, jobname char(50))')
    print(Fore.BLUE + "mysql:" + mysql_host + ":" + mysql_port + "/" + mysql_database + " 初始化完成")
    my_db.close()
