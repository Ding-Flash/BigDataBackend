import os
from env_conf import *

slaves_name = get_slaves_name()
user = get_user()


def clean_sample_log():
    cur = os.path.dirname(os.path.abspath(__file__))
    slaves_name = get_slaves_name()
    user = get_user()

    os.system("rm {}/sample/iostat_log_*".format(cur))
    os.system("rm {}/sample/out_log/iostat_out_*".format(cur))
    os.system("rm {}/sample/mpstat_log_*".format(cur))
    os.system("rm {}/sample/out_log/mpstat_out_*".format(cur))
    os.system("rm {}/sample/sar_log_*".format(cur))
    os.system("rm {}/sample/out_log/sar_out_*".format(cur))

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/iostat_log_" + slave + "&\"")

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/mpstat_log_" + slave + "&\"")

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/sar_log_" + slave + "&\"")


os.system("rm tracelog_*")
os.system("rm task_tracelog_*")

os.system("rm trace*")

# os.system("python3 ./sample/clean_sample_log.py")
clean_sample_log()

os.system("rm app*")

os.system("rm $SPARK_HOME/tsee_log/app*")

os.system("rm analysis/app_info")
os.system("rm analysis/app_task")
os.system("rm analysis/app_straggler")

os.system("rm analysis/straggler_stack")
os.system("rm straggler_stack")

os.system("rm analysis/atree.dot")
os.system("rm atree.dot")



for slave in slaves_name:
    os.system("ssh -p 22 "+user+"@"+slave+" \'cd "+slave_path+";rm tracelog; rm task_tracelog\'")


