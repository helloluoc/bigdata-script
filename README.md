里面有几个需要读日志文件的函数，如果只是测试线程池的话可以自己写几个函数代替todoList里的函数进行测试
#对字符进行截取
#!/bin/sh

strings="htljsldfjdfdifjdfi:4545;453534;345353635;4533;34535;"

if [  ${#strings} -gt 20 ];then
	stringlimit=`expr substr "${strings}" 1 30`
	echo "${stringlimit}" > shit.txt
	stringsend=`echo ${stringlimit} | sed 's/[0-9]*$//g'`
	echo $stringsend
fi
