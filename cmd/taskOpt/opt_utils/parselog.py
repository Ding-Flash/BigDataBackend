import logging
import requests
import pymysql
from colorama import Fore

'''
功能：获取并解析历史任务的详细信息，得到历史执行任务运行记录的详细信息
实现方式：调用spark history server API
备注：json解析格式与命名参考spark history server:
'''

# 关注的参数
Wantedconf = ['spark.driver.memory', 'spark.driver.cores', 'spark.executor.memory', \
              'spark.executor.cores', 'spark.default.parallelism', 'spark.memory.fraction', \
              'spark.memory.storageFraction', 'spark.reducer.maxSizeInFlight', 'spark.shuffle.file.buffer', \
              'spark.shuffle.io.maxRetries', 'spark.shuffle.io.numConnectionsPerPeer']
# url权限
url = None


# logging level


def init_parse(conf):
    """
    初始化模块变量
    :param conf:
    """
    global url
    url = "http://{host}:{port}/api/v1/applications/".format(host=conf.get('spark').get('host'),
                                                             port=conf.get('spark').get('history_server_port'))


def getParameter(jobid):
    """
    按照jobid获取参数的配置信息
    :param jobid:
    :return: 某个job的配置参数字典
    """
    try:
        cs_url = url + str(jobid) + '/environment'  # url为全局变量
        print(Fore.BLUE + cs_url)
        r = requests.get(cs_url)
        data = r.json()
        parameter_dir = {}
        for d in data['sparkProperties']:
            parameter_dir[d[0]] = d[1]

        print(Fore.BLUE + "get parameters ok")
        return parameter_dir
    except Exception as e:
        logging.error("network error when get parameters for jobid:", jobid)
        logging.exception(e)


def getInput(jobid):
    """
    按照jobid获取指定任务的输入数据大小
    :param jobid:
    :return: 输入文件大小
    """
    try:
        cs_url = url + str(jobid) + '/stages'  # url为全局变量
        r = requests.get(cs_url)
        data = r.json()
        if len(data) == 0:
            logging.warning('Job Invalid!')
            return 0
        else:
            n = len(data)
            for i in range(0, n):
                strB = str(data[i]['stageId'])  # 从stageId=0判断，数据大小
                if strB == '0':
                    print(Fore.BLUE + 'input size:' + str(round(float(data[i]['inputBytes']) / 10 ** 9, 4)) + 'GB')
                    return round(float(data[i]['inputBytes']) / 10 ** 9, 4)
                else:
                    continue
    except Exception as e:
        logging.error("network error when get inputsize for jobid: " + jobid)
        logging.exception(e)


def get_job_main_class(jobid):
    class_url = url + str(jobid) + '/environment'
    print(Fore.BLUE + '获取:' + class_url)
    r = requests.get(class_url)
    r = requests.get(class_url)
    if r is None:
        print(Fore.BLUE + '重新获取' + class_url)
        r = requests.get(class_url)
    if r is None:
        logging.error("无法获得任务{jobid}信息".format(jobid=jobid))
        raise Exception
    data = r.json()
    for d in data['systemProperties']:
        if d[0] == 'sun.java.command':
            submit_command: str = d[1]
            break
    command_args = submit_command.split(' ')
    index = command_args.index('--class')
    main_class = command_args[index + 1]
    if main_class is None:
        logging.error("无法找到任务{jobid}主类".format(jobid=jobid))
        raise Exception
    return main_class


def getJobs(start):
    """
    访问job history server,返回jobid列表，以及jobid对应的执行时间字典
    :param start: 时间戳，用于进行api数据过滤
    :return: jobid列表和由jobid与job执行时间构成的列表
    """
    try:
        cs_url = url[:len(url) - 1] + '?startTimeEpoch=' + str(start)  # url为全局变量
        print(Fore.BLUE + cs_url)
        # print(Fore.BLUE + str(start))
        print(Fore.BLUE + "{:-^29}".format("-"))
        r = requests.get(cs_url)
        data = r.json()  # data 是list结构数据，但是data[0]是字典结构数据，data[0]['attempts']是list结构数据，data[0]['attempts'][0]是个字典结构
        if data is None:
            return None, None
        n = len(data)  # 获取列表元素个数
        jobid_list = []
        jobid_name = {}
        jobid_excuteTime = {}
        jobid_main_class = {}
        for i in range(n):
            jobid_list.append(data[i]['id'])  # 取出id
            attempt = data[i]['attempts']  # 取出attempts
            jobid_name[data[i]['id']] = str(data[i]['name'])
            jobid_main_class[data[i]['id']] = get_job_main_class(data[i]['id'])  # 获得任务主类
            startTime = int(attempt[0]['startTimeEpoch'])
            finishTime = int(attempt[0]['endTimeEpoch'])
            excuteTime = finishTime - startTime
            jobid_excuteTime[data[i]['id']] = excuteTime
        return jobid_list, jobid_name, jobid_excuteTime, jobid_main_class
    except Exception as e:
        logging.error("network error when getting jobs")
        logging.exception(e)
        raise Exception


