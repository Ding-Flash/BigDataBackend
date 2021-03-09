import sys
import os
from datetime import datetime
import threading
import time
import logging
import argparse
import subprocess
import bigroot.root_cause
import bigroot.decoder as decoder
from bigroot.env_conf import *
sys.path.append('../')
from apps.store import bigroot_cache
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
prefix = app_path
master_ip = get_master_ip()
slaves_name = get_slaves_name()


def start_samp_slave(slave,log_dir):
    os.system("ssh "+slave+" python3 "+prefix+"/bigroot/samp_run.py "+log_dir + " >/dev/null 2>&1")
# 去掉异常生成器的调用
# def start_anomaly_slave(slave,last,t,ip):
#     os.system('ssh '+slave+' python3 '+prefix+'anomaly_generator.py -t '+t+' -last '+str(last)+' -tnum '+str(res.tnum)+' ')

# def start_iostat_local():
#     os.system("python "+prefix+"/samp_run.py")
#     time.sleep(100)

# def start_anomaly_local():
#     os.system("python "+prefix+"anomaly_generator.py -disable -ip "+master_ip)
#     time.sleep(100)

# def start_benchmark(cmd):
    ### luice modified
    '''
    检查是否存在 spark 程序，如果存在，运行 spark 程序，否则运行 hadoop 程序
    '''
    # workload_path = benchmark_prefix+name
    # if os.path.exists(workload_path + '/spark'):
    #     os.system(workload_path + '/spark/run.sh')
    # elif os.path.exists(workload_path + '/hadoop'):
    #     os.system(workload_path + '/hadoop/run.sh')
    #########################################################
    # while True:
    #     try:
    #         print(cmd)
    #         subprocess.check_call(cmd, shell=True)
    #         break
    #     except subprocess.CalledProcessError:
    #         logging.info("命令执行失败,请重新输入")
    #         cmd = input()
    #         continue


#    os.system('ssh slave5 \'' + workload_path + '/hadoop/run.sh\'')

def start(res, log_dir):

    print('请输入执行任务的命令')
    cmd = input()
    while True:
        # benchmark=res.name
        pin_ano_start_time=time.time()
        ### luice comment

        for slave in slaves_name:
            t = threading.Thread(target = start_samp_slave,args=(slave,log_dir))
            t.start()

        slaves=res.slaves
        ano_slaves=[]
        if slaves=='all':
            ano_slaves=slaves_name
        elif slaves=='':
            pass
        else:
            ano_slaves.extend(slaves.split())
        # 去掉异常生成器的调用
        # for i in ano_slaves:
        #     t = threading.Thread(target = start_anomaly_slave,args=(i,res.last,res.ano,res.ip))
        #     t.start()
        logging.info('ready to start workload,timestamp='+str(time.time()))
        pin_benchmark_start_time=time.time()
        try:
            subprocess.check_call(cmd, shell=True)
            break
        except subprocess.CalledProcessError:
            logging.info("命令执行失败,请重新输入")
            cmd = input()
            continue
    # start_benchmark(cmd)
    logging.info('benchmark done! timestamp='+str(time.time()))
    logging.info('ready to collect logs')
    pin_benmark_end_time=time.time()
    collect_logs(log_dir)
    pin_collect_log_time=time.time()
    kill()
    decode(log_dir)

    pin_end_time=time.time()
    with open(prefix+'/bigroot/experiment/overhead','w') as d:
        d.write('%.3f %.3f %.3f %.3f %.3f %.3f'%(pin_global_init_time-pin_global_start_time,pin_ano_start_time-pin_global_init_time,
            pin_benchmark_start_time-pin_ano_start_time,pin_benmark_end_time-pin_benchmark_start_time,pin_collect_log_time-pin_benmark_end_time,
            pin_end_time-pin_collect_log_time)+'\n')
    # get application duration
    for file in os.listdir(log_dir+"/out"):
        if file.startswith('app'):
            app=log_dir+"/out"+file

    # luice comment
    '''
    import job_time
    print('spark log file:',app)
    start_time,end_time=job_time.job_time(app)
    print('\n+---------------------------------------------------------------+')
    print('\tjob time:',end_time-start_time,'delay:',start_time-pin_ano_start_time)
    print('+---------------------------------------------------------------+\n')
    with open(res.job_time_file,'a') as f:
        f.write(str(end_time-start_time)+'\n')
    with open('out/delay','w') as f:
        f.write(str(start_time-pin_ano_start_time))
    time.sleep(5)
    os.system("ps aux|grep \"anomaly_generator.py\"|awk \'{print $2}\'|xargs kill $1")
    print('\033[32m[INFO] Application analysis...\033[0m')
    '''


