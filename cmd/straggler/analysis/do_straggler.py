import random
import sys
import os
import re

straggler_num = 999
s_info = []

cur_path = os.path.dirname(os.path.abspath(__file__)) + '/../../temp/spark/sample/'


def prepro():
    global straggler_num

    #f = open('straggler_stack')
    #straggler_kind = len(f.readlines()) - 1

    #print straggler_kind

    #f.seek(0)
    if not os.path.exists(cur_path + '../straggler_stack'):
        straggler_num = 0
        print("No Straggler_stack")
        return

    f = open(cur_path + '../straggler_stack')
    straggler_kind = len(f.readlines())
    f.seek(0)
    for i in range(0, straggler_kind):
        line = f.readline().split()
        f_num = len(line)

        temp_s_list = []

        for j in range(0, f_num):
            info_list = line[j].split(',')
            #print(info_list[1]) 
            feature = info_list[0]
            ar = info_list[1]
            while float(ar) > 1 :
                ar = float(ar) / 10
            straggler_num = info_list[2]

            temp_s_list.append([feature, ar, straggler_num])

        s_info.append(temp_s_list)
    f.close()
    print(s_info)
    #return straggler_kind


#f = open("/home/hadoop/qwc_trace/analysis/app_info", 'r')
#app_name = f.readline().split()[0]
#f.close()
#f = open("/home/hadoop/qwc_trace/analysis/app_task" , 'r')
#task_num = int(f.readline().split()[0])
#f.close()
#f = open("/home/hadoop/qwc_trace/analysis/app_straggler" , 'r')
#straggler_num = int(f.readline().split()[0])
#f.close()

#f.close()

def trans():
    global s_info
    global straggler_num


    for i in range(0, len(s_info)):
        for j in range(0, len(s_info[i])):
            if(s_info[i][j][0] == 'serialize'):
                s_info[i][j][0] = 0
            elif(s_info[i][j][0] == 'deserialize'):
                s_info[i][j][0] = 1
            elif(s_info[i][j][0] == 'executor_run_ime'):
                s_info[i][j][0] = 2
            elif(s_info[i][j][0] == 'memory_bytes_spilled'):
                s_info[i][j][0] = 3
            elif(s_info[i][j][0] == 'JVM_time'):
                s_info[i][j][0] = 4
            elif(s_info[i][j][0] == 'remote_fetch_rate'):
                s_info[i][j][0] = 5
            elif(s_info[i][j][0] == 'shuffle_read'):
                s_info[i][j][0] = 6
            elif(s_info[i][j][0] == 'shuffle_records'):
                s_info[i][j][0] = 7
            elif(s_info[i][j][0] == 'shuffle_write'):
                s_info[i][j][0] = 8
            elif(s_info[i][j][0] == 'shuffle_write_records'):
                s_info[i][j][0] = 9
            elif(s_info[i][j][0] == 'locality'):
                s_info[i][j][0] = 10
            elif(s_info[i][j][0] == 'cpu'):
                s_info[i][j][0] = 11
            elif(s_info[i][j][0] == 'io'):
                s_info[i][j][0] = 12
            elif(s_info[i][j][0] == 'net'):
                s_info[i][j][0] = 13
            elif(s_info[i][j][0] == 'read_from_hdfs'):
                s_info[i][j][0] = 14
            elif(s_info[i][j][0] == 'input_bytes/result_bytes'):
                s_info[i][j][0] = 15
            elif(s_info[i][j][0] == 'data_read_method'):
                s_info[i][j][0] = 16
            else:
                s_info[i][j][0] = 17
                

    
    '''
        if(straggler_num == 0):
            random.seed()
            seed = random.random()
            #print int((seed*10)%2)
            if(int((seed*10)%3) != 0):
                straggler_num = int(seed*10)
                for i in range(0, len(s_info[2])):
                    s_info[2][i][0] = int((random.random()*10)%3)
                    s_info[2][i][1] = round(random.random(), 2)
                    s_info[2][i][2] = straggler_num

                    #print s_info[2][i]
                for i in range(0, 2):
                    del s_info[0]
        
                
                #print s_info
    '''

    fw = open(cur_path+'../task_data', 'w')
    if(straggler_num == 0):
        fw.write('0')
        fw.write('\n')
        exit() 
    fw.write(str(len(s_info)))
    fw.write('\n')
    straggler_sum = 0
    for i in range(0, len(s_info)):
        num = 9999
        
        for j in range(0, len(s_info[i])):
            if(int(s_info[i][j][2]) < num):
                num = int(s_info[i][j][2])
        fw.write(str(num))
        fw.write('\n')
        fw.write(str(len(s_info[i])))
        fw.write('\n')
        straggler_sum = straggler_sum + int(num)
        if(num > 10):
            fw.write('1')
        else:
            fw.write('0')
        fw.write('\n')
        for j in range(0, len(s_info[i])):
            string = str(s_info[i][j][0])+' '+str(s_info[i][j][1])
            fw.write(string)
            fw.write('\n')

    fw.write(str(straggler_sum))
    print(("Find "+str(straggler_sum)+" stragglers root-cause !"))
    fw.close()


def detect():
        #if(app_name == 'test_skew'):
    #print app_name
    prepro()
    trans()

    #print s_info
