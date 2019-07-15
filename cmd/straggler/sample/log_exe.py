import re
import os
import sys
sys.path.append('..')
from env_conf import *

slaves_name = get_slaves_name()
master = get_master_name()

#rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   wait r_await w_await  svctm  %util


def do_refine_iostat(iostatfile, outfile):
    time_count = []
    rrgm = []
    wrgm = []
    rs = []
    ws = []
    rkb = []
    wkb = []
    avgrq = []
    avgqu = []
    wait = []
    # rawait = []
    # wawait = []
    # svctm = []
    util = []

    line = iostatfile.readline()

    count = -1

    while line:
        if 'sda' in line:
            linedata = re.findall(r'[0-9]+\.?[0-9]*',line)
            # if linedata and len(linedata) == 13 :

            count = count + 1
            time_count.append(str(count))
            rrgm.append(linedata[0])
            wrgm.append(linedata[1])
            rs.append(linedata[2])
            ws.append(linedata[3])
            rkb.append(linedata[4])
            wkb.append(linedata[5])
            avgrq.append(linedata[6])
            avgqu.append(linedata[7])
            wait.append(linedata[8])
            # rawait.append(linedata[9])
            # wawait.append(linedata[10])
            # svctm.append(linedata[11])
            util.append(linedata[-1])
			

        line = iostatfile.readline()	

	
    for i in range(0,count):
	    outline = [time_count[i],' ',rrgm[i],' ',wrgm[i],' ',rs[i],' ',ws[i],' ',rkb[i],' ',wkb[i],' ',avgrq[i],' ',avgqu[i],' ',wait[i],' ',
        # rawait[i],' ',wawait[i],' ',svctm[i],' ',
        util[i],'\n']
	    outfile.writelines(outline)	


def do_refine_mpstat(mpfile, outfile):
    mpstat = {}
    mpstat['time_stp_all'] = []
    mpstat['user_all'] = []
    mpstat['nice_all'] = []
    mpstat['sys_all'] = []
    mpstat['iowait_all'] = []
    mpstat['irq_all'] = []
    mpstat['soft_all'] = []
    mpstat['steal_all'] = []
    mpstat['guest_all'] = []
    #mpstat['gnice_all'] = []
    mpstat['idle_all'] = []

    line = mpfile.readline()
    while line:
        if 'CPU' in line and 'usr' in line:
            keys = line.split()
            break
        line = mpfile.readline()
    line_num = 1
    count = -1
    while line:
        line_list = line.split()
        if  len(line_list) == len(keys) and 'all' in line and line_num < 10000: # ALL
            mpstat['time_stp_all'].append(str(count+1))
            mpstat['user_all'].append(line_list[keys.index('%usr')])
            mpstat['nice_all'].append(line_list[keys.index('%nice')])
            mpstat['sys_all'].append(line_list[keys.index('%sys')])
            mpstat['iowait_all'].append(line_list[keys.index('%iowait')])
            mpstat['irq_all'].append(line_list[keys.index('%irq')])
            mpstat['soft_all'].append(line_list[keys.index('%soft')])
            mpstat['steal_all'].append(line_list[keys.index('%steal')])
            mpstat['guest_all'].append(line_list[keys.index('%guest')])
            #mpstat['gnice_all'].append(line_list[keys.index('%gnice')])
            mpstat['idle_all'].append(line_list[keys.index('%idle')])
            count = count + 1
        line_num = line_num + 1
        line = mpfile.readline()

    for i in range(0,count):
        outline = [mpstat['time_stp_all'][i],' ',mpstat['user_all'][i],' ',mpstat['nice_all'][i],' ', mpstat['sys_all'][i],' ',mpstat['iowait_all'][i],' ',
                    mpstat['irq_all'][i],' ',mpstat['soft_all'][i],' ',mpstat['steal_all'][i],' ',mpstat['guest_all'][i],' ',
                    #mpstat['gnice_all'][i],' ',
                    mpstat['idle_all'][i],'\n']
        
        outfile.writelines(outline)


def do_refine_sar(sarfile, outfile):
    sar = {}
    sar['time_stp_all'] = []
    sar['rxkb_all'] = []
    sar['txkb_all'] = []
    sar['ifutil_all'] = []
    line = sarfile.readline().split()
    while line:
        if 'IFACE' in line and 'rxpck/s' in line:
            keys = line.split()
            break
        line = sarfile.readline()

    line_num = 1
    count = -1
    line = sarfile.readline()
    while line:
        line_list = line.split()
        if len(line_list) == len(keys) and ('IFACE' not in line) and (line_list[keys.index('rxkB/s')] != '0.00') and (line_list[keys.index('txkB/s')] != '0.00'): # eth0
            sar['time_stp_all'].append(str(count+1))
            sar['rxkb_all'].append(line_list[keys.index('rxkB/s')])
            sar['txkb_all'].append(line_list[keys.index('txkB/s')])
            sar['ifutil_all'].append('0.00')
            count = count + 1
        line_num = line_num + 1
        line = sarfile.readline()
    for i in range(0,count):
        outline = [sar['time_stp_all'][i],' ',sar['rxkb_all'][i],' ',sar['txkb_all'][i],' ',sar['ifutil_all'][i],'\n']
        outfile.writelines(outline)

iostatfile = open("iostat_log_"+master,"r")
outfile = open("out_log/iostat_out_"+master,"w")
do_refine_iostat(iostatfile,outfile)
iostatfile.close()
outfile.close()

mpstatfile = open("mpstat_log_"+master,"r")
outfile = open("out_log/mpstat_out_"+master,"w")
do_refine_mpstat(mpstatfile, outfile)
mpstatfile.close()
outfile.close()

sarfile = open("sar_log_"+master,"r")
outfile = open("out_log/sar_out_"+master,"w")
do_refine_sar(sarfile, outfile)
sarfile.close()
outfile.close()

for slave in slaves_name:
    iostatfile = open("iostat_log_"+slave,"r")
    outfile = open("out_log/iostat_out_"+slave,"w")
    do_refine_iostat(iostatfile,outfile)
    iostatfile.close()
    outfile.close()

    mpstatfile = open("mpstat_log_"+slave,"r")
    outfile = open("out_log/mpstat_out_"+slave,"w")
    do_refine_mpstat(mpstatfile,outfile)
    mpstatfile.close()
    outfile.close()

    sarfile = open("sar_log_"+slave,"r")
    outfile = open("out_log/sar_out_"+slave,"w")
    do_refine_sar(sarfile, outfile)
    sarfile.close()
    outfile.close()



