#!/bin/bash

TEMP=/tmp/grep$$
cat > $TEMP < /dev/null

for i in $*
do
	#set -x
	grep "$i" ~/mscac-prefilter/dcs-prefilter-*.csv >> $TEMP
	#set -
done

if test -s "$TEMP"
then
	echo oh oh, sgs number appears in existing prefilter file:
	echo 'vvvvvvvvvvvvvvvvv'
	cat $TEMP
	echo '^^^^^^^^^^^^^^^^^^'
fi
/bin/rm $TEMP
		 
