#/bin/bash

######################  CLEAN WORK ###########################
python3 clean_all.py


##################### Time Alignment ##########################
python3 get_time_alignment_deviation.py


####################### Start Sample ############################

cd sample
python3 samp_run.py $2
#python3 instru_run.py
for ((i=1;i<3;i++))
do
	ssh -p 22 yangs@slave$i 'cd ~/Bigdata/qwc_trace;./run_instrument.sh'&
done


###################### start app ################################
echo 'Starting APP:'
echo $1

if [ $1 == 'pagerank' ]; then

	echo 'pagerank' >> analysis/app_info
	echo `date +%s`
	/home/yangs/Bigdata/hibench/bin/workloads/websearch/pagerank/spark/run.sh
	echo `date +%s`
elif [ $1 == 'terasort' ]; then

	echo 'terasort' >> analysis/app_info
	echo `date +%s`
	/home/yangs/Bigdata/hibench/bin/workloads/micro/terasort/spark/run.sh	
	echo `date +%s`

elif [ $1 == 'bayes' ]; then

	echo 'bayes' >> analysis/app_info
	echo `date +%s`
	/home/yangs/Bigdata/hibench/bin/workloads/ml/bayes/spark/run.sh	
	echo `date +%s`

elif [ $1 == 'als' ]; then

	echo 'als' >> analysis/app_info
        echo `date +%s`	
	/home/yangs/Bigdata/hibench/bin/workloads/ml/als/spark/run.sh
	echo `date +%s`



elif [ $1 == 'test0' ]; then

	echo 'test' >> analysis/app_info 
	echo `date +%s`
	spark-submit --master spark://master:7077 --deploy-mode client  WordCount7.jar Norm_test_data
	echo `date +%s`

elif [ $1 == 'test1' ]; then
	
	echo 'test' >> analysis/app_info
	echo `date +%s`
	spark-submit --master spark://master:7077 --deploy-mode client  WordCount7.jar Norm_test_data
	echo `date +%s`

else
	echo "Unknow app"
	exit

fi
####################### Stop Instrumen ##################################

python3 instru_stop.py
cd ..

####################### Get Logs ##################################

#exit

cp $SPARK_HOME/tsee_log/app* app

python3 get_trace_log.py

cd sample
python3 get_logs.py

####################### ANALYSIS #################################
python3 log_exe.py
cd ../analysis
python3 engine.py
python3 decode_dot.py
python3 do_straggler.py
cd ..
python3 merge.py
#for ((i=1;i<6;i++))
#do
#	ssh -p 22 hadoop@slave$i 'cd ~/qwc_trace;./run_instrument.sh'&
#done&
