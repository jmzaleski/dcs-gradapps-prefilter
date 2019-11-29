#!/bin/bash

TEMP=/tmp/grep$$
cat > $TEMP < /dev/null

if test "$#" -eq 2
then
	app="$1"
	sgs="$2"
else
	echo usage: $0 app_num sgs_num
	exit 2
fi

for pf in ~/mscac-prefilter/dcs-prefilter-*.csv
do
	grep $sgs $pf > $TEMP
	if test -s $TEMP
	then
		echo app $app with sgs number $sgs already appears in prefilter file $pf
		cat $TEMP
		/bin/rm $TEMP
		exit 1
	else
		echo no $sgs in $pf > /dev/null
	fi
done
		 