def collect_logs(log_dir):
    os.system("cp $SPARK_HOME/tsee_log/* "+log_dir+"/logs")
    os.system("cp "+log_dir+"/logs/app* "+log_dir+"/out")
    for slave in slaves_name:
        os.system("scp "+slave+":"+log_dir+"/logs/iostat_log_master "+log_dir+"/logs/iostat_log_"+slave)

    for slave in slaves_name:
        os.system("scp "+slave+":"+log_dir+"/logs/vmstat_log_master "+log_dir+"/logs/vmstat_log_"+slave)

    for slave in slaves_name:
        os.system("scp "+slave+":"+log_dir+"/logs/mpstat_log_master "+log_dir+"/logs/mpstat_log_"+slave)

    for slave in slaves_name:
        os.system("scp "+slave+":"+log_dir+"/logs/sar_log_master "+log_dir+"/logs/sar_log_"+slave)

    # for slave in slaves_name:
    #     os.system("scp "+slave+":"+log_dir+"/logs/anomaly_log.txt "+log_dir+"/logs/anomaly_"+slave)


def collect_load_logs(log_dir):
    for slave in slaves_name:
        os.system("scp "+slave+":"+log_dir+"/logs/iostat_log_master "+log_dir+"/logs/iostat_log_"+slave)

    for slave in slaves_name:
        os.system("scp "+slave+":"+log_dir+"/logs/vmstat_log_master "+log_dir+"/logs/vmstat_log_"+slave)

    for slave in slaves_name:
        os.system("scp "+slave+":"+log_dir+"/logs/mpstat_log_master "+log_dir+"/logs/mpstat_log_"+slave)

    for slave in slaves_name:
        os.system("scp "+slave+":"+log_dir+"/logs/sar_log_master "+log_dir+"/logs/sar_log_"+slave)


def init_root(work_dir):
    log_dir = prefix + "/temp/bigroot/" + work_dir
    if os.path.exists(log_dir):
        os.system("rm "+log_dir+"/logs/* "+log_dir+"/out/* bigroot/experiment/* >/dev/null 2>&1")
    else:
        os.system("mkdir -p "+log_dir+"/logs "+log_dir+"/out")
    for slave in slaves_name:
        os.system("ssh "+slave+" python "+prefix+"/bigroot/kill_samp.py >/dev/null 2>&1")

    # os.system("rm $SPARK_HOME/tsee_log/* >/dev/null 2>&1")
    logging.info('clear old logs in salves')
    for slave in slaves_name:
        os.system("ssh "+slave+" mkdir -p " + log_dir + "/logs " + log_dir + "/out")
        os.system("ssh "+slave+" rm " + log_dir + "/logs/* " + log_dir + "/out/* bigroot/experiment/* >/dev/null 2>&1")

    return log_dir


def decode(log_dir):
    # os.system("cp "+log_dir+"/logs/anomaly* "+log_dir+"/out")
    for slave in slaves_name:
        decoder.decode_sar(slave,log_dir)
    for slave in slaves_name:
        decoder.decode_mpstat(slave,log_dir)
    for slave in slaves_name:
        decoder.decode_iostat(slave,log_dir)


def kill():
    for slave in slaves_name:
        os.system("ssh "+slave+" python "+prefix+"/bigroot/kill_samp.py >/dev/null 2>&1")


parser=argparse.ArgumentParser()
# parser.add_argument('-run',action='store_true',help='run the whole system')
# parser.add_argument('-name',type=str,default='micro/wordcount',help='specify benchmark name')
parser.add_argument('-collect',action='store_true',help='collect logs from slaves')
parser.add_argument('-decode',action='store_true',help='decode logs')
parser.add_argument('-last',type=int,default=30,help='specify anomaly last time')
parser.add_argument('-ano',type=str,default='cpu',help='choices are cpu, io, net, all')
parser.add_argument('-slaves',type=str,default='all',help='slaves to generate anomaly')
parser.add_argument('-ip',type=str,default='10.254.13.16',help='connect particular ip address')
parser.add_argument('-job_time_file',type=str,default='info',help='dump job duration info to this file')
parser.add_argument('-tnum',type=int,default='32',help='thread num to start')
res=parser.parse_args()


if __name__ == '__main__':
    ### luice comment
    while True:
        logging.info('请为任务命名')
        task_name = input()
        # if bigroot_cache.get_task_report(task_name):
        #     print("task_name existed")
        #     continue
        pin_global_start_time=time.time()
        logging.info('init system status')
        log_dir = init(task_name)
        pin_global_init_time=time.time()
        start(res, log_dir)
        res = bigroot.root_cause.analysis(log_dir)
        bigroot_cache.set_conf(task_name, dict(time=datetime.now()))
        bigroot_cache.set_task_report(task_name, res)
        bigroot_cache.status[task_name] = 'finished'
        bigroot_cache.store_pickle()
        break

# luice comment
'''
if res.collect:
    collect_logs()
    decode()
    kill()
if res.decode:
    decode()
'''
