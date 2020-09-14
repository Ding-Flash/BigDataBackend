import threading

from colorama import init, Fore, Back, Style
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import xmltodict as xd

import os
import sys

from taskOpt.opt_utils.tuneParameters import callcommand
from taskOpt.para_opt_main import task_opt_api_init, task_opt_api_main

sys.path.append('../')
from utils import clean_xml
import subprocess
from straggler import clean_all, get_time_alignment_deviation, get_trace_log, merge
from straggler.sample import samp_run, get_logs, log_exe
from straggler.analysis import engine, decode_dot, do_straggler
from datetime import datetime
from apps.store import SparkCache, AliLoadCache, TaskOptCache

from detect_root import start_samp_slave, start, collect_logs, collect_load_logs, init_root, decode, kill
from bigroot.env_conf import app_path, get_master_ip, get_slaves_name
from bigroot.root_cause import analysis
from apps.store import bigroot_cache
from common import extract_stat

from config import HADOOP_HOME
core_file = HADOOP_HOME + "/etc/hadoop/core-site.xml"

completer = WordCompleter(['BigRoot', 'SparkTree', 'ASTracer', 'AliLoad','TaskOpt'], ignore_case=True)

sparkcache = SparkCache()
alicache = AliLoadCache()
optcache = TaskOptCache()

def clean_xml():
    with open(core_file) as f:
        core = f.read()
    core = xd.parse(core)
    conf_map = {}
    def find_name(target):
        for idx, t in enumerate(target):
            conf_map[t['name']] = idx
    target = core['configuration']['property']
    find_name(target)
    target[conf_map['hadoop.htrace.local.file.span.receiver.path']]['value'] = ""
    target[conf_map['hadoop.htrace.sampler.classes']]['value'] = ""
    ans = xd.unparse(core, pretty=True)
    with open(core_file, 'w') as f:
        f.write(ans)


def spark(session):
    global spark_cache
    while True:
        spark_cache = sparkcache.update_from_pickle()
        print(Fore.YELLOW+"You are in SparkTree mode, please input task name:")
        task_name = session.prompt("SparkTree (task name)> ", auto_suggest=AutoSuggestFromHistory())
        if task_name == "quit":
            break
        print(Fore.YELLOW+"You are in SparkTree mode, please input cmd:")
        cmd = session.prompt("SparkTree (cmd)> ", auto_suggest=AutoSuggestFromHistory())

        print(Fore.YELLOW + "Please input your describe of the task:")
        describe = session.prompt("SparkTree (describe)> ")

        print(Fore.BLUE+"Initializing...".upper())
        clean_all.clean_sample_log()

        print(Fore.BLUE + "Doing time alignment...".upper())
        get_time_alignment_deviation.ntpdate()

        print(Fore.BLUE+"Sampling Start".upper())
        samp_run.start_sample()

        res = os.system(cmd)

        if res != 0:
            print(Fore.RED+"Task Run Error, Please Try Again")
            print(Fore.BLUE + "Sampling stop".upper())
            samp_run.stop_sample()
            continue

        print(Fore.BLUE+"Sampling stop".upper())
        samp_run.stop_sample()

        print(Fore.BLUE+"Collecting logs...".upper())
        try:
            spark_home = os.environ['SPARK_HOME']
        except KeyError:
            print(Fore.RED+"请设置SPARK_HOME环境变量")
            break
        try:
            cur_path = os.path.dirname(os.path.abspath(__file__))
            collect_log_cmd = "cp " + spark_home + '/tsee_log/app* ' + cur_path + '/temp/spark/app'
            subprocess.check_call(collect_log_cmd, shell=True)
        except subprocess.CalledProcessError:
            print(Fore.RED+"日志收集失败")
            continue
        try:
            get_trace_log.collect_trace_log()
            get_logs.get_sys_log()
        except Exception:
            pass

        print(Fore.BLUE+"Analysis Start...".upper())
        log_exe.analysis_log()
        engine.start_analysis()
        res = decode_dot.decode_tree()

        straggler_num = 0

        try:
            straggler_num = do_straggler.detect()
        except:
            print(Fore.RED + "No straggler! Please Try Again")
            break

        print(Fore.GREEN+"analysis complete!".upper())

        if straggler_num > 0:
            report = merge.analysis_store()
            spark_cache.set_conf(task_name, dict(time=datetime.now(), desc=describe))
            spark_cache.set_task_report(task_name, report)
            spark_cache.status[task_name] = 'finished'
            spark_cache.store_pickle()
            print(Style.DIM+"please open your browser to look your report")
        else:
            print(Fore.RED + "No straggler! Please Try Again")
        break


