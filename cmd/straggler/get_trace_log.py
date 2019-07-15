#/bin/bash
import os
import sys
sys.path.append('..')
from env_conf import *

slaves_name = get_slaves_name()
user = get_user()

for slave in slaves_name:
    os.system("scp "+user+"@"+slave+":"+slave_path+"/tracelog ./tracelog_"+slave)

for slave in slaves_name:
    os.system("scp "+user+"@"+slave+":"+slave_path+"/task_tracelog ./task_tracelog_"+slave)

