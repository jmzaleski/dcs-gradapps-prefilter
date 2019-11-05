#!/bin/bash

#run from mscac20 directory or hard code path

if test ! -d public_html
then
	echo are you in right directory? $0 must be run from gradapps archive directory 1>&2
	exit
fi

find $PWD/public_html/data -name profile.data 
