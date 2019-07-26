import os
from straggler.env_conf import get_slaves_name, get_user, slave_path

slaves_name = get_slaves_name()
user = get_user()
cur_path = os.path.dirname(os.path.abspath(__file__))
sample_path = cur_path + '/../../temp/spark/sample/'


def get_sys_log():
    for slave in slaves_name:
        cmd = "scp "+user+"@"+slave+":"+slave_path+"/sample/iostat_log_"+slave+ " " + sample_path + "iostat_log_"+slave
        print(cmd)
        os.system(cmd)

    for slave in slaves_name:
        cmd = "scp "+user+"@"+slave+":"+slave_path+"/sample/mpstat_log_"+slave+ " " + sample_path + "mpstat_log_"+slave
        print(cmd)
        os.system(cmd)

    for slave in slaves_name:
        cmd = "scp "+user+"@"+slave+":"+slave_path+"/sample/sar_log_"+slave+ " " + sample_path + "sar_log_"+slave
        print(cmd)
        os.system(cmd)




