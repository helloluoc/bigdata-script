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
----------------------------------------------------
#while版本

#!/bin/sh

strings="htljsldfjdfdifjdfi:4545;453534;345353635;4533;34535;"
lastsend=$strings
num=${#strings}
echo $num
while [ ${num} > 20 ]
do
        stringlimit=`expr substr "${lastsend}" 1 10`
        echo "${stringlimit}" > shit.txt
        stringsend=`echo ${stringlimit} | sed 's/[0-9]*$//g'`
        cutstringnum=`echo ${#stringsend}`
        lastsend=`echo ${stringlimit} | sed "s/${stringsend}//g"`
        echo $lastsend
        echo $stringsend
        echo $stringlimit
done


echo ${stringlimit} | sed 's/htljsld//g'
---------------------------------------------------------
#if版本
#!/bin/sh

strings="htljsldfjdfdifjdfi:4545;453534;345353635;4533;34535;"

if [  ${#strings} -gt 20 ];then
	stringlimit=`expr substr "${strings}" 1 30`
	echo "${stringlimit}" > shit.txt
	stringsend=`echo ${stringlimit} | sed 's/[0-9]*$//g'`
	cutstringnum=`echo ${#stringsend}`
	lastsend=`echo ${stringlimit} | sed "s/${stringsend}//g"`
	echo $lastsend
	echo $stringsend
	echo $stringlimit
fi
