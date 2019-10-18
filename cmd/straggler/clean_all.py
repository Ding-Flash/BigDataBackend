from straggler.env_conf import *

slaves_name = get_slaves_name()
user = get_user()


def clean_sample_log():
    cur = os.path.dirname(os.path.abspath(__file__)) + "/../temp/spark/"
    slaves_name = get_slaves_name()
    user = get_user()

    os.system("rm {}task_data >/dev/null 2>&1".format(cur))
    os.system("rm {}op_data >/dev/null 2>&1".format(cur))
    os.system("rm {}Trace_time* >/dev/null 2>&1".format(cur))
    os.system("rm {}sample/iostat_log_* >/dev/null 2>&1".format(cur))
    os.system("rm {}sample/out_log/iostat_out_* >/dev/null 2>&1".format(cur))
    os.system("rm {}sample/mpstat_log_* >/dev/null 2>&1".format(cur))
    os.system("rm {}sample/out_log/mpstat_out_* >/dev/null 2>&1".format(cur))
    os.system("rm {}sample/sar_log_* >/dev/null 2>&1".format(cur))
    os.system("rm {}sample/out_log/sar_out_* >/dev/null 2>&1".format(cur))

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/iostat_log_" + slave + " >/dev/null 2>&1 &\"")

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/mpstat_log_" + slave + "  >/dev/null 2>&1 &\"")

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/sar_log_" + slave + " >/dev/null 2>&1 &\"")

    os.system("rm {}tracelog_* >/dev/null 2>&1".format(cur))
    os.system("rm {}task_tracelog_* >/dev/null 2>&1".format(cur))

    # os.system("rm {}trace*".format(cur))

    os.system("rm {}app* >/dev/null 2>&1".format(cur))

    os.system("rm $SPARK_HOME/tsee_log/app* >/dev/null 2>&1")

    # os.system("rm " + cur + "/analysis/app_info")
    # os.system("rm " + cur + "/analysis/app_task")
    # os.system("rm " + cur + "/analysis/app_straggler")

    # os.system("rm " + cur + "/analysis/straggler_stack")
    os.system("rm {}straggler_stack >/dev/null 2>&1".format(cur))

    os.system("rm {}analysis/atree.dot >/dev/null 2>&1".format(cur))
    os.system("rm {}analysis/dataset.dat >/dev/null 2>&1".format(cur))
    # os.system("rm {}atree.dot".format(cur))

    for slave in slaves_name:
        os.system("ssh -p 22 "+user+"@"+slave+" \'cd "+slave_path+";rm tracelog; rm task_tracelog >/dev/null 2>&1\'")


