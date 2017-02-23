use {{db_name}};
create table if not exists {{table_name}} (
    /*id*/
    id int auto_increment primary key,
    /*ip*/
    telecom_ip char(15) null,
    /*状态*/
    status varchar(12) null,
    /*使用的工具*/
    tool_path  text  null,
    /*操作时间*/
    c_time char(19)    null,
    /*操作人*/
    c_user varchar(35)   null
) character set utf8;