#!/bin/bash
dir=$1
filter=$2
getfacl ${dir} -R 2>/dev/null|grep -P "${filter}"|awk '{a=a"/"$NF"::::::"}END{print a}'