import os
import sys
sys.path.append('../')
from env_conf import *

slaves_name = get_slaves_name()
user = get_user()

os.system("echo 'Stoping Instrument Listening:'")
for slave in slaves_name:
    os.system("ssh -p 22 "+user+"@"+slave+" \'cd "+slave_path+";\"$BYTEMAN_HOME\"/bin/bmsubmit.sh -u slave_trace.btm\'")