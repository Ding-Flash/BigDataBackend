import os
import sys
sys.path.append('..')
from env_conf import *

slaves_name = get_slaves_name()
user = get_user()

for slave in slaves_name:
    os.system("scp "+user+"@"+slave+":"+slave_path+"/sample/iostat_log_"+slave+" iostat_log_"+slave)

for slave in slaves_name:
    os.system("scp "+user+"@"+slave+":"+slave_path+"/sample/mpstat_log_"+slave+" mpstat_log_"+slave)

for slave in slaves_name:
    os.system("scp "+user+"@"+slave+":"+slave_path+"/sample/sar_log_"+slave+" sar_log_"+slave)




