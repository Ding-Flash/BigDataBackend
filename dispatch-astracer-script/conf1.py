#encoding:utf-8
import xmltodict as xd 
import os

file = os.environ['HADOOP'] + "/etc/hadoop/core-site.xml"

sampler_map = {
    '1': "AlwaysSampler",
    '2': 'ProbabilitySampler',
    '3': 'LimitSampler',
    '5': 'TBucketSampler',
    '0': '不使用采样器'
}

conf_map = {}

def find_name(target):
    for idx, t in enumerate(target):
        conf_map[t['name']] = idx

def deploy_conf():
    with open(file) as f:
        res = f.read()
    conf = xd.parse(res)
    s = input("请输入采样器类型: \n 1. AlwaysSampler \n 2. ProbabilitySampler \n 3. LimitSampler\n 0. none  \n 5. TBucketSampler \n")
    sampler = sampler_map[s]
    target = conf['configuration']['property']
    find_name(target)
    if s == '0':
        target[conf_map['hadoop.htrace.sampler.classes']]['value'] = ''
    if s == '2':
        p = input('请输入概率P 默认为0.1 \nP:')
        p = 0.1 if p == '' else float(p)
        target[conf_map['hadoop.htrace.sampler.fraction']]['value'] = p
    elif s == '3':
        n = input("请输入每秒限制次数N 默认为100 \nN:")
        n = 100 if n == '' else int(n)
        min_p = input("请输入最小概率mp 默认为0.01 \nmp:")
        min_p = 0.01 if min_p == '' else float(min_p)
        target[conf_map['hadoop.htrace.sampler.fraction']]['value'] = min_p
        target[conf_map['hadoop.htrace.sampler.limit']]['value'] = n
    elif s == '4':
        lam = input("请输入参数lambda 默认为100 \nlambda:")
        lam = 100 if lam == '' else int(lam)
        min_p = input("请输入最小概率mp 默认为0.01 \nmin_p:")
        min_p = 0.01 if min_p == '' else float(min_p)
        target[conf_map['hadoop.htrace.sampler.fraction']]['value'] = min_p
        target[conf_map['hadoop.htrace.sampler.number']]['value'] = lam
    elif s == '5':
        size = input("请输入桶大小 默认为1000 \nsize:")
        size = 1000 if size == '' else int(size)
        step = input("请输入步长 默认为300 \nsize:")
        step = 300 if step == '' else int(step)
        target[conf_map['hadoop.htrace.sampler.bucketSize']]['value'] = size
        target[conf_map['hadoop.htrace.sampler.increaseStep']]['value'] = step

    
    ans = xd.unparse(conf,pretty=True)
    
    with open(file, 'w') as f:
        f.write(ans)

if __name__ == "__main__":
    deploy_conf()
