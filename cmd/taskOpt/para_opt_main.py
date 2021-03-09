import os
import re

import pymysql
from colorama import Fore

from taskOpt.opt_utils import load_conf, init_mysql, generate_random_program
from taskOpt.opt_utils.parselog import init_parse, GetsAndSave
from taskOpt.opt_utils.tuneParameters import parseAndSubmit

'''
本文件是调优程序唯一入口，参数设置均由本文件完成
程序运行命令类似：
python para_opt_main.py --model Xgb --times 15 sort cn.ac.ict.bigdatabench.Sort bd_jars/bigdatabench-spark_1.3.0-hadoop_1.0.4.jar arg1 arg2
'''
# logging.basicConfig(level=print)
# /tune/spark/sort/data /tune/spark/sort/result
# /tune/spark/pagerank/data/Google_genGraph_21.txt /tune/spark/pagerank/result
# spark-submit --class cn.ac.ict.bigdatabench.Sort --conf spark.driver.memory=30g --conf spark.driver.cores=4 --conf spark.executor.memory=10g --conf spark.executor.cores=4 --conf spark.default.parallelism=6 --conf spark.memory.fraction=0.6499999999999999 --conf spark.memory.storageFraction=0.49999999999999983 --conf spark.reducer.maxSizeInFlight=118mb --conf spark.shuffle.file.buffer=96kb --conf spark.shuffle.io.maxRetries=8 --conf spark.shuffle.io.numConnectionsPerPeer=2 /home/lsy/Bigdata/BigDataBackend/example_jars/bigdatabench-spark_1.3.0-hadoop_1.0.4.jar hdfs://10.251.1.10:58021/tune/spark/sort/data hdfs://10.251.1.10:58021/tune/spark/sort/result
conf = None
main_class_dict = {'cn.ac.ict.bigdatabench.Sort': 'sort',
                   'cn.ac.ict.bigdatabench.WordCount': 'wordcount',
                   'cn.ac.ict.bigdatabench.PageRank': 'pagerank'}


