import os
import sys
import logging
import threading
from env_conf import *
prefix = app_path
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_iostat_local(log_dir):
    os.system("iostat -d -x -k 1 5400 >> " +log_dir+"/logs/iostat_log_master")

def start_vmstat_local(log_dir):
    os.system("vmstat 1 5400 >> " +log_dir+"/logs/vmstat_log_master")

def start_mpstat_local(log_dir):
    os.system("mpstat -P ALL 1 5400 >> " +log_dir+"/logs/mpstat_log_master")

def start_sar_local(log_dir):
    os.system("sar -n DEV 1 5400 >> " +log_dir+"/logs/sar_log_master")

def main(log_dir):
    logging.info('Sampling start')
    t0 = threading.Thread(target=start_iostat_local,args={log_dir,})
    t0.start()
    t1 = threading.Thread(target=start_vmstat_local,args={log_dir,})
    t1.start()
    t2 = threading.Thread(target=start_mpstat_local,args={log_dir,})
    t2.start()
    t3 = threading.Thread(target=start_sar_local,args={log_dir,})
    t3.start()

main(sys.argv[1])
