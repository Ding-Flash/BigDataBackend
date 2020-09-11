#!/bin/bash
I=$1 # Iterations of GenGragh
let L=I*2
HDFS_LOC_PATH=$2
PROGRAM_NAME=$3
BDBENCH_HOME=$4
LINES_PER_FILE=$5
WORDS_PER_LINE=$6
echo ${BASH_SOURCE[0]}
cd "$(dirname "${BASH_SOURCE[0]}")"
cd "../lib/"
if [ ! -d "${PROGRAM_NAME}" ]; then
  mkdir ${PROGRAM_NAME}
fi
cd ${PROGRAM_NAME}
WORK_DIR=$(pwd)
echo $WORK_DIR
rm -rf $WORK_DIR/data/


hdfs dfs -rm -r $HDFS_LOC_PATH/result

hdfs dfs -mkdir -p $HDFS_LOC_PATH/data
#hdfs dfs -mkdir -p $HDFS_LOC_PATH/result

if [ "$PROGRAM_NAME" = "pagerank" ]; then
  if [ ! -d "data" ]; then
    mkdir "data"
  fi
  cd $BDBENCH_HOME/datagen/BigDataGeneratorSuite/Graph_datagen/
  ./gen_kronecker_graph -o:$WORK_DIR/data/Google_genGraph_$I.txt -m:"0.8305 0.5573; 0.4638 0.3021" -i:$I
  cd -
  head -4 $WORK_DIR/data/Google_genGraph_$I.txt >$WORK_DIR/data/Google_parameters_$I
  sed 1,4d $WORK_DIR/data/Google_genGraph_$I.txt >$WORK_DIR/data/Google_genGraph_$I.tmp
  mv $WORK_DIR/data/Google_genGraph_$I.tmp $WORK_DIR/data/Google_genGraph_$I.txt
  ${HADOOP_HOME}/bin/hdfs dfs -copyFromLocal $WORK_DIR/data $HDFS_LOC_PATH/
  rm -rf $WORK_DIR/data/*
else
  hdfs dfs -rm -r $HDFS_LOC_PATH/data/*
  cd $BDBENCH_HOME/datagen/BigDataGeneratorSuite/Text_datagen
  ./gen_text_data.sh lda_wiki1w $L $LINES_PER_FILE $WORDS_PER_LINE $HDFS_LOC_PATH/data
  cd -
fi