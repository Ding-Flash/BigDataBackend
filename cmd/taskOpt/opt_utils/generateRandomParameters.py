# coding=utf-8
import random

'''
功能：
对于给定的参数范围，随机生成配置参数，以及生成数据的规模（MB）
输入：
给出需要生成几组配置参数：num
输出：
生成的参数，存放在数组中
'''


def generate_random_parameters(program):
    defPlsm = random.randrange(1, 5, 1)  # spark.default.parallelism
    memFra = 0.05 * random.randint(0, 8) + 0.3  # spark.memory.fraction 0.6
    memStFra = 0.05 * random.randint(0, 8) + 0.3  # spark.memory.storageFraction  0.5
    redMSIF = random.randrange(10, 128, 5)  # spark.reducer.maxSizeInFlight 48m
    shuffleFB = random.randrange(16, 128, 16)  # spark.shuffle.file.buffer 32k
    shuffleIMR = random.randrange(2, 16, 2)  # spark.shuffle.io.maxRetries   3
    shuffleINCPP = random.randrange(1, 4, 1)  # spark.shuffle.io.numConnectionsPerPeer    1
    exeMem = random.randrange(5, 15, 1)  # spark.executor.memory 1g
    # driMem = random.randrange(2, 30, 1)  # spark.driver.memory   1g
    driMem = 4 * exeMem
    if program.lower() == 'pagerank':
        iterations = random.randrange(15, 22, 1)  # data size :
        driCor = random.randrange(3, 20, 1)  # spark.driver.cores    1
        exeCor = random.randrange(3, 20, 1)  # spark.executor.cores
        confs = [iterations, driMem, driCor, exeMem, exeCor, defPlsm, memFra, memStFra, redMSIF, shuffleFB, shuffleIMR,
                 shuffleINCPP]
        return confs
    dataSize = random.randrange(1, 20, 1)  # data size : GB
    driCor = random.randrange(1, 20, 1)  # spark.driver.cores    1
    exeCor = random.randrange(1, 20, 1)  # spark.executor.cores
    confs = [dataSize, driMem, driCor, exeMem, exeCor, defPlsm, memFra, memStFra, redMSIF, shuffleFB, shuffleIMR,
             shuffleINCPP]
    return confs
