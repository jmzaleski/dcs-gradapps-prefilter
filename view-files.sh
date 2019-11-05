#!/bin/bash

#exec'd from gradapps prefilter app

for i in $*
do
	if test -f $i
	then
		ls -l $i
		open -a Preview.app $i
	else
		echo sorry $i not found
	fi
done

