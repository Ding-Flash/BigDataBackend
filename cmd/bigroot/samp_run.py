import os
import threading
from env_conf import *
prefix = app_path

def start_iostat_local():
    os.system("iostat -d -x -k 1 5400 >> " + prefix + "/temp/bigroot/logs/iostat_log_master")

def start_vmstat_local():
    os.system("vmstat 1 5400 >> " + prefix + "/temp/bigroot/logs/vmstat_log_master")

def start_mpstat_local():
    os.system("mpstat -P ALL 1 5400 >> " + prefix + "/temp/bigroot/logs/mpstat_log_master")

def start_sar_local():
    os.system("sar -n DEV 1 5400 >> " + prefix + "/temp/bigroot/logs/sar_log_master")

def main():
    print('Sampling start')
    t0 = threading.Thread(target=start_iostat_local)
    t0.start()
    t1 = threading.Thread(target=start_vmstat_local)
    t1.start()
    t2 = threading.Thread(target=start_mpstat_local)
    t2.start()
    t3 = threading.Thread(target=start_sar_local)
    t3.start()

main()
