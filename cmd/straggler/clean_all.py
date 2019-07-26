from straggler.env_conf import *

slaves_name = get_slaves_name()
user = get_user()


def clean_sample_log():
    cur = os.path.dirname(os.path.abspath(__file__)) + "/../temp/spark/"
    slaves_name = get_slaves_name()
    user = get_user()

    os.system("rm {}task_data".format(cur))
    os.system("rm {}op_data".format(cur))
    os.system("rm {}Trace_time*".format(cur))
    os.system("rm {}sample/iostat_log_*".format(cur))
    os.system("rm {}sample/out_log/iostat_out_*".format(cur))
    os.system("rm {}sample/mpstat_log_*".format(cur))
    os.system("rm {}sample/out_log/mpstat_out_*".format(cur))
    os.system("rm {}sample/sar_log_*".format(cur))
    os.system("rm {}sample/out_log/sar_out_*".format(cur))

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/iostat_log_" + slave + "&\"")

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/mpstat_log_" + slave + "&\"")

    for slave in slaves_name:
        os.system("ssh " + user + "@" + slave + " \"rm " + slave_path + "/sample/sar_log_" + slave + "&\"")

    os.system("rm {}tracelog_*".format(cur))
    os.system("rm {}task_tracelog_*".format(cur))

    # os.system("rm {}trace*".format(cur))

    os.system("rm {}app*".format(cur))

    os.system("rm $SPARK_HOME/tsee_log/app*")

    # os.system("rm " + cur + "/analysis/app_info")
    # os.system("rm " + cur + "/analysis/app_task")
    # os.system("rm " + cur + "/analysis/app_straggler")

    # os.system("rm " + cur + "/analysis/straggler_stack")
    os.system("rm {}straggler_stack".format(cur))

    os.system("rm {}analysis/atree.dot".format(cur))
    os.system("rm {}analysis/dataset.dat".format(cur))
    # os.system("rm {}atree.dot".format(cur))

    for slave in slaves_name:
        os.system("ssh -p 22 "+user+"@"+slave+" \'cd "+slave_path+";rm tracelog; rm task_tracelog\'")


