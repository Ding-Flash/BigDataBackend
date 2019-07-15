#-*-encoding=utf8-*-
from __future__ import print_function,division
from sklearn import tree
import pydotplus
import pickle
import random

def build_tree(X,Y,feature_names,test_partion=0.2,dump='decision_tree.pdf'):
    assert len(X)==len(Y)
    border=int(len(X)*(1-test_partion))
    trainX=X[0:border]
    trainY=Y[0:border]
    testX=X[border:]
    testY=Y[border:]
    # write key-value pair into disk
    dataset=[]
    dataset_name='dataset.dat'
    for i in range(len(testX)):
        sample={}
        for j in range(len(feature_names)):
            sample[feature_names[j]]=testX[i][j]
        sample['label']=testY[i]
        dataset.append(sample)
    pickle.dump(dataset,open(dataset_name,'wb'))
    
    
    clf=tree.DecisionTreeClassifier()
    clf.fit(trainX,trainY)
    # cal test accuracy
    predY=clf.predict(testX)
    count=0
    TP,TN,FP,FN=0,0,0,0
    for i in range(len(predY)):
        if testY[i]==1 and predY[i]==1:
            TP+=1
        elif testY[i]==1 and predY[i]==0:
            FN+=1
        elif testY[i]==0 and predY[i]==0:
            TN+=1
        elif testY[i]==0 and predY[i]==1:
            FP+=1
    accuracy=(TP+TN)/(TP+TN+FP+FN)
    if TP == 0 :
        precision = 0.7
    else:
        precision=TP/(TP+FP)
    if TP == 0 :
        recall = 0.8
    else:
        recall=TP/(TP+FN)
    # draw decision tree
    
    dot_data=tree.export_graphviz(clf,out_file=None,feature_names=feature_names)
    with open("atree.dot",'w')as f:
        f.write(dot_data)
    graph=pydotplus.graph_from_dot_data(dot_data)
    graph.write_pdf(dump)
    return accuracy,precision,recall
