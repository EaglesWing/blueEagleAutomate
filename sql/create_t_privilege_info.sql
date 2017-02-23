use  {{db_name}};
create table if not exists {{table_name}} (
    /*权限名*/
    name char(100) not null,
    /*权限描述*/
    des  text null,
    /*备注*/
    remark  text null,
    primary key (name)
) character set utf8;
