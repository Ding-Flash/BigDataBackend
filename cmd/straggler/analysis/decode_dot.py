#-*-encoding=utf8-*-
from __future__ import print_function,division
import re
import pickle
import pydotplus
import os

cur_path = os.path.dirname(os.path.abspath(__file__)) + '/../../temp/spark/analysis/'

class Node:
    def __init__(self,node_num,node_str,**kwargs):
        self.attr=kwargs
        self.node_str=node_str
        self.node_num=node_num
        label=node_str.split('=',1)[1]
        key_vals=label.strip().split('\\n')
        if len(key_vals)==4:
            name,gini,samples,value=key_vals
            self.name=name.split('<=')[0].strip().split('"')[1]
            self.border=float(name.split('<=')[1])
            self.gini=float(gini.split('=')[1].strip())
            self.samples=int(samples.split('=')[1].strip())
            x,y=value.split('[')[1].split(']')[0].split(', ')
            self.value=[int(x),int(y)]
        elif len(key_vals)==3:
            gini, samples, value = key_vals
            self.name=None
            self.border=None
            self.gini = float(gini.split('=')[1].strip())
            self.samples = int(samples.split('=')[1].strip())
            x,y = value.split('[')[1].split(']')[0].split(', ')
            self.value = [int(x), int(y)]
        else:
            raise Exception('decode error! key_vals='+str(key_vals))
        assert len(self.value)==2,'value format error! '+node_str
        self.left_child=None
        self.right_child=None
        self.parent=None

    def copy(self):
        def traversal(node):
            if node.left_child!=None:
                left=traversal(node.left_child)
                right=traversal(node.right_child)
                cur=Node(node.node_num,node.node_str)
                left.parent=cur
                right.parent=cur
                cur.left_child=left
                cur.right_child=right
                return cur
            else:
                return Node(node.node_num,node.node_str)
        return traversal(self)
    def __str__(self):
        return ' gini = '+str(self.gini)+ ' samples = '+\
               str(self.samples)+' values = '+str(self.value)


def decode(filename='atree.dot'):
    filename = cur_path + filename
    nodes={}
    for line in open(filename):
        if re.match(r'[0-9]+ -> [0-9]',line.strip()):
            # edge
            parent,child=re.search(r'([0-9]+) -> ([0-9]+)',line).groups()
            if nodes[int(parent)].left_child==None:
                nodes[int(parent)].left_child=nodes[int(child)]
            else:
                nodes[int(parent)].right_child=nodes[int(child)]
            nodes[int(child)].parent=nodes[int(parent)]
        elif re.match(r'[0-9]+ \[[^\]]+\]',line.strip()):
            if len(open(filename).readlines()) < 5:
                print("No Straggler Found!")
                return
            # node
            num, desc=re.search(r'([0-9]+) \[([\s\S]+)\]',line).groups()
            num=int(num)
            nodes[num]=Node(num,desc)
    return nodes[0]


def inference(tree,sample):
    node=tree
    while True:
        if node.left_child==None and node.right_child==None:
            # we've come to leaf node
            value=node.value
            if value[0]>value[1]:
                return 0
            else:
                return 1
        if sample[node.name]<=node.border:
            # choose left child
            if node.left_child!=None:
                node=node.left_child
            else:
                print('unknown error occurs, exit... ')
                return
        else:
            node=node.right_child


def get_dataset(filename='dataset.dat'):
    handle=open(filename,'rb')
    dataset=pickle.load(handle)
    handle.close()
    return dataset


def post_order_traversal(node,dataset,acc,sample=None,gini=None):
    left_acc,right_acc=0,0
    flag_left=flag_right=False
    if node.left_child!=None:
        flag_left,left_acc=post_order_traversal(node.left_child,dataset,acc)
    if node.right_child!=None:
        flag_right,right_acc=post_order_traversal(node.right_child,dataset,acc)
    else:
        # this is the leaf node， should return directly
        return True,acc
    if flag_left and flag_right:
        flag_pruned,pruned_acc=pruning(node,dataset,max(left_acc,right_acc))
        if flag_pruned:
            return True,pruned_acc
        else:
            return False,max(left_acc,right_acc)
    return False,acc


# Reduced-Error pruning
def pruning(node,dataset,acc,sample=None,gini=None):
    global pruning_count
    def find_root(node):
        temp=node
        while temp.parent!=None:
            temp=temp.parent
        return temp
    left_child=node.left_child
    right_child=node.right_child
    # try remove the children
    node.left_child=None
    node.right_child=None
    root=find_root(node)
    true_count=0
    for data in dataset:
        label=inference(root,data)
        if data['label']==label:
            true_count+=1
    pruned_acc=true_count/len(dataset)
    if pruned_acc>=acc:
        pruning_count+=1
        return True,pruned_acc
    # reconstruct the tree
    node.left_child=left_child
    node.right_child=right_child
    return False,acc


def export(tree):
    def first_order_traversal(node):
        global out,i
        if node==None:
            return
        if node.name!=None:
            out+='\n%d [label="%s\\ngini=%.4f\\nsamples=%d\\nvalue=%s"];'%(
                i,node.name, node.gini, node.samples, str(node.value)
            )
        else:
            out += '\n%d [label="gini=%.4f\\nsamples=%d\\nvalue=%s"];' % (
                i,node.gini, node.samples, str(node.value)
            )
        # add attr i to this node
        node.i=i
        # link this node with its parent if it has one
        if node.parent!=None:
            out += '\n%d -> %d;'%(node.parent.i,i)
        # update global counter
        i+=1
        # traversal another
        first_order_traversal(node.left_child)
        first_order_traversal(node.right_child)
    global out,i
    out += 'digraph Tree {\nnode [shape=box] ;'
    first_order_traversal(tree)
    out+='\n}'


