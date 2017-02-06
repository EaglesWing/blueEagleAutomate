use {{db_name}};
create table if not exists {{table_name}} (
    id int auto_increment primary key,
    /*账号名,邮件地址/微信公众号联系人*/
    name varchar(50) not null,
    /*账号描述*/
    des text null,
    /*账号类型/邮箱/微信*/
    `type` varchar(10) null,
    /*创建时间*/
    c_time varchar(19) null,
    /*创建人*/
    c_user varchar(35) null 
) character set utf8;
