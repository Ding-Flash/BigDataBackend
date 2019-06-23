import json
from operator import itemgetter
from threading import Lock

from flask import (
    Flask,
    request
)
from flask_cors import CORS
import pandas as pd

from mock import hdfs

from apps.hdfs.parse import Parse as ps
from utils import cache_data
from apps.store import (
    hdfs_cache,
    spark_cache,
    bigdata_cache,
    tree_cache
)

app = Flask(__name__)
CORS(app)

bench_name = "bench"

@app.route("/")
def hello_world():
    return "nothing~~~~"


# htrace 相关
@app.route("/api/hdfs/getfuncfeature", methods=["GET"])
def get_func_feature():
    path = request.args["path"]
    # TODO 这里除了传递path之外 还要传递一个任务名字 这里先用bench代替
    cache = hdfs_cache.get(bench_name)
    if not cache:
        cache = cache_data(ps(path), bench_name)
    return json.dumps(cache.func_feature)


@app.route("/api/hdfs/gettimeline", methods=["GET"])
def get_time_line():
    get_args = itemgetter("path", "count", "name")
    path, count, name = get_args(request.args)
    cache = hdfs_cache.get(bench_name)
    if not cache:
        cache = cache_data(ps(path), bench_name)
    df = cache.time_line
    timeline = df["begin"]
    com_timeline = df[df['name'] == name]['begin']
    interval = range(0, timeline.max(), timeline.max() // int(count))
    res = pd.cut(timeline, interval, right=False).value_counts(sort=False)
    com_res = pd.cut(com_timeline, interval, right=False).value_counts(sort=False)
    data = [{'interval': str(item[0]), 'all': item[1]} for item in res.iteritems()]
    for i, c in enumerate(com_res.iteritems()):
        data[i][name] = c[1]
    return json.dumps(dict(columns=['interval', 'all', name], rows=data))


@app.route("/api/hdfs/getcalltree", methods=["GET"])
def get_call_tree():
    path = request.args["path"]
    func_name = request.args["func_name"]
    cache = hdfs_cache.get(bench_name)
    if not cache:
        cache = cache_data(ps(path), bench_name)
    records = cache.call_tree.records
    all_trees = cache.call_tree.trees
    trees = [r['root'] for r in records if func_name in r['node']]
    res = dict(res=[all_trees[tree] for tree in trees])
    return json.dumps(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
