#!/bin/bash
#$1为类型run/stop/restart(执行/停止/重新脚本时候使用) $2为任务名称，$3为cmd/filepath
curr_path=$(cd $(dirname $0);pwd)
dos2unix *.sh >/dev/null 2>&1
. ${curr_path}/comm.sh
[[ $# < 3 ]] && echo 'parameter err.' && exit 1

run_type=$1
task_name=$2
cmd=$3

log_path=${curr_path}/log/task_log/${task_name}

log_file=$log_path/$(echo $cmd|sed  -r 's#.*/(.*)$#\1#g').log
#在log_file后引用
. ${curr_path}/util.sh

mkdir -p $log_path >/dev/null 2>&1


if [[ -f $cmd && $run_type == 'run' || $run_type == "restart" ]];then
    > $log_file
    {
        dos2unix $cmd;
        chmod u+x $cmd;
    }>/dev/null 2>&1
elif [[ $run_type == 'run' || $run_type == "restart" ]];then
    log_err 'cmd err.can not find the cmd file.'
fi

function get_system_info(){
    log_info "get system cpu/mem used status."
    pct=$(ps aux|grep -v grep |grep -E "$cmd" >/dev/null 2>&1|wc -l)
    if [[ $pct == 0 ]];then
        log_info "can not find any process as sam as $cmd.skip check."
        return 0
    else
        #100*(MemTotal-MemFree-Buffers-Cached)/MemTotal
        mem_ret=$(awk '/^MemTotal:/{mtoal=$2}/^MemFree:/{mfree=$2}/^Buffers:/{buffer=$2}/^Cached:/{catched=$2}END{cmp=100*(mtoal-mfree-buffer-catched)/mtoal;if(cmp>90){print 1}else{print 0}}' /proc/meminfo)
        cpu_ret=$(vmstat |awk '/id/{getline;if($15<10){print 1}else{print 0}}')
        if [[ $mem_ret == 0 && $cpu_ret == 0 ]];then
            log_info "cpu/mem status check success."
            return 0
        else
            log_info "cpu/mem status check success."
            return 1
        fi
    fi
}

#检查是否有当前任务存在,若有则检查cpu和内存使用率,没有则跳过检查
pro_count=$(ps aux|grep -v grep |grep -E "$cmd" >/dev/null 2>&1|wc -l)
if [[ $pro_count != 0 ]];then
    log_warn "find $pro_count process sam as $cmd."
    sm_check=0
    for((;1<2;));do
        log_info "get system cpu/mem the $sm_check."
        #获取系统CPU和内存使用率,返回1/0
        get_system_info
        ret=$?
        if [[ ${ret} == 1 ]];then
            (($sm_check++))
            #检查100次还不正常则退出，说明有任务异常，半小时
            if [[ $sm_check > 360 ]];then
                exit 1
            fi
            sleep 5
        fi
        break
    done
fi

function task_stop(){
    log_warn "type is ${run_type},kill process of $0[ \\\t]+(run|restart)[ \\\t]+${task_name}[ \\\t]+$cmd."
    if [[ ${run_type} == "stop"  ]];then
        ps aux|grep -E "$0[ \t]+(run|restart)[ \t]+${task_name}[ \t]+$cmd"|awk '{print "kill -9  "$2}' | bash &
    else
        ps aux|grep -Ev "(grep|$$|$(awk '/PPid:/{print $NF}' /proc/$$/status))" |grep -E "$0[ \t]+(run|restart)[ \t]+${task_name}[ \t]+$cmd"|awk '{print "kill -9  "$2}' | bash &
    fi
}

log_info "$run_type $cmd begin."

if [[ $run_type == 'run' ]];then
    $cmd >>$log_file
elif [[ $run_type == 'stop' ]];then
    task_stop >>$log_file
elif [[ $run_type == 'restart' ]];then
    task_stop >>$log_file
    $cmd >>$log_file
else
    log_err "can not support parameter ${run_type}"
fi
ret=$?
if [[ $ret == 0 ]];then
    log_info "$run_type $cmd success."
else
    log_info "$run_type $cmd faild."
fi
echo ":::task call done $ret." >> $log_file
exit $ret