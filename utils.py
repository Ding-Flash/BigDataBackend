from apps.store import hdfs_cache
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
    hdfs_cache.set_task_report(name, {
        "size": bench.size,
        "func_feature": bench.get_func_feature(),
        "call_tree": bench.get_call_tree(),
        "time_line": bench.get_time_line(),
        "func_type": len(bench.names)
    })
    return hdfs_cache.get_task_report(name)


# 修改xml文件
def change_xml(conf):
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
