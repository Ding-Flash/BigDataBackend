#$1 workload
#$2 sampler
#$3 times
import sys
import os
import time
import re


hadoop_home = os.environ['HADOOP']
conf_path = hadoop_home+'/etc/hadoop'
workload_path = '~/env/hibench/bin/workloads'
trace_path_r = '~/trace' 
report_path = '/home/yangs/env/hibench/report/hibench.report'

path = {
        'wordcount':workload_path+'/micro/wordcount',
        'sort':workload_path+'/micro/sort',
        'terasort':workload_path+'/micro/terasort',
        'dfsioe_r':workload_path+'/micro/dfsioe',
        'dfsioe_w':workload_path+'/micro/dfsioe',
        'kmeans':workload_path+'/ml/kmeans',
        'pagerank':workload_path+'/websearch/pagerank',
        }

trace_path = {
        'wordcount':trace_path_r+'/wordcount',
        'sort':trace_path_r+'/sort',
        'terasort':trace_path_r+'/terasort',
        'dfsioe_r':trace_path_r+'/dfsioe_r',
        'dfsioe_w':trace_path_r+'/dfsioe_w',
        'kmeans':trace_path_r+'/kmeans',
        'pagerank':trace_path_r+'/pagerank',
        }

def t(i):
    with open(report_path) as f:
        line = f.readlines()[-1]
        temp = line.split(' ')
        res = [t for t in temp if t!= '']
        return res[i]
def mean():
    with open('/home/yangs/trace/'+sys.argv[1]+'/'+sys.argv[2]+'/trace.log','a+') as f:
        lines = f.readlines()
        mean_time = 0
        mean_through = 0
        for line in lines:
            temp = line.split(' ')
            res = [t for t in temp if t!= '']
            mean_time += float(res[3])/len(lines)
            mean_through += float(res[4])/len(lines)
        f.write('meantime: '+str(mean_time)+' meanthrough: '+str(mean_through)+'\n')

def run(bench,n):
    if(n == 0 and int(sys.argv[3]) == 0):
        os.system(path[bench]+'/prepare/prepare.sh')
        time.sleep(1)
        os.system('rm '+trace_path_r+'/htrace.out')
    if(n != 0):
        os.system(path[bench]+'/hadoop/run.sh')
        time.sleep(2)
        os.system('mkdir -p '+trace_path[bench]+'/'+sys.argv[2])
        os.system('mv '+trace_path_r+'/htrace.out '+trace_path[bench]+'/'+sys.argv[2]+'/'+str(n)+'.out')
        with open('/home/yangs/trace/'+bench+'/'+sys.argv[2]+'/trace.log','a+') as f:
            f.write(bench+' '+sys.argv[2]+' '+str(n)+' '+str(t(4))+' '+str(t(5))+'\n')
def main():
    os.system('rm '+trace_path[sys.argv[1]]+'/'+sys.argv[2]+'/trace.log')
    for i in range(int(sys.argv[3])+1):
        run(sys.argv[1],i)
    mean()

if __name__ == '__main__':
    main()

#sort p0.1 wordcount p0.1