def saveParamters(jobid, name, executeTime, main_class, parameters, inputsize):
    """
    将需要的信息存入数据库
    :param jobid:
    :param name:
    :param executeTime:
    :param parameters:
    :param inputsize:
    """
    from taskOpt.opt_utils import mysql_host, mysql_port, mysql_user, mysql_passwd, mysql_database
    db = pymysql.connect(host=mysql_host, port=int(mysql_port), user=mysql_user, passwd=mysql_passwd, db=mysql_database)
    l = [str(jobid), str(name), str(main_class), str(executeTime)]
    for p in parameters:
        l.append(float(p))
    l.append(inputsize)

    sql_command = "INSERT INTO jobParameters(jobid, name, mainClass,executeTime, driMemGB, " \
                  "driCor, exeMemGB,exeCor,defPlsm ,memFra ,memStFra,redMSIFMB," \
                  "shuffleFBKB,shuffleIMR,shuffleINCPP,inputsizeGB) VALUES {values}".format(values=str(tuple(l)))
    # print(Fore.BLUE + sql_command)
    try:
        cursor = db.cursor()
        cursor.execute(sql_command)
        db.commit()
    except Exception as e:
        logging.debug("SQL: " + sql_command)
        logging.error("error occurs when saving in mysql for jobid:" + jobid)
        logging.exception(e)
        db.rollback()
    db.close()


def jobExist(jobid):
    """

    判断某个job是否已经存在
    :param jobid:
    :return:
    """
    from taskOpt.opt_utils import mysql_host, mysql_port, mysql_user, mysql_passwd, mysql_database
    db = pymysql.connect(host=mysql_host, port=int(mysql_port), user=mysql_user, passwd=mysql_passwd,
                         db=mysql_database)  # 打开数据库连接
    print(Fore.BLUE + '******************************************')
    sql_command = "select * from jobParameters where jobid = '{jobid}'".format(jobid=jobid)  # 从jobParameters表中查询jobid
    print(Fore.BLUE + sql_command)

    try:
        cursor = db.cursor()  # 使用cursor()方法获取操作游标
        data = cursor.execute(sql_command)  # 使用execute方法执行SQL语句
        db.commit()  # 提交到数据库执行
    except Exception as e:
        logging.error("commit error when justify if the job exist")
        logging.exception(e)
        db.rollback()  # 发生错误时回滚
        db.close()
        return True
    if data > 0:
        db.close()  # 关闭数据库连接
        print(Fore.BLUE + str(jobid) + " exist")
        return True  # 已经存在
    else:
        db.close()
        print(Fore.BLUE + str(jobid) + " not exist")
        return False


def GetsAndSave(start):
    """
    将取到的数据存入数据库参数表中
    :param start:
    :return:
    """
    try:
        jobid_list, jobid_name, jobid_excuteTime, jobid_main_class = getJobs(start)  # 获取全部jobid
        print(Fore.BLUE + "all jobs: {jobid_list}".format(jobid_list=jobid_list))
        if jobid_list is None:
            return

        for jobid in jobid_list:
            if jobExist(jobid) is not True:  # 不存在则插入数据库
                inputsize = getInput(jobid)  # 获取输入大小
                if inputsize == 0:
                    continue
                else:
                    parameterdir = getParameter(jobid)  # 获取参数字典（目前获取的字典与单位，在存入数据库时需要去掉）
                    name = jobid_name[jobid]
                    excuteTime = jobid_excuteTime[jobid]
                    main_class = jobid_main_class[jobid]
                    parameters = []
                    next_job = False
                    for p in Wantedconf:
                        if parameterdir.get(p, None) is None:
                            next_job = True
                            break
                        parameters.append("".join(filter(lambda x: x in "1234567890.", parameterdir[p])))
                    if next_job:
                        continue
                    saveParamters(jobid, name, excuteTime, main_class, parameters, inputsize)
        print(Fore.BLUE + "fetch and save successfully")
    except Exception as e:
        logging.error("cannot fetch data for network error")
        logging.exception(e)
