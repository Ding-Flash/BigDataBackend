import operator
from functools import reduce
import datetime


def bfs_tree(tree, nodes):
    res = []
    names = nodes[tree]['name']
    layers = [tree]
    res.append([names])
    while len(layers):
        temp_names = []
        temp_layer = []
        for l in layers:
            for c in nodes[l]['childs']:
                temp_layer.append(c)
                temp_names.append(nodes[c]['name'])

        layers = temp_layer
        res.append(temp_names)
    res = reduce(operator.add, res)
    return dict(root=tree, node=res), hash(frozenset(res))


def hash_tree(roots, nodes):
    ans = []
    record = set()
    for root in roots:
        temp, h = bfs_tree(root, nodes)
        if h in record:
            continue
        else:
            record.add(h)
            ans.append(temp)
    return ans


def _convert_java_millis(java_time_millis):
    """Provided a java timestamp convert it into python date time object"""
    ds = datetime.datetime.fromtimestamp(
        int(str(java_time_millis)[:10])) if java_time_millis else None
    ds = ds.replace(hour=ds.hour, minute=ds.minute, second=ds.second,
                    microsecond=int(str(java_time_millis)[10:]) * 1000)
    return ds
