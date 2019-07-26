import os
import sys
sys.path.append('..')
from straggler.env_conf import get_slaves_name, get_user, slave_path

slaves_name = get_slaves_name()
user = get_user()

cur_path = os.path.dirname(os.path.abspath(__file__)) + "/../temp/spark/"


def collect_trace_log():
    for slave in slaves_name:
        cmd = "scp "+user+"@"+slave+":"+slave_path+"/tracelog " + cur_path +"tracelog_"+slave
        print(cmd)
        os.system(cmd)

    for slave in slaves_name:
        cmd = "scp "+user+"@"+slave+":"+slave_path+"/task_tracelog " + cur_path + "task_tracelog_"+slave
        print(cmd)
        os.system(cmd)

