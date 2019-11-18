#!/bin/bash

# I usually do this in ~/mscac to update ~/mscac/public_html
# it depends on having my ssh public key (id_rsa.pub) known by gradbackup@gradapps.cs.toronto.edu
# lloyd will have to set this up for you.

GRAD_APPS="gradbackup@gradapps.cs.toronto.edu"
CMD="rsync -av $GRAD_APPS:archive/mscac.2020/mscac20/public_html ."

if test ! -d public_html
then
	/bin/pwd
	echo where are you? cannot see public_html dir in .
	exit 2
fi

echo trying ssh $GRAD_APPS whoami
echo if hangs you probably need to get on CSLAB vpn..
ssh $GRAD_APPS whoami

echo okay then.. about exec: $CMD
read -p "hit enter to continue ... > " JUNK
set -x
$CMD

