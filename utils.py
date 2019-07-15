from apps.store import hdfs_cache


def cache_hdfs_data(bench, name):
    """
    :param bench: instancs of apps.hdfs.parse.Parse
    :param name: task name
    :return: bench_data
    """
    hdfs_cache.set_task_report(name, {
        "func_feature": bench.get_func_feature(),
        "call_tree": bench.get_call_tree(),
        "time_line": bench.get_time_line()
    })
    return hdfs_cache.get_task_report(name)