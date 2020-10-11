from apps.store import HdfsCache
import xmltodict as xd

from config import HADOOP_HOME

core_file = HADOOP_HOME + "/etc/hadoop/core-site.xml"

sampler_map = {
    "概率采样": "ProbabilitySampler",
    "系统采样": "CountSampler",
    "Bump采样": "LimitSampler",
    "令牌桶采样": "TBucketSampler"
}


def cache_hdfs_data(bench, name):
    """
    :param bench: instancs of apps.hdfs.parse.Parse
    :param name: task name
    :return: bench_data
    """
    hdfs_cache = HdfsCache()
    hdfs_cache = hdfs_cache.update_from_pickle()
    hdfs_cache.set_task_report(name, {
        "size": bench.size,
        "func_feature": bench.get_func_feature(),
        "call_tree": bench.get_call_tree(),
        "time_line": bench.get_time_line(),
        "func_type": len(bench.names)
    })
    hdfs_cache.store_pickle()
    return hdfs_cache.get_task_report(name)


# 修改xml文件
def change_xml(conf):
    hdfs_cache = HdfsCache()
    hdfs_cache = hdfs_cache.update_from_pickle()

    conf_map = {}

    def find_name(target):
        for idx, t in enumerate(target):
            conf_map[t['name']] = idx

    with open(core_file) as f:
        core = f.read()

    core = xd.parse(core)
    sampler = sampler_map[conf['sampler']]
    target = core['configuration']['property']
    find_name(target)
    target[conf_map['hadoop.htrace.sampler.classes']]['value'] = sampler
    target[conf_map['hadoop.htrace.local.file.span.receiver.path']]['value'] = hdfs_cache.get_task_path(
        conf['name']) + '/trace.out'
    if sampler == "ProbabilitySampler":
        target[conf_map['hadoop.htrace.sampler.fraction']]['value'] = conf['probability']
    if sampler == "LimitSampler":
        target[conf_map['hadoop.htrace.sampler.fraction']]['value'] = conf['probability']
        target[conf_map['hadoop.htrace.sampler.limit']]['value'] = conf['lambda']
    if sampler == "TBucketSampler":
        target[conf_map['hadoop.htrace.sampler.bucketSize']]['value'] = conf['bsize']
        target[conf_map['hadoop.htrace.sampler.increaseStep']]['value'] = conf['brate']

    ans = xd.unparse(core, pretty=True)

    with open(core_file, 'w') as f:
        f.write(ans)


# 清理core-site.xml 新启动一个任务就清理一遍
def clean_xml():
    conf_map = {}

    def find_name(target):
        for idx, t in enumerate(target):
            conf_map[t['name']] = idx

    with open(core_file) as f:
        core = f.read()

    core = xd.parse(core)
    target = core['configuration']['property']
    find_name(target)
    target[conf_map['hadoop.htrace.sampler.classes']]['value'] = ""
    ans = xd.unparse(core, pretty=True)

    with open(core_file, 'w') as f:
        f.write(ans)


def clean_bigroot_data(slave):
    exe_time = max(len(slave['cpu']), len(slave['io']), len(slave['net'])) + 1

    cpu, io, net = [0] * exe_time, [0] * exe_time, [0] * exe_time

    for c in slave['cpu']:
        cpu[int(c[0])] = c[1]
    for i in slave['io']:
        io[int(i[0])] = i[1]
    for n in slave['net']:
        net[int(n[0])] = n[1]

    try:
        straggler_scala = max(slave['tasks'], key=lambda x: x[2])[2]
    except:
        straggler_scala = 0

    tasks, table = [], []

    pie_data = {}

    for task in slave['tasks']:

        table.append({
            'start': round(task[0],3),
            'end': round(task[1],3),
            'factor': round(task[2],3),
            'root-cause': "unkown" if task[3] == '{unkown}' else ','.join(task[3])
        })

        if task[3] == '{unkown}':
            pie_data['unkown'] = pie_data.get('unkown', 0) + 1
            continue
        else:
            for cause in task[3]:
                pie_data[cause] = pie_data.get(cause, 0) + 1

        scala = task[2]/straggler_scala
        tasks.append([
            {
                'symbol': 'none',
                'name': ','.join(task[3]),
                'coord': [task[0], scala]
            },
            {
                'symbol': 'none',
                'coord': [task[1], scala]
            }
        ])

    def normal_cpu(cpu):
        if max(cpu) == 0:
            return cpu
        else:
            return list(map(lambda x: x/max(cpu), cpu))

    return {
        'time': exe_time,
        'cpu': normal_cpu(cpu),
        'io': list(map(lambda x: x/max(io), io)),
        'net': list(map(lambda x: x/max(net), net)),
        'tasks': tasks,
        'scala': straggler_scala,
        'table': table,
        'cause': list(pie_data.keys()),
        'pie_data': [{'name': key, 'value': val} for key, val in pie_data.items()]
    }