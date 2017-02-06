use    {{db_name}};
create table  if not exists {{table_name}} (
    /*id标示*/
    id int auto_increment primary key,
    /*ip信息(电信IP)*/
    ip char(15) not null,
    /*变更前信息*/
    old_info text  null,
    /*变更后信息*/
    new_info text  null,
    /*操作类型modify,delete*/
    c_type     char(10)     not null,
    /*操作用户*/
    c_user    varchar(35)  not null,
    /*操作时间*/
    c_time     char(19)     not null
) character set utf8;