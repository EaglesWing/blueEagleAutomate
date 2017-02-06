use  {{db_name}};
create table if not exists {{table_name}} (
    /*针对单台服务器设置登录信息*/
    /*ip*/
    ip char(15) not null primary key,
    /*服务器登录用户*/
    `user`    varchar(35)  null,
    /*服务器登录端口*/
    port      int(5) null,
    /*服务器登录密码*/
    pwd       text  null,
    /*操作时间*/
    c_time char(19)    null,
    /*操作人*/
    c_user varchar(35)   null
) character set utf8;