use    {{db_name}};
create table  if not exists {{table_name}} (
    /*key标示*/
    `key`  varchar(100)   not null  primary key,
    /*对应的值信息*/
    `value` text null,
    /*操作时间*/
    c_time varchar(19)  null,
    /*操作人*/
    c_user varchar(35)  null
) character set utf8;