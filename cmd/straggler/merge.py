import time
import sys
sys.path.append('..')
from straggler.env_conf import *

slaves_name = get_slaves_name()
slave_num = len(slaves_name)

thread_count = 0

thread_list = []
time_list = []
op_kind_list = []
op_name = {}

cur_path = os.path.dirname(os.path.abspath(__file__)) + '/../temp/spark/'


def analysis_store():
    """
    :return: timeline straggler cart_tree
    """
    # GET THE TIME LIST
    for i in range(1,slave_num+1):
        f = open(cur_path+"tracelog_"+slaves_name[i-1])
        thread_count = 0
        min_thread = 9999
        operator_count = 0

        line = f.readline().split()
        while(line):
            if ( line[4] != 'end' ):

                this_thread = line[6]
                if (i,this_thread) not in thread_list:

                    thread_list.append((i,this_thread))
                    thread_count = thread_count + 1

                if(min_thread > int(this_thread)):

                    min_thread = int(this_thread)

            else:

                if(operator_count < int(re.findall("\d+",line[11])[0])):
                    operator_count = int(re.findall("\d+",line[11])[0])

            line = f.readline().split()

        t = int(min_thread)

        file_line_count = 0
        f.seek(0)
        line = f.readline()
        while(line):
            file_line_count = file_line_count + 1
            line = f.readline()

        for t in range( int(min_thread) , int(min_thread) + thread_count):

            this_thread_start_time_list = []
            this_thread_end_time_list = []
            this_thread_time_list = []
            this_thread_opkind_list = []
            this_thread_opkind_nounknown_list = []

            for j in range(0 , file_line_count//2):
                this_thread_start_time_list.append(0)
                this_thread_end_time_list.append(0)
                this_thread_opkind_list.append("unknown")

            f.seek(0)
            line = f.readline().split()
            while(line):
                if (line[4] != 'end'):
                    this_line_threadid = line[6]
                    if(int(this_line_threadid) == t):
                        op_id  = int(re.findall("\d+",line[10])[0])
                        time_stamp = int(line[8])
                        op_kind = re.findall("[a-z,A-Z]+",line[10])[0]
                        this_thread_start_time_list.pop( op_id )
                        this_thread_start_time_list.insert( op_id , time_stamp )
                        if(this_thread_opkind_list[op_id] == 'unknown'):
                            this_thread_opkind_list.pop( op_id )
                            this_thread_opkind_list.insert( op_id , op_kind )
                else:
                    this_line_threadid = line[7]
                    if(int(this_line_threadid) == t):
                        op_id = int(re.findall("\d+",line[11])[0])
                        time_stamp = int(line[9])
                        op_kind = re.findall("[a-z,A-Z]+",line[11])[0]


                        this_thread_end_time_list.pop( op_id )
                        this_thread_end_time_list.insert( op_id , time_stamp)
                        if(this_thread_opkind_list[op_id] == 'unknown'):
                            this_thread_opkind_list.pop( op_id )
                            this_thread_opkind_list.insert( op_id , op_kind )
                line = f.readline().split()



            for k in range(0, operator_count+1):
                this_thread_time_list.append(this_thread_start_time_list[k])
                this_thread_time_list.append(this_thread_end_time_list[k])
                this_thread_opkind_nounknown_list.append(str(this_thread_opkind_list[k]) + "_" + "start")
                this_thread_opkind_nounknown_list.append(str(this_thread_opkind_list[k]) + "_" + "end")

    #        this_thread_time_list.insert(0 , "Slave" + str(i) + " " + "Thread:" + str(t))
    #        this_thread_opkind_nounknown_list.insert(0 , "Slave" + str(i) + " " + "Thread:" + str(t))

            time_list.append(this_thread_time_list)
            op_kind_list.append(this_thread_opkind_nounknown_list)


            t = t + 1


        f.close()


    #COUNT AND MARK HTE LOCATION OF EACH STAGE

    stage_count_list=[0]
    stage_count = 1

    for i in range(0,len(time_list[0]),2):
        if(i > 1):
            try:
                if((time_list[0][i] > time_list[0][i-2]) or (time_list[0][i+1] <  time_list[0][i-1])):
                    stage_count_list.append(i)
                    stage_count = stage_count + 1
            except Exception as err:
                print(time_list[0][i])
                print(time_list[0][i-2])
                print(time_list)
                raise err

    time_duration_list = []

    min_length = 0
    for i in range(0,slave_num*thread_count):
        this_thread_time_duration_list = []
        for j in range(0,stage_count):
            stage_start = stage_count_list[j]
            duration_sum = 0
            if ( i > len(time_list) - 1 ):
                for k in range(stage_start,min_length,2):
                    this_thread_time_duration_list.append(0)
            else:
                min_length = len(time_list[i])
                if(j == stage_count - 1):
                    for k in range(stage_start,len(time_list[i]),2):

                        this_thread_time_duration_list.append(int(time_list[i][k + 1]) - int(time_list[i][k]) - duration_sum)
                        duration_sum = int(time_list[i][k + 1]) - int(time_list[i][k])
                else:
                    for k in range(stage_start,stage_count_list[j+1],2):
                        this_thread_time_duration_list.append(int(time_list[i][k + 1]) - int(time_list[i][k]) - duration_sum)
                        duration_sum = int(time_list[i][k + 1]) - int(time_list[i][k])



        time_duration_list.append(this_thread_time_duration_list)


    aver_time_list = []
    for j in range(0, len(time_duration_list[0])):
        op_sum_for_aver = 0
        for i in range(0, slave_num*thread_count):
            op_sum_for_aver = op_sum_for_aver + time_duration_list[i][j]
        aver_time_list.append(op_sum_for_aver/(slave_num*thread_count))

    ############# hot spot op ###########################
    if(len(time_duration_list[0]) < 5):
        hot_operator_length = 1
    else:
        hot_operator_length = len(time_duration_list[0])//5


    hot_op_time_list = []
    hot_op_list = []
    for i in range(0, hot_operator_length):
        hot_op_time_list.append(aver_time_list[i])
        hot_op_list.append(i)

    for i in range(hot_operator_length, len(time_duration_list[0])):
        small = hot_op_time_list[0]
        small_loc = 0
        for j in range(0,hot_operator_length):
            if(hot_op_time_list[j] < small):
                small = hot_op_time_list[j]
                small_loc = j
        if(aver_time_list[i] > small):
            hot_op_time_list[small_loc] = aver_time_list[i]
            hot_op_list[small_loc] = i


    hot_op_list.sort()
    ################### straggler op ##########################

    straggler_op_list = []

    for j in range(0, len(time_duration_list[0])):
        op_sum_for_straggler = 0
        if j in hot_op_list:
            for i in range(0, slave_num*thread_count):
                op_sum_for_straggler = op_sum_for_straggler + time_duration_list[i][j]
            average_time = op_sum_for_straggler / (slave_num*thread_count)
            for i in range(0, slave_num*thread_count):
                if (time_duration_list[i][j] > average_time * 1.3):
                    straggler_op_list.append([i ,j])



    ###########################################################

    task_num = slave_num*thread_count
    operator_number = len(time_duration_list[0])
    stage_num = stage_count
    stage_start_op_list = stage_count_list
    hot_spot_op_list = hot_op_list
    hot_spot_op_num = len(hot_op_list)
    straggler_op_num = len(straggler_op_list)
    straggler_op_location_list = straggler_op_list
    op_list = time_duration_list
    #
    # os.system("rm " + cur_path +"op_data")

    f = open(cur_path + 'op_data', 'w')
    f.writelines([str(task_num),'\n'])
    f.writelines([str(operator_number),'\n'])
    f.writelines([str(stage_num),'\n'])
    f.writelines([str(stage_start_op_list),'\n'])
    f.writelines([str(hot_spot_op_num),'\n'])
    f.writelines([str(hot_spot_op_list),'\n'])
    f.writelines([str(straggler_op_num),'\n'])
    for i in range(0, straggler_op_num):
        f.writelines([" ".join(str(s) for s in straggler_op_location_list[i]),'\n'])
    for i in range(0, task_num):
        f.writelines([" ".join(str(s) for s in op_list[i]),'\n'])

    f.close()
    ###########################################################

    #print(time_duration_list)


    #DO THE TIME ALIGNMENT




    #DO THE STANDARIZATION

    time_list_float = []

    #for i in range(0,slave_num*thread_count):
    #    this_line_time_list_float = []
    #    for j in range(0,len(time_list[i])):
            #this_line_time_list_float.append(float(time_list[i][j])/1000000)
    #        this_line_time_list_float.append(int(time_list[i][j])%1000000)
    #    time_list_float.append(this_line_time_list_float)

    #time_list_scaled = preprocessing.scale(time_list_float)
    #print time_list_scaled





    time_ = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    f = open(cur_path+"Trace_time_list_" + str(time_) , 'w')
    for i in range(0,slave_num*thread_count):
        for j in range(0,len(time_list[i])):
            f.write(str(time_list[i][j]))
            f.write(' ')
        f.write('\n')
    f.close()

    i = 0
    f = open(cur_path+"Trace_time_and_op_list_" + str(time_) , 'w')
    for i in range(0,slave_num*thread_count):
        for j in range(0,len(op_kind_list[i])):
            f.write(str(op_kind_list[i][j]))
            f.write(' ')
        f.write('\n')
        for j in range(0,len(time_list[i])):
            f.write(str(time_list[i][j]))
            f.write(' ')
        f.write('\n')
    f.close()

    '''
    i = 0
    f = open("Trace_duration_list" , 'w')
    for i in range(0,slave_num*thread_count):
        for j in range(0, len(time_duration_list[i])):
            f.write(str(time_duration_list[i][j]))
            f.write(' ')
        f.write('\n')
    f.close()
    '''
    ##############################timeline#################################
    timeline = {}
    data = {}
    data['task_num'] = task_num
    data['operator_number'] = operator_number
    data['stage_num'] = stage_num
    data['stage_start_op_list'] = stage_start_op_list
    data['hot_spot_op_list'] = hot_spot_op_list
    data['hot_spot_op_num'] = hot_spot_op_num
    data['straggler_op_num'] = straggler_op_num
    data['straggler_op_location_list'] = straggler_op_location_list
    data['op_name_list'] = {k: v for k, v in enumerate(op_kind_list[0])}
    data['op_list'] = op_list
    timeline['data'] = data
    ################################straggler#######################################
    f = open(cur_path+'task_data','r')

    line = f.readline().split()
    straggler_kind = int(line[0])

    straggler_type = []

    for i in range(0, straggler_kind):
        straggler_type.append('')
        straggler_type[i] = {}
        line = f.readline().split()
        straggler_type[i]['task_number'] = int(line[0])
        line = f.readline().split()
        straggler_type[i]['feature_number'] = int(line[0])
        line = f.readline().split()
        straggler_type[i]['urgent_level'] = int(line[0])

        straggler_type[i]['feature'] = []
        for j in range(0, straggler_type[i]['feature_number']):
            line = f.readline().split()
            line[0] = int(line[0])
            straggler_type[i]['feature'].append(line)
    f.close()
    straggler = {}
    data = {}
    data['straggler_type'] = straggler_type
    straggler['data'] = data
    ################################cart tree#######################################
    f = open(cur_path +"analysis/atree.dot")
    nodes = []
    lines = f.readlines()
    for line in lines:
        if ('label' in line) and not('->' in line):
            nodes.append('')
            idx = int(line.split()[0])
            nodes[idx] = {}
            nodes[idx]['name'] = 'node '+str(idx)
            nodes[idx]['label'] = re.search(r'\"[\s\S]*\"',line).group(0)[1:-1].split('\\n')

    for line in lines:
        if '->' in line:
            p = int(line.split()[0])
            c = int(line.split()[2])
            if not('childs' in nodes[p]):
                nodes[p]['childs'] = []
            nodes[p]['childs'].append(nodes[c])
    cart_tree = nodes[0]
    #####################################################################################
    report = dict(timeline=timeline, straggler=straggler, cart_tree=cart_tree)
    return report
