use         {{db_name}};
create table if not exists {{table_name}} (
    /*登录信息管理由资产的产品线细化到负责人,取登录信息时候按照最小匹配获取*/
    /*id*/
    id int auto_increment primary key,
    /*产品线*/
    line varchar(50)  null ,
    /*业务*/
    product varchar(50)  null,
    /*应用*/
    app varchar(50)  null,
    /*机房*/
    idc varchar(80)  null,
    /*负责人*/
    owner varchar(100)  null,
    /*类型(动态获取登录信息还是静态的)*/
    `type` varchar(30) null,
    /*服务器登录用户*/
    `user`   text  null,
    /*服务器登录端口*/
    port     text null,
    /*服务器登录密码*/
    pwd       text  null,
    /*操作人*/
    c_user varchar(35)  null,
    /*操作时间*/
    c_time varchar(19)  null
) character set utf8;