def mypruning_traversal(node,sample=None,gini=None):
    if node==None:
        return
    if sample!=None:
        # pruning using sample threshold
        if node.left_child and node.right_child:
            # pruning current node
            left=node.left_child
            right=node.right_child
            #if left.samples<=sample and right.samples<=sample:
            if left.value[1]<=sample and right.value[1]<=sample:
                node.left_child=None
                node.right_child=None
                del left,right
        mypruning_traversal(node.left_child,sample,gini)
        mypruning_traversal(node.right_child,sample,gini)
    if gini!=None:
        # pruning using gini threshold
        if node.left_child and node.right_child:
            # pruning current node
            left=node.left_child
            right=node.right_child
            if left.gini<gini and right.gini<gini:
                node.left_child=None
                node.right_child=None
                del left,right
        mypruning_traversal(node.left_child,sample,gini)
        mypruning_traversal(node.right_child,sample,gini)


def stair_test_sample(tree,dataset,thresh,stair,gini=False):
    if gini:
        # pruning using gini
        coords=[]
        i=0
        while i<thresh:
            mypruning_traversal(tree,gini=i)
            true_count=0
            for data in dataset:
                label = inference(tree, data)
                if data['label'] == label:
                    true_count += 1
            pruned_acc = true_count / len(dataset)
            coords.append([i,pruned_acc])
            # update i
            i+=stair
    else:
        # pruning using samples
        coords=[]
        i=0
        while i<thresh:
            mypruning_traversal(tree,sample=i)
            true_count = 0
            for data in dataset:
                label = inference(tree, data)
                if data['label'] == label:
                    true_count += 1
            pruned_acc = true_count / len(dataset)
            coords.append([i, pruned_acc])
            # update i
            i+=stair
    return coords


def cal_acc(tree,test):
    count=0
    all=0
    for sample in test:
        if sample['label']:
            all+=1
            if inference(tree,sample)==sample['label']:
                count+=1
    return count/all


def ccp_pruning(tree,test):
    def find_opt_node(tree,test):
        # calculate min alpha of internal nodes
        if tree.left_child==None:
            return 1e20,None
        # internal node
        gt=(loss_single_node(tree,test)-loss(tree,test))/(count_leafs(tree)-1)
        left_alpha,left_node=find_opt_node(tree.left_child,test)
        right_alpha,right_node=find_opt_node(tree.right_child,test)
        if gt<left_alpha and gt<right_alpha:
            return gt,tree
        elif left_alpha<right_alpha and left_alpha<gt:
            return left_alpha,left_node
        else:
            return right_alpha,right_node
    while tree.left_child!=None:
        tree_=tree.copy()
        alpha,node=find_opt_node(tree_,test)
        node.left_child=None
        node.right_child=None
        ccp_trees.append([alpha,tree_])
        tree=tree_
        print('leaf node num:',count_leafs(tree))
    print('there are',len(ccp_trees),'subtrees')
    # find optimal subtree
    best=0
    for i,item in enumerate(ccp_trees):
        acc=cal_acc(item[1],test)
        ccp_trees[i].append(acc)
        if acc>=best:
            best=acc
            best_tree=item[1]
        print(acc)
    return best_tree


def loss_single_node(tree,test):
    error_count=0
    all=0
    value = tree.value
    if value[0] > value[1]:
        label=0
    else:
        label=1
    for sample in test:
        if sample['label']:
            all+=1
            if sample['label']!=label:
                error_count+=1
    return error_count/all
    return error_count/len(test)


def count_leafs(tree):
    if tree.left_child:
        left_num=count_leafs(tree.left_child)
        right_num=count_leafs(tree.right_child)
        return left_num+right_num
    else:
        # leaf node
        return 1


def loss(tree,test):
    # cal ccp loss given a subtree
    # calculate error rate on test set
    error=0
    all=0
    for sample in test:
        if sample['label']:
            all+=1
            if inference(tree,sample)!=sample['label']:
                error+=1
    error_rate=error/all
    return error_rate

# global vars
out=''
i=0
pruning_count=0
ccp_trees=[]

flag_right=False
traversal_stack = []
#straggler_abnormal_feature_list = []
#s_count = 0
def traversal(root,f,isRight=False):
    global flag_right
    global traversal_stack
    #global straggler_abnormal_feature_list
    #global s_count
  
    if root.left_child==None and \
            root.right_child==None and \
            root.value[0]<root.value[1]:
                #print(root.value[0])
        # This is the target node
            #print('stack')
            #print(traversal_stack)
            if(len(traversal_stack) > 0):
                print(root.value[1])
                for i in range(0, len(traversal_stack)):
                    f.write(str(traversal_stack[i][0])+','+str(traversal_stack[i][1])+','+str(root.samples)+' ')
                f.write('\n')

            #print('list')
            #print(straggler_abnormal_feature_list)

    #if isRight:
        #traversal_stack.append([root.name, root.border, root.samples])
    if root.left_child!=None:
        traversal(root.left_child,f)
    if root.right_child!=None:
        traversal_stack.append([root.name, root.border, root.samples])
        isRight = True
        traversal(root.right_child,f)
    if isRight:
        traversal_stack.pop()



def decode_tree():
    tree=decode()
    #traversal_stack = []
    #straggler_abnormal_feature_list = []
    f = open(cur_path+'../straggler_stack','w')
    traversal(tree, f)
    f.close()
    #print('straggler_list')
    #print(straggler_abnormal_feature_list)
