import os
import sys
sys.path.append('..')
from env_conf import *

cur = os.path.dirname(os.path.abspath(__file__))
slaves_name = get_slaves_name()
user = get_user()

os.system("rm {}/iostat_log_*".format(cur))
os.system("rm {}/out_log/iostat_out_*".format(cur))
os.system("rm {}/mpstat_log_*".format(cur))
os.system("rm {}/out_log/mpstat_out_*".format(cur))
os.system("rm {}sar_log_*".format(cur))
os.system("rm {}out_log/sar_out_*".format(cur))

for slave in slaves_name:
    os.system("ssh "+user+"@"+slave+" \"rm "+slave_path+"/sample/iostat_log_"+slave+"&\"")

for slave in slaves_name:
    os.system("ssh "+user+"@"+slave+" \"rm "+slave_path+"/sample/mpstat_log_"+slave+"&\"")

for slave in slaves_name:
    os.system("ssh "+user+"@"+slave+" \"rm "+slave_path+"/sample/sar_log_"+slave+"&\"")
