import threading
from straggler.env_conf import *

slaves_name = get_slaves_name()
user = get_user()
master = get_master_name()
cur_path = os.path.dirname(os.path.abspath(__file__))
sample_path = cur_path + '/../../temp/spark/sample/'


def start_iostat(time):
        os.system("iostat -d -x -k 1 "+str(time)+" >> " + sample_path + "iostat_log_"+master+"&")
        for slave in slaves_name:
                os.system("ssh "+user+"@"+slave+" \"iostat -d -x -k 1 "+str(time)+" >> "+slave_path+"/sample/iostat_log_"+slave+"&\"")


def start_mpstat(time):
        os.system("mpstat -P ALL 1 "+str(time)+" >> " + sample_path + "mpstat_log_"+master+"&")
        for slave in slaves_name:
                os.system("ssh "+user+"@"+slave+" \"mpstat -P ALL 1 "+str(time)+" >> "+slave_path+"/sample/mpstat_log_"+slave+"&\"")


def start_sar(time):
        os.system("sar -n DEV 1 "+str(time)+" >> " + sample_path + "sar_log_"+master+"&")
        for slave in slaves_name:
                os.system("ssh "+user+"@"+slave+" \"sar -n DEV 1 "+str(time)+" >> "+slave_path+"/sample/sar_log_"+slave+"&\"")
        

def start_sample(time=5000):
        print('Sampling start ! Sample time = '+str(time)+"s")
        t0 = threading.Thread(target=start_iostat(time))
        t0.start()
        t1 = threading.Thread(target=start_mpstat(time))
        t1.start()
        t2 = threading.Thread(target=start_sar(time))
        t2.start()


def stop_sample():
        os.system("ps aux|grep \"iostat\"|awk \'{print $2}\'|xargs kill $1")
        os.system("ps aux|grep \"mpstat\"|awk \'{print $2}\'|xargs kill $1")
        os.system("ps aux|grep \"sar\"|awk \'{print $2}\'|xargs kill $1")
        for slave in slaves_name:
                os.system("ssh "+user+"@"+slave + " python3 " + slave_path + "/../BigDataBackend/cmd/bigroot/kill_samp.py")