# @click.command()
# @click.option('--model', default='Ext', type=click.Choice(['Ext', 'Xgb']), help='Tuning model')
# @click.option('--times', default='5', help='execute command times')
# @click.option('--mode', default='run_all', type=click.Choice(['run_all', 'get_opt_para', 'gen_train_data']),
#               help='program running mode')
# @click.option('--lpf', default=8000, type=int, help='only be used in generate word worklod, it means lines per file')
# @click.option('--wpl', default=10000, type=int, help='only be used in generate word worklod, it means words per line')
# @click.option('--resubmit', default="no", type=click.Choice(["no", "yes"]), help="resubmit spark job or not")
# @click.argument('program')
# @click.argument('main_class')
# @click.argument('jar_path', type=click.Path(exists=True))
# @click.argument('args', nargs=-1)
def run_para_opt_main(program: str, main_class, jar_path, args, model, times, mode, lpf, wpl, resubmit):
    # ###############################
    # 初始化阶段
    # ###############################
    print(
        Fore.BLUE + "\nprogram: {program}\nmain_class: {main_class}\njar path: {jar_path}\nprogram args: {args}".format(
            program=program,
            main_class=main_class,
            jar_path=jar_path,
            args=args))
    print(Fore.BLUE + "\nprogram mode: {mode}\ntrain model: {model}".format(mode=mode, model=model))
    # 判断对应文件夹是否存在
    if not os.path.exists("./lib/" + program):
        os.system("mkdir -p ./lib/" + program)

    # hdfs 本地访问路径
    hdfs_loc_path = conf.get('hdfs_path') + '/' + program
    hdfs_loc_io_path = [hdfs_loc_path + '/data', hdfs_loc_path + '/result']
    # 构造hdfs访问路径
    from taskOpt.opt_utils import hadoop_host, hadoop_hdfs_port
    io_path = ['hdfs://{host}:{port}'.format(host=hadoop_host, port=hadoop_hdfs_port) + path
               for path in hdfs_loc_io_path]

    # 如果是pagerank时，需要检验用户输入文件是否存在

    # 判断如果用户输入参数中含有hdfs路径，是否加上hdfs://前缀，如果没有则加上前缀
    args_list = [str(arg) for arg in args.split(' ')]
    for i in range(len(args_list)):
        if re.match('^/(\w+/?)+', args_list[i]) is not None:
            res = os.popen("hdfs dfs -test -e {path};echo $?".format(path=args_list[i])).read()
            if res.strip() == "1":
                # 对应路径不存在，需要创建
                if "res" not in args_list[i]:
                    if program.lower() == 'pagerank':
                        print(Fore.RED + "pagerank程序请先确保输入文件夹、数据文件均存在")
                        raise Exception
            elif res.strip() == "0":
                # 对应路径存在
                pass
            else:
                print(Fore.RED + "用户输入hdfs路径有误，未知情况，程序退出")
                raise Exception
            args_list[i] = 'hdfs://{host}:{port}'.format(host=hadoop_host, port=hadoop_hdfs_port) + args_list[i]

    # ###############################
    # 运行模式判断
    # ###############################
    if mode == 'run_all' or mode == 'gen_train_data':
        print(Fore.BLUE + f"execute train command times: {times}")
        # 生成随机参数命令脚本
        random_pro_file = generate_random_program(times, program, main_class, jar_path, args_list, hdfs_loc_path,
                                                  conf.get('bdbench_home'), lpf, wpl)

        # 执行随机参数命令脚本
        os.system('bash ' + random_pro_file)

        # 获取程序执行历史，并将相关参数存入mysql
        init_parse(conf)
        GetsAndSave(0)
        print(Fore.BLUE + "{:-^30}".format("训练数据生成完成"))
    if mode == 'run_all' or mode == 'get_opt_para':
        # 获取程序执行历史，并将相关参数存入mysql
        init_parse(conf)
        GetsAndSave(0)
        # 校验数据库中是否存在数据
        check_mysql(program, main_class, jar_path, args, model, times, mode, lpf, wpl, resubmit)
        # 根据提交的任务，得出最优参数
        tunecommand, command_args_dict = parseAndSubmit([main_class, jar_path, *io_path, args_list], 100000, model,
                                                        program,
                                                        resubmit, times)
        return tunecommand, command_args_dict


def task_opt_api_init():
    global conf
    # 加载配置文件
    conf = load_conf()
    # 初始化数据库
    init_mysql()


def task_opt_api_main(jar_path, main_class, args, times, model_name):
    if main_class not in main_class_dict.keys():
        return None
    # 运行主程序
    tunecommand, command_args_dict = run_para_opt_main(main_class_dict[main_class],
                                                       main_class,
                                                       jar_path,
                                                       args,
                                                       model_name,
                                                       times,
                                                       'get_opt_para',
                                                       8000,
                                                       10000,
                                                       'no')
    return tunecommand, command_args_dict


def check_mysql(program, main_class, jar_path, args, model, times, mode, lpf, wpl, resubmit):
    from taskOpt.opt_utils import mysql_host,mysql_port,mysql_user,mysql_passwd,mysql_database
    db = pymysql.connect(host=mysql_host, port=int(mysql_port), user=mysql_user, passwd=mysql_passwd, db=mysql_database)
    cursor = db.cursor()
    sql_command = f"SELECT * FROM jobParameters WHERE jobParameters.mainClass='{main_class}'"
    cursor.execute(sql_command)
    d = cursor.fetchall()
    db.close()
    if len(d) < 1:
        print(Fore.RED + "mysql中没有{job}的数据，本次执行需要生成数据，时间较长".format(job=main_class))
        run_para_opt_main(program, main_class, jar_path, args, model, times, "run_all", lpf, wpl, resubmit)


if __name__ == '__main__':
    # 加载配置文件
    # conf = load_conf('conf/para_opt_setting.json')
    conf = load_conf()
    # 初始化数据库
    init_mysql()
    # 运行主程序
    command_args_dict = run_para_opt_main()
    print(Fore.BLUE + str(command_args_dict))
