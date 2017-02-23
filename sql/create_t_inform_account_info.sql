use {{db_name}};
create table if not exists {{table_name}} (
    id int auto_increment primary key,
    /*邮箱主账号名*/
    name varchar(50) null,
    /*邮箱密码*/
    pwd text null,
    /*邮箱描述信息*/
    des text null,
    /*账号类型*/
    `type` varchar(10) null,
    /*邮箱服务器地址*/
    email_server varchar(50) null,
    /*smtp_ssl_port:ssl认证时候使用,无信息则为不使用*/
    smtp_ssl_port char(5)  null,
    /*smtp_port:邮箱服务器地址端口号,无信息则使用默认25*/
    smtp_port     char(5)   null,
    /*微信公众号ID,微信唯一,所以只提供ID和secret配置*/
    wechatid  varchar(50) null,
    /*微信公众号secret*/
    wechatsecret text null,
    /*状态:一个类型只且唯一使用一个主账号*/
    status    varchar(15)   null,
    /*联系人信息[成员]*/
    member   text     null,
    /*操作时间*/
    c_time    varchar(19)   null,
    /*操作人*/
    c_user    varchar(35)   null
) character set utf8;