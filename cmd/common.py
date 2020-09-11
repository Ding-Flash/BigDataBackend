from bigroot.env_conf import get_slaves_name, app_path
import numpy as np
import os

def extract_iostat(slaves,log_dir):
    slaves_ior = []
    slaves_iow = []
    for slave in slaves:
        ior = []
        iow = []
        file = log_dir+"/out/iostat_out_"+slave
        with open(file) as f:
            line = f.readline()
            while line:
                ios = line.split()
                ior.append(ios[5])
                iow.append(ios[6])
                line = f.readline()
        slaves_ior.append(ior)
        slaves_iow.append(iow)
    return slaves_ior, slaves_iow


def extract_mpstat(slaves, log_dir):
    slaves_cpu = []
    for slave in slaves:
        cpu = []
        file = log_dir+ "/out/mpstat_out_"+slave
        with open(file) as f:
            line = f.readline()
            while line:
                cpus = line.split()
                cpu.append(cpus[1])
                line = f.readline()
        slaves_cpu.append(cpu)
    return slaves_cpu


def extract_sar(slaves, log_dir):
    slaves_rx = []
    slaves_tx = []
    for slave in slaves:
        rx = []
        tx = []
        file = log_dir + "/out/sar_out_"+slave
        with open(file) as f:
            line = f.readline()
            while line:
                nets = line.split()
                rx.append(nets[1])
                tx.append(nets[2])
                line = f.readline()
        slaves_rx.append(rx)
        slaves_tx.append(tx)
    return slaves_rx, slaves_tx


def extract_stat(log_dir):
    slaves = get_slaves_name()
    slaves_ior, slaves_iow = extract_iostat(slaves, log_dir)
    slaves_cpu = extract_mpstat(slaves, log_dir)
    slaves_rx, slaves_tx = extract_sar(slaves, log_dir)

    res = []
    for i in range(len(slaves)):
        len_time = max(len(slaves_ior[i]), len(slaves_cpu[i]), len(slaves_rx[i]))
        if len(slaves_ior[i]) < len_time:
            slaves_ior[i] += [0]*(len_time-len(slaves_ior[i]))
            slaves_iow[i] += [0]*(len_time-len(slaves_iow[i]))
        if len(slaves_cpu[i]) < len_time:
            slaves_cpu[i] += [0]*(len_time-len(slaves_cpu[i]))
        if len(slaves_rx[i]) < len_time:
            slaves_rx[i] += [0]*(len_time-len(slaves_rx[i]))
            slaves_tx[i] += [0]*(len_time-len(slaves_tx[i]))


        item = {
            "host": slaves[i],
            "ior": normalization(slaves_ior[i]),
            "iow": normalization(slaves_iow[i]),
            "cpu": normalization(slaves_cpu[i]),
            "net_rx": normalization(slaves_rx[i]),
            "net_tx": normalization(slaves_tx[i]),
            "time": len_time
        }
        res.append(item)
    return res


def normalization(data):
    data = np.array(data).astype(np.float)
    _range = np.max(data) - np.min(data)
    res = (data - np.min(data)) / _range
    return res.tolist()