def bigroot(session):
    prefix = app_path
    master_ip = get_master_ip()
    slaves_name = get_slaves_name()
    while True:
        print(Fore.YELLOW+"You are in bigroot mode, please input task name:")
        task_name = session.prompt("BigRoot (task name)> ", auto_suggest=AutoSuggestFromHistory())
        if task_name == "quit":
            break
        print(Fore.YELLOW+"You are in bigroot mode, please input cmd:")
        cmd = session.prompt("BigRoot (cmd)> ", auto_suggest=AutoSuggestFromHistory())

        print(Fore.YELLOW+"Please input your describe of the task:")
        describe = session.prompt("BigRoot (describe)> ")

        print(Fore.BLUE + "Initializing...".upper())
        log_dir = init_root(task_name)

        print(Fore.BLUE+"Sampling Start".upper())
        for slave in slaves_name:
            t = threading.Thread(target=start_samp_slave, args=(slave, log_dir))
            t.start()

        res = os.system(cmd)

        if res != 0:
            print(Fore.RED+"Task Run Error, Please Try Again")
            print(Fore.BLUE + "Sampling stop".upper())
            kill()
            continue

        print(Fore.BLUE+"Sampling stop".upper())
        kill()

        print(Fore.BLUE+"Collecting logs...".upper())
        collect_logs(log_dir)

        print(Fore.BLUE+"Decoding logs...".upper())
        decode(log_dir)

        print(Fore.BLUE+"Analysis Start...".upper())
        res = analysis(log_dir)

        print(Fore.BLUE+"log analysis finished".upper())
        bigroot_cache.set_conf(task_name, dict(time=datetime.now(), desc=describe))
        bigroot_cache.set_task_report(task_name, res)
        bigroot_cache.status[task_name] = 'finished'
        bigroot_cache.store_pickle()

        print(Fore.GREEN+"analysis success!".upper())
        print(Style.DIM+"please open your browser to look your report")
        break


def htrace(session):
    while True:
        print(Fore.YELLOW+"You are in ASTracer mode, please input task name:")
        task_name = session.prompt("ASTracer (task name)> ", auto_suggest=AutoSuggestFromHistory())
        if task_name == "quit":
            break
        print(Fore.YELLOW+"You are in ASTracer mode, please input cmd:")
        cmd = session.prompt("ASTracer (cmd)> ", auto_suggest=AutoSuggestFromHistory())
        print(Fore.BLUE+"Sampling Start".upper())
        res = os.system(cmd)

        # if res != 0:
        #     print(Fore.RED+"Task Run Error, Please Try Again")
        #     print(Fore.BLUE + "Sampling stop".upper())
        #     continue

        print(Fore.BLUE+"Sampling stop".upper())
        print(Fore.BLUE+"Analysis Start...".upper())
        print(Fore.GREEN+"analysis success!".upper())
        print(Style.DIM+"please open your browser to look your report")
        break


def alicloud(session):

    global ali_cache
    slaves_name = get_slaves_name()
    while True:
        ali_cache = alicache.update_from_pickle()
        print(Fore.YELLOW+"You are in AliLoad mode, please set parameters:")
        task_rate = session.prompt("AliLoad (rate)> ", auto_suggest=AutoSuggestFromHistory())
        task_start = session.prompt("AliLoad (start_time)> ", auto_suggest=AutoSuggestFromHistory())
        task_end = session.prompt("AliLoad (end_time)> ", auto_suggest=AutoSuggestFromHistory())

        task_name = "aliload" + "-" + "rate" + "-" + task_rate + "-" + "start" + "-" + task_start + "-" + "end" + "-" +  task_end

        print(Fore.BLUE + "Initializing...".upper())
        log_dir = init_root(task_name)

        print(Fore.BLUE+"Sampling Start".upper())
        for slave in slaves_name:
            t = threading.Thread(target=start_samp_slave, args=(slave, log_dir))
            t.start()

        cmd = "hadoop  jar ../aliload/AliCloud.jar Test.AliCloudLoad " + task_rate + " "  + task_start + " " + task_end
        res = os.system(cmd)

        if res != 0:
            print(Fore.RED+"Task Run Error, Please Try Again")
            print(Fore.BLUE + "Sampling stop".upper())
            kill()
            continue

        print(Fore.BLUE+"Sampling stop".upper())
        kill()

        print(Fore.BLUE+"Collecting logs...".upper())
        collect_load_logs(log_dir)

        print(Fore.BLUE+"Decoding logs...".upper())
        decode(log_dir)
        res = extract_stat(log_dir)
        ali_cache.set_conf(task_name, dict(rate=task_rate, start=task_start, end=task_end, time=datetime.now()))
        ali_cache.set_task_report(task_name, dict(data=res))
        ali_cache.store_pickle()
        print(Fore.YELLOW+"Finished")
        break


