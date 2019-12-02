#!/bin/bash

TEMP=/tmp/grep$$
cat > $TEMP < /dev/null

#set -x 
grep "$1" ~/mscac-prefilter/dcs-prefilter-*.csv >> $TEMP
rc = $?
if test -s "$TEMP"
then
	echo oh oh, sgs number appears in existing prefilter file:
	echo 'vvvvvvvvvvvvvvvvv'
	cat $TEMP
	echo '^^^^^^^^^^^^^^^^^^'
	rm $TEMP
	exit 1
fi

exit 0


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
		 
