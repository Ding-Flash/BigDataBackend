import os
import subprocess
import logging
import argparse
from datetime import datetime

from straggler import clean_all, get_time_alignment_deviation, get_trace_log, merge

from straggler.sample import samp_run, get_logs, log_exe
from straggler.analysis import engine, decode_dot, do_straggler

from apps.store import spark_cache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='')


def main():

    task_name = None

    while True:
        logging.info("请给执行任务指定一个任务名称")
        task_name = input()
        if spark_cache.get_task_report(task_name):
            logging.info("任务名称已经存在")
            continue
        break

    while True:
        logging.info("请输入执行任务指令")
        cmd = input()

        # - CLEAN WORK -
        logger.info("删除过期文件")
        clean_all.clean_sample_log()

        # - Time Alignment -
        logger.info("集群时间校准")
        get_time_alignment_deviation.ntpdate()

        # - Sample SYS Info -
        logging.info("开始系统信息采集")
        samp_run.start_sample()

        # - Start Workload -
        logging.info("开始启动程序")

        # try:
        #     subprocess.check_call(cmd, shell=True)
        # except subprocess.CalledProcessError:
        #     logging.info("指令执行失败,请重新输入")
        #     continue

        os.system(cmd)

        samp_run.stop_sample()

        # - Get Logs -
        logging.info("收集spark日志")
        try:
            spark_home = os.environ['SPARK_HOME']
        except KeyError:
            logging.info("请设置SPARK_HOME环境变量")
            continue

        try:
            cur_path = os.path.dirname(os.path.abspath(__file__))
            collect_log_cmd = "cp " + spark_home + '/tsee_log/app* ' + cur_path + '/temp/spark/app'
            logging.info(collect_log_cmd)
            subprocess.check_call(collect_log_cmd, shell=True)
        except subprocess.CalledProcessError:
            logging.info("日志收集失败")
            continue

        try:
            get_trace_log.collect_trace_log()
        except Exception:
            pass

        # 收集来自slave的sys信息
        logging.info("收集来自slave的sys信息")
        get_logs.get_sys_log()

        # - ANALYSIS -
        log_exe.analysis_log()
        engine.start_analysis()
        decode_dot.decode_tree()
        do_straggler.detect()

        # - Write Report -
        report = merge.analysis_store()
        spark_cache.set_conf(task_name, dict(time=datetime.now()))
        spark_cache.set_task_report(task_name, report)
        spark_cache.status[task_name] = 'finished'
        spark_cache.store_pickle()
        break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("任务终止")
