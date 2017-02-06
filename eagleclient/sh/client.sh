#!/bin/bash
:<<!
客户端部署和停止/删除使用
部署路径信息在client/config/config.xml里

部署：
    1：twisted:把eagleclient.zip推送到 /temp 目录并解压和调用当前脚本
    2：当前脚本把目录文件拷贝到部署路径，启动client.py
    3: 当前脚本清理多余文件
停止/删除：
    1: 调用当前脚本
    2: 当前脚本stop client.py  并删除部署目录
!
curr_path=$(cd $(dirname $0);pwd)
config_file=$curr_path/../config/config.xml 

deploy_path=$(awk -F'[ >]+' '/server/{for(i=1;i<=NF;i++){if($i~"^deploy_path"){split($i,a,"=");match(a[2],/[^ ](.*)[^ ]/,b);print b[1]}}}' $config_file)

client_file=$deploy_path/eagleclient/client.py

log_file=/tmp/client.sh.log
> $log_file
dos2unix *.sh >/dev/null 2>&1
. ${curr_path}/util.sh
. ${curr_path}/comm.sh


deploy_home_path_clear(){
    if [[ -n $deploy_path && ! $deploy_path =~ ^(/|/root|/home)\$ ]];then
        log_info "delete $deploy_path"
        rm -rf $deploy_path
    fi
}

client_stop(){
    log_info "stop  client.py"
    python $client_file stop >> $log_file 2>&1 &
}

client_start(){
    log_info "client start begin."
    python $client_file start >> $log_file 2>&1 &
}

client_start_check(){
    for ((;1<2;));do
        if ps aux|grep -E 'python.*client.py'|grep -v grep >/dev/null 2>&1;then
            log_info "client start success."
            break
        else
            ((i++))
            log_warn "client start faild,sleep 5s,this $i 30s timeout"
            if [[ $i == 10 ]];then
                log_warn "client start faild,timeout"
                break
            fi
            sleep 3
            client_restart
        fi
    done
}

client_restart(){
    log_info "client restart"
    python $client_file restart >/dev/null 2>&1 &
}

client_deploy(){
    log_info "client deploy"
    deploy_home_path_clear
    mkdir -p $deploy_path >/dev/null 2>&1 
    cp /tmp/eagleclient.zip $deploy_path && yes| unzip $deploy_path/eagleclient.zip -d $deploy_path
    
    client_restart && rm -rf /tmp/eagleclient /tmp/eagleclient.zip >/dev/null 2>&1 
}

client_update(){
    update_file="${curr_path}/client_update.sh"
    log_info "client update"
    if [[ -e $update_file ]] ;then
        chmod a+x $update_file >/dev/null 2>&1 
        nohup $update_file  >> $log_file 2>&1 &
    else
       log_err "update err.can not find ${update_file}"
    fi
}


if [[ $1 == "stop" ]];then
    client_stop
    deploy_home_path_clear
elif [[ $1 == "start" ]];then
    client_start
    client_start_check
elif [[ $1 == "deploy" ]];then
    client_deploy
    client_start_check
elif [[ $1 == "update" ]];then
    client_update
elif [[ $1 == "restart" ]];then
    client_restart
    client_start_check
fi
