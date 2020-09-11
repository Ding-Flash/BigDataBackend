import json
from operator import itemgetter
from multiprocessing import Lock
from datetime import datetime
import os.path

from flask import (
    Flask,
    render_template,
    request
)
from flask_cors import CORS
import pandas as pd

from apps.hdfs.parse import Parse as ps
from utils import (
    cache_hdfs_data,
    change_xml,
    clean_bigroot_data
)
from apps.store import (
    HdfsCache,
    SparkCache,
    BigDataCache,
    AliLoadCache,
    TaskOptCache,
)

hdfscache = HdfsCache()
sparkcache = SparkCache()
bigrootcache = BigDataCache()
alicache = AliLoadCache()
optcache = TaskOptCache()


app = Flask(__name__)
CORS(app)

mutex = Lock()


@app.route("/")
def index():
    return render_template("index.html")


# htrace 相关
@app.route("/api/hdfs/createtask", methods=["GET"])
def create_hdfs_task():
    r = request.args.to_dict()
    print(r)
    name = r['name']
    hdfs_cache = hdfscache.update_from_pickle()
    if hdfs_cache.get_task_path(name):
        return json.dumps({'status': 2})
    r['time'] = datetime.now()
    hdfs_cache.set_conf(name, r)
    hdfs_cache.set_task_path(name)
    hdfs_cache.store_pickle()
    change_xml(r)
    return json.dumps({'status': 0})


@app.route("/api/hdfs/gettasklist")
def get_task_list():
    l = []
    hdfs_cache = hdfscache.update_from_pickle()
    for name, conf in hdfs_cache.conf.items():
        l.append({
            "name": name,
            "sampler": conf['sampler'],
            "time": str(conf['time'])[:19],
            "desc": conf["desc"],
            "status": hdfs_cache.status[name]
        })
    return json.dumps({"data": l[::-1]})


@app.route("/api/hdfs/refresh")
def refresh_bench_status():
    bench_name = request.args['name']
    hdfs_cache = hdfscache.update_from_pickle()
    path = hdfs_cache.get_task_path(bench_name)
    res = {}
    if os.path.isfile(path+'/trace.out'):
        hdfs_cache.status[bench_name] = "finished"
        hdfs_cache.store_pickle()
        res['status'] = 1
    else:
        res['status'] = 0
    return json.dumps(res)


@app.route("/api/hdfs/delete")
def delete_hdfs_task():
    bench_name = request.args['name']
    hdfs_cache = hdfscache.update_from_pickle()
    hdfs_cache.delete_task(bench_name)
    return json.dumps({
        'status': 0
    })


@app.route("/api/hdfs/getfuncfeature", methods=["GET"])
def get_func_feature():
    bench_name = request.args["name"]
    hdfs_cache = hdfscache.update_from_pickle()
    path = hdfs_cache.get_task_path(bench_name) + '/trace.out'
    with mutex:
        cache = hdfs_cache.get_task_report(bench_name)
        if not cache:
            cache = cache_hdfs_data(ps(path), bench_name)
    return json.dumps(cache.func_feature)


