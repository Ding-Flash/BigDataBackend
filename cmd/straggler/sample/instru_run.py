import os
import sys
sys.path.append('../')
from env_conf import *

slaves_name = get_slaves_name()
user = get_user()

os.system("echo 'Starting Instrument Listening:'")
for slave in slaves_name:
    print(slave)
    os.system("ssh -p 22 "+user+"@"+slave+" \'cd "+slave_path+"; ./run_instrument.sh&\'")
