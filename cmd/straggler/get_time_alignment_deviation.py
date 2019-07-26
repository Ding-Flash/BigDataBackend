#/bin/bash
import os
import sys
sys.path.append('..')
from straggler.env_conf import *

slaves_name = get_slaves_name()
user = get_user()
master_ip = get_master_ip()


def ntpdate():
	os.system("sudo ntpdate cn.pool.ntp.org")
	for slave in slaves_name:
		os.system("ssh -p 22 "+user+"@"+slave+" \'echo \"hadoop\" | sudo ntpdate "+master_ip+"\'")