@app.route("/api/hdfs/gettimeline", methods=["GET"])
def get_time_line():
    hdfs_cache = hdfscache.update_from_pickle()
    get_args = itemgetter("name", "count", "func_name")
    bench_name, count, fname = get_args(request.args)
    path = hdfs_cache.get_task_path(bench_name) + '/trace.out'
    with mutex:
        cache = hdfs_cache.get_task_report(bench_name)
        if cache is None:
            cache = cache_hdfs_data(ps(path), bench_name)
    df = cache.time_line
    timeline = df["begin"]
    com_timeline = df[df['name'] == fname]['begin']
    interval = range(0, timeline.max(), timeline.max() // int(count))
    res = pd.cut(timeline, interval, right=False).value_counts(sort=False)
    com_res = pd.cut(com_timeline, interval, right=False).value_counts(sort=False)
    data = [{'interval': str(item[0]), 'all': item[1]} for item in res.iteritems()]
    for i, c in enumerate(com_res.iteritems()):
        data[i][fname] = c[1]
    return json.dumps(dict(columns=['interval', 'all', fname], rows=data))


@app.route("/api/hdfs/getcalltree", methods=["GET"])
def get_call_tree():
    hdfs_cache = hdfscache.update_from_pickle()
    bench_name = request.args["name"]
    path = hdfs_cache.get_task_path(bench_name) + '/trace.out'
    func_name = request.args["func_name"]
    with mutex:
        cache = hdfs_cache.get_task_report(bench_name)
        if cache is None:
            cache = cache_hdfs_data(ps(path), bench_name)
    records = cache.call_tree.records
    all_trees = cache.call_tree.trees
    trees = [r['root'] for r in records if func_name in r['node']]
    res = dict(res=[all_trees[tree] for tree in trees])
    return json.dumps(res)


@app.route("/api/hdfs/gettracedetail")
def get_trace_detail():
    bench_name = request.args["name"]
    hdfs_cache = hdfscache.update_from_pickle()
    path = hdfs_cache.get_task_path(bench_name) + '/trace.out'
    with mutex:
        cache = hdfs_cache.get_task_report(bench_name)
        if cache is None:
            cache = cache_hdfs_data(ps(path), bench_name)
    return json.dumps({
        'size': cache.size / (2**20),
        'func_type': cache.func_type,
        'tree_type': len(cache.call_tree.records)
    })


# spark 相关
@app.route("/api/spark/timeline")
def get_spark_timeline():
    task_name = request.args['name']
    spark_cache = sparkcache.update_from_pickle()
    report = spark_cache.report[task_name]
    return json.dumps(report.timeline)


@app.route("/api/spark/straggler")
def get_straggler():
    task_name = request.args['name']
    spark_cache = sparkcache.update_from_pickle()
    report = spark_cache.report[task_name]
    return json.dumps(report.straggler)


@app.route("/api/spark/cart_tree")
def get_cart_tree():
    task_name = request.args['name']
    spark_cache = sparkcache.update_from_pickle()
    report = spark_cache.report[task_name]
    return json.dumps(report.cart_tree)


@app.route("/api/spark/gettasklist")
def get_spark_task_list():
    l = []
    spark_cache = sparkcache.update_from_pickle()
    for name, conf in spark_cache.conf.items():
        l.append({
            "name": name,
            "time": str(conf['time'])[:19],
            "desc": conf.get("desc", ""),
            "status": spark_cache.status[name]
        })
    return json.dumps(dict(data=l[::-1]))


@app.route("/api/spark/delete")
def delete_spark_task():
    bench_name = request.args['name']
    spark_cache = sparkcache.update_from_pickle()
    spark_cache.delete_task(bench_name)
    return json.dumps({
        'status': 0
    })


# bigroot相关
@app.route("/api/bigroot/getstraggler")
def get_bigroot_straggler():
    name = request.args['name']
    bigroot_cache = bigrootcache.update_from_pickle()
    report = bigroot_cache.report[name]['rest']
    res = []
    for slave, value in report.items():
        data = clean_bigroot_data(value)
        data['host'] = slave
        res.append(data)
    return json.dumps({
        "data": res
    })


@app.route("/api/bigroot/gettasklist")
def get_bigroot_task_list():
    l = []
    bigroot_cache = bigrootcache.update_from_pickle()
    for name, conf in bigroot_cache.conf.items():
        l.append({
            "name": name,
            "time": str(conf['time'])[:19],
            "desc": conf.get("desc", ""),
            "status": bigroot_cache.status[name]
        })
    return json.dumps(dict(data=l[::-1]))


@app.route("/api/bigroot/delete")
def delete_bigroot_task():
    bench_name = request.args['name']
    bigroot_cache = bigrootcache.update_from_pickle()
    bigroot_cache.delete_task(bench_name)
    return json.dumps({
        'status': 0
    })


# aliload 相关
@app.route("/api/aliload/gettasklist")
def get_aliload_task_list():
    l = []
    ali_cache = alicache.update_from_pickle()
    for name, conf in ali_cache.conf.items():
        l.append({
            "name": name,
            "rate": conf['rate'],
            "start": conf['start'],
            "end": conf["end"],
            "time": str(conf['time'])[:19],
        })
    return json.dumps(dict(data=l[::-1]))


@app.route("/api/aliload/delete")
def delete_aliload_task():
    task_name = request.args['name']
    ali_cache = alicache.update_from_pickle()
    ali_cache.delete_task(task_name)
    return json.dumps({
        'status': 0
    })


@app.route("/api/aliload/getstatus")
def get_aliload_status():
    name = request.args['name']
    ali_cache = alicache.update_from_pickle()
    res = ali_cache.get_task_report(name)
    return json.dumps(dict(data=res.data))


# taskopt相关
@app.route("/api/taskopt/gettasklist")
def get_opt_list():
    l = []
    opt_cache = optcache.update_from_pickle()
    for name, conf in opt_cache.conf.items():
        l.append({
            "name": name,
            "class": conf["class"],
            "train_time": conf["train_time"],
            "model": conf["model"],
            "time": str(conf['time'])[:19],
        })
    return json.dumps(dict(data=l[::-1]))


@app.route("/api/taskopt/delete")
def delete_opt_task():
    task_name = request.args['name']
    opt_cache = optcache.update_from_pickle()
    opt_cache.delete_task(task_name)
    return json.dumps({
        'status': 0
    })


@app.route("/api/taskopt/getstatus")
def get_opt_status():
    task_name = request.args['name']
    opt_cache = optcache.update_from_pickle()
    res = opt_cache.get_task_report(task_name)
    return json.dumps({
        "data": {
            "status": res.data,
            "tune": res.tune,
            "cmd": res.cmd,
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
