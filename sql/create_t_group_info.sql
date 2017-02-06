use  {{db_name}};
create table if not exists {{table_name}} (
    /*组名*/
    name char(20) not null,
    /*描述:组名描述*/
    des    text not null,
    /*创建时间*/
    c_time varchar(19) null,
    /*创建人*/
    c_user varchar(35) null,
    primary key (name)
) character set utf8;
replace into {{table_name}} (name, des, c_time, c_user) values ('admin', '管理员组', now(), 'admin');
