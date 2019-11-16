#!/bin/bash


#exec'd from gradapps prefilter app

case $PATH in
	*WINDOWS* )
		CMD="cygstart"
		;;
	*)
		CMD="open -a Preview.app"
		;;
esac

for i in $*
do
	if test -f $i
	then
		#ls -l $i
		$CMD $i
	else
		echo $0: $i not found
	fi
done

