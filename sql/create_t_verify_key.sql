use    {{db_name}};
create table if not exists {{table_name}} (
    /*ID*/
    id int auto_increment primary key,
    /*key名称*/
    name varchar(35) null,
    /*key描述*/
    des  text null,
    /*key的值*/
    `value`  text null,
    /*操作时间*/
    opertion_time varchar(19) null,
    /*操作人*/
    opertion_user varchar(35) null
) character set utf8;
insert into {{table_name}} (name, des, `value`, opertion_time, opertion_user) values('verify_key', '后台认证key', '1233211234567', now(), 'admin')
