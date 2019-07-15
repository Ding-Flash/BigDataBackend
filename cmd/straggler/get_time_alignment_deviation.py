#/bin/bash
import os
import sys
sys.path.append('..')
from env_conf import *

slaves_name = get_slaves_name()
user = get_user()
master_ip = get_master_ip()

os.system("sudo ntpdate cn.pool.ntp.org")

for slave in slaves_name:
	os.system("ssh -p 22 "+user+"@"+slave+" \'echo \"hadoop\" | sudo ntpdate "+master_ip+"\'")


#rm /home/hadoop/qwc_trace/time_deviation
#timebase=`echo $[$(date +%s%N)/1000000]`

#for i in {1,6}
#do
#	echo `ssh -p 22 hadoop@slave$i '$[$(date +%s%N)/1000000]'`
#	time_on_slave[$i]=`ssh -p 22 hadoop@slave$i '$[$(date +%s%N)/1000000]'`
#done

#echo 0 >> time_deviation
#echo ${time_on_slave[@]}

#for v in ${time_on_slave[@]}
#do

#	echo $(($timebase-${v})) >> time_deviation
#done


#for ((i=1;i<6;i++))
#do 
#	echo $(($timebase-${time_on_slave[$i]})) >> time_deviation
#done


