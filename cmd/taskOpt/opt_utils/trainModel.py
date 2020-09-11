
import logging

import numpy as np
import pymysql
from colorama import Fore
from sklearn.tree import ExtraTreeRegressor
from xgboost import XGBRegressor

'''
@功能：独立的用于构建模型的模块
@实现：从数据库中读取数据，使用一定的规则选取相应的数据，构建预测模型
'''


def SQLTrainData(sql):
    """
    从数据库中获取数据
    :param sql: 输入SQL语句
    :return: 训练数据
    """
    from taskOpt.opt_utils import mysql_host, mysql_port, mysql_user, mysql_passwd, mysql_database
    db = pymysql.connect(host=mysql_host, port=int(mysql_port), user=mysql_user, passwd=mysql_passwd, db=mysql_database)
    try:
        cursor = db.cursor()
        cursor.execute(sql)
        d = cursor.fetchall()  # 取出符合要求的数据
        db.close()
        data = np.array(d)
    except Exception as e:
        print(Fore.RED + "erros occur when fetching data from the database")
        logging.exception(e)

    if len(data) < 1:  # 无返回结果
        return [], []

    Target = data[:, 3]  # 终极预测目标     行全取，只取第二列
    feature = data[:, 4:]  # 第一层属性    行全取，取4-16列
    inputsize = feature[:, -1]
    inputsize = inputsize.astype(np.float)  # astype用来转换数据类型
    feature = np.column_stack((feature, inputsize * np.log(inputsize)))  # 增加特征N*logN
    return feature, Target


'''
功能：构建模型,没有验证参数的环节，单层模型
'''


def getExtraTreeModel(x, y):
    et = ExtraTreeRegressor()
    et.fit(x, y)
    return et


def getXgboostModel(x, y):
    xgb = XGBRegressor(max_depth=5, learning_rate=0.1, n_estimators=200, silent=False, objective='reg:gamma')
    xgb.fit(x, y)
    return xgb