def task_opt(session):
    global opt_cache
    slaves_name = get_slaves_name()
    while True:
        opt_cache = optcache.update_from_pickle()
        print(Fore.YELLOW + "You are in TaskOpt mode, please input task name:")
        task_name = session.prompt("TaskOpt (task name)> ", auto_suggest=AutoSuggestFromHistory()).strip()
        jar_path = session.prompt("TaskOpt (jar absolute path)> ", auto_suggest=AutoSuggestFromHistory()).strip()
        main_class = session.prompt("TaskOpt (main class)> ", auto_suggest=AutoSuggestFromHistory()).strip()
        args = session.prompt("TaskOpt (program args)> ", auto_suggest=AutoSuggestFromHistory()).strip()
        times = session.prompt("TaskOpt (Train Data Execute Times)> ", auto_suggest=AutoSuggestFromHistory()).strip()
        model_name = session.prompt("TaskOpt (Model Name[Ext, Xgb])> ", auto_suggest=AutoSuggestFromHistory()).strip()

        print(Fore.BLUE + "Initializing...".upper())
        task_opt_api_init()
        print(Fore.BLUE + "Start...".upper())
        tunecommand, command_args_dict = task_opt_api_main(jar_path, main_class, args, times, model_name)
        if tunecommand is None:
            print(Fore.BLUE + "Program {main_class} lacks load generator program, please connect administrator".format(
                main_class=main_class))
            break
        # 执行优化后的参数
        print(Fore.YELLOW + "ReSubmit {task_name}...".format(task_name=task_name))

        log_dir = init_root("opt_"+task_name)
        print(Fore.BLUE+"Sampling Start".upper())
        for slave in slaves_name:
            t = threading.Thread(target=start_samp_slave, args=(slave, log_dir))
            t.start()

        res = callcommand(tunecommand)

        if res != 0:
            print(Fore.RED+"Task Run Error, Please Try Again")
            print(Fore.BLUE + "Sampling stop".upper())
            kill()
            continue

        print(Fore.BLUE+"Sampling stop".upper())
        kill()

        print(Fore.BLUE+"Collecting logs...".upper())
        collect_load_logs(log_dir)

        print(Fore.BLUE+"Decoding logs...".upper())
        decode(log_dir)
        res = extract_stat(log_dir)

        opt_cache.set_conf(task_name, {
            "class": main_class,
            "train_time": times,
            "model": model_name,
            "time": datetime.now(),
        })

        opt_cache.set_task_report(task_name, dict(data=res, tune=command_args_dict, cmd=tunecommand))
        opt_cache.store_pickle()
        os.system('rm trace*')
        print(Fore.YELLOW+"Finished")
        break

def main():
    init(autoreset=True)
    soft_info = "BigData Analysis Software \nVersion: 1.0\n"
    print(Style.DIM + soft_info)

    introduce = "BigData Analysis Software can be used to analyze big data program performance and visualize the results through the web side.\nThis software has three functions for performance analysis of big data programs, they are:\n"

    print(Fore.CYAN + introduce)
    class_ = "1. BigRoot".center(120, " ") + "\n"
    class_ += "An Effective Approach for Root-cause Analysis of Stragglers in Big Data System".center(120, " ")+"\n\n"
    class_ += "2. SparkTree".center(120, " ") + "\n"
    class_ += "Data Mining Based Root-Cause Analysis of Performance Bottleneck for Big Data Workload".center(120, " ")+" \n\n"
    class_ += "3. ASTracer".center(120, " ") + "\n"
    class_ += "A Fine-grained Performance Bottleneck Analysis Method for HDFS".center(120, " ")+"\n\n"
    class_ += "4. TaskOpt".center(120, " ") + "\n"
    class_ += "A parameter optimization program for Spark".center(120, " ")+"\n\n"
    class_ += "5. AliLoad".center(120, " ") + "\n"
    class_ += "Simulate Alibaba Cloud load".center(120, " ")+"\n\n"
    print(Fore.GREEN + class_)

    tourist = "please type the analysis mode you want e.g: BigRoot, SparkTree, ASTracer; type quit or CTRL+C to EXIT"
    print(Style.DIM + tourist)
    session = PromptSession()

    try:
        while True:
            clean_xml()
            text = session.prompt("mode > ",completer=completer, auto_suggest=AutoSuggestFromHistory())
            if text == 'quit':
                break
            if text == 'BigRoot':
                clean_xml()
                bigroot(session)
            if text == 'SparkTree':
                clean_xml()
                spark(session)
            if text == 'ASTracer':
                htrace(session)
            if text == "AliLoad":
                alicloud(session)
            if text == "TaskOpt":
                task_opt(session)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()