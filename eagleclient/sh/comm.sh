#/bin/sh
curr_path=$(cd $(dirname $0);pwd)
curr_time=$(date "+%Y-%M-%d-%H-%M")
function log_echo(){
    time=$(date +'%F %T')
    type=$1
    info=$2
    logfile=$3
    [[ $# < 3 ]] && echo "parameter err." && return 1
    if [[ $type == 'info' ]];then
        ifn="\033[32;1m$time - ${FUNCNAME[1]} - $type - \033[0m $info"
    elif [[ $type == 'warn' ]];then
        ifn="\033[33;1m$time - ${FUNCNAME[1]} - $type - \033[0m $info"
    elif [[ $type == 'err' ]];then
        ifn="\033[31;1m$time - ${FUNCNAME[1]} - $type - \033[0m $info"
    else
        echo "parameter err." 
        return 1
    fi
    echo -e $ifn
    if [[ $logfile ]];then
        echo -e $ifn >> $logfile 2>&1
    fi
    return 0
}