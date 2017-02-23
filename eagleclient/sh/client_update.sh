#!/bin/bash
:<<!
更新客户端时候使用
!
curr_path=$(cd $(dirname $0);pwd)
update_pkg=$curr_path/../../file/eagleclient.zip
client_path=$curr_path/../../

log_info "client update begin."
if [[ -e $curr_path/eagleclient.sh ]];then
    . $curr_path/eagleclient.sh
else
    log_err 'client update err.'
fi

if [[ ! -e $update_pkg   ]];then
    log_err "client update err.can not find $update_pkg"
else
    cp -rf $client_path/eagleclient{,_bak}
    yes|unzip -q $update_pkg -d  $client_path &&     client_restart  && client_start_check
    if [[ $? == 0 ]];then
        log_info "client update done."
    else
        log_err 'client update err.unzip err.'
    fi
fi
exit $?
