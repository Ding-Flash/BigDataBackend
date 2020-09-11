import logging
import os
import re

from colorama import Fore

from taskOpt.opt_utils import generate_random_program, check_mysql, load_conf, init_mysql
from taskOpt.opt_utils.parselog import init_parse, GetsAndSave
from taskOpt.opt_utils.tuneParameters import parseAndSubmit

'''
本文件是调优程序唯一入口，参数设置均由本文件完成
程序运行命令类似：
python para_opt_main.py --model Xgb --times 15 sort cn.ac.ict.bigdatabench.Sort bd_jars/bigdatabench-spark_1.3.0-hadoop_1.0.4.jar arg1 arg2
'''
# logging.basicConfig(level=print)
conf = None


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
    args = [str(arg) for arg in args.split(' ')]
    for i in range(len(args)):
        if re.match('^/(\w+/?)+', args[i]) is not None:
            res = os.popen("hdfs dfs -test -e {path};echo $?".format(path=args[i])).read()
            if res.strip() == "1":
                # 对应路径不存在，需要创建
                if "res" not in args[i]:
                    if program.lower() == 'pagerank':
                        print(Fore.RED + "pagerank程序请先确保输入文件夹、数据文件均存在")
                        raise Exception
            elif res.strip() == "0":
                # 对应路径存在
                pass
            else:
                print(Fore.RED + "用户输入hdfs路径有误，未知情况，程序退出")
                raise Exception
            args[i] = 'hdfs://{host}:{port}'.format(host=hadoop_host, port=hadoop_hdfs_port) + args[i]

    # ###############################
    # 运行模式判断
    # ###############################
    if mode == 'run_all' or mode == 'gen_train_data':
        print(Fore.BLUE + "execute train command times: {times}")
        # 生成随机参数命令脚本
        random_pro_file = generate_random_program(times, program, main_class, jar_path, args, hdfs_loc_path,
                                                  conf.get('bdbench_home'), lpf, wpl)

        # 执行随机参数命令脚本
        os.system('bash ' + random_pro_file)

        # 获取程序执行历史，并将相关参数存入mysql
        init_parse(conf)
        GetsAndSave(0)
        print(Fore.BLUE + "{:-^30}".format("训练数据生成完成"))
    if mode == 'run_all' or mode == 'get_opt_para':
        # 校验数据库中是否存在数据
        check_mysql(main_class)
        # 根据提交的任务，得出最优参数
        tunecommand, command_args_dict = parseAndSubmit([main_class, jar_path, *io_path, args], 100000, model, program,
                                                        resubmit)
        return tunecommand, command_args_dict


def task_opt_api_init():
    global conf
    # 加载配置文件
    conf = load_conf()
    # 初始化数据库
    init_mysql()


def task_opt_api_main(jar_path, main_class, args, times, model_name):
    main_class_dict = {'cn.ac.ict.bigdatabench.Sort': 'sort',
                       'cn.ac.ict.bigdatabench.WordCount': 'wordcount',
                       'cn.ac.ict.bigdatabench.PageRank': 'pagerank'}
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


if __name__ == '__main__':
    # 加载配置文件
    # conf = load_conf('conf/para_opt_setting.json')
    conf = load_conf()
    # 初始化数据库
    init_mysql()
    # 运行主程序
    command_args_dict = run_para_opt_main()
    print(Fore.BLUE + str(command_args_dict))
