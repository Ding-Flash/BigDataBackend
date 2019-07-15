import time
import threading
import os
import sys
sys.path.append('..')
from env_conf import *

slaves_name = get_slaves_name()
user = get_user()
master = get_master_name()
def start_iostat(time):
    
        os.system("iostat -d -x -k 1 "+str(time)+" >> iostat_log_"+master+"&")
        for slave in slaves_name:
                os.system("ssh "+user+"@"+slave+" \"iostat -d -x -k 1 "+str(time)+" >> "+slave_path+"/sample/iostat_log_"+slave+"&\"")

# def start_vmstat_local(time):
# 	os.system("vmstat 1 5400 >> ~/samp_log/vmstat_log_master")

def start_mpstat(time):

        os.system("mpstat -P ALL 1 "+str(time)+" >> mpstat_log_"+master+"&")
        for slave in slaves_name:
                os.system("ssh "+user+"@"+slave+" \"mpstat -P ALL 1 "+str(time)+" >> "+slave_path+"/sample/mpstat_log_"+slave+"&\"")

def start_sar(time):

        os.system("sar -n DEV 1 "+str(time)+" >> sar_log_"+master+"&")
        for slave in slaves_name:
                os.system("ssh "+user+"@"+slave+" \"sar -n DEV 1 "+str(time)+" >> "+slave_path+"/sample/sar_log_"+slave+"&\"")
        

def main(time):

        print('Sampling start ! Sample time = '+str(time)+"s")
        t0 = threading.Thread(target = start_iostat(time))
        t0.start()
        #t1 = threading.Thread(target = start_vmstat_local)
        #t1.start()
        t1 = threading.Thread(target = start_mpstat(time))
        t1.start()
        t2 = threading.Thread(target = start_sar(time))
        t2.start()


main(sys.argv[1])
