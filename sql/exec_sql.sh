#!/bin/bash
curr_path=$(cd $(dirname $0);pwd)
curr_scr_n=$(basename $0)
curr_time=$(date "+%Y-%M-%d-%H-%M")
sql_path=$curr_path
db_cfg=$sql_path/../config/db_config.xml
dos2unix $db_cfg >/dev/null 2>&1
dfile=$1

function get_mysql_pwd(){
    py_p=$sql_path/../encrypt.py
    en_pwd=$(sed -rn '/<pwd>/{s|<pwd>([^ ]+)</pwd>|\1|p}'  $db_cfg)
    python $py_p decode $en_pwd
}
#遍历curr_path下的所有建表sql(表的规则为create_x;x为表名)，并执行
for t in $(ls $curr_path/create_*.sql);do
    {
        table=$(echo $t|sed -r 's/.*create_(.*).sql/\1/')
        db_pwd=$(get_mysql_pwd)
        db_name=$(sed -rn '/<db_name>/{s|<db_name>([^ ]+)</db_name>|\1|p}' $db_cfg)
        db_user=$(sed -rn '/<user>/{s|<user>([^ ]+)</user>|\1|p}' $db_cfg)
        host=$(sed -rn '/<ip>/{s|<ip>([^ ]+)</ip>|\1|p}' $db_cfg)
        sed -ri  "s/\{\{table_name\}\}/$table/g;s/\{\{db_name\}\}/$db_name/" $t
        if [[ -n $dfile ]];then
            if [[ $curr_path/$dfile == $t ]];then
                mysql -h$host -u$db_user -p$db_pwd < $t
                exit 0
            else
                continue
            fi
            
        else
            mysql -h$host -u$db_user -p$db_pwd < $t
        fi
        
        if [[ $? != 0 ]];then
            echo "ERR:"$t
        fi
    }&
done