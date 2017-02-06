use  {{db_name}};
create table if not exists {{table_name}} (
    /*组名*/
    name char(20) not null,
    /*权限列表*/
    privi_list text null,
    /*组成员列表*/
    member  text null,
    /*最近一次操作类型[成员变更member_change/权限变更privilege_change]*/
    `type` varchar(19) null,
    /*最近一次操作时间*/
    opertion_time varchar(19) null,
    /*最近一次操作人*/
    opertion_user varchar(50) default null,
    primary key (name)
) character set utf8;
/*member字段需要','开头*/
replace into {{table_name}} (name, member, `type`, opertion_time, opertion_user) values ('admin', ',admin', "member_change", now(), 'admin');