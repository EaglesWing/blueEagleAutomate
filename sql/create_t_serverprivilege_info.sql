use  {{db_name}};
create table if not exists {{table_name}} (
    /*id*/
    id int auto_increment primary key,
    /*产品线*/
    line varchar(50)  null,
    /*业务*/
    product varchar(50)  null,
    /*应用(这里为类别),同个line-product下唯一*/
    app varchar(50)  null,
    /*主机组id, 同个line-product-app下唯一*/
    group_id text null,
    /*权限规则*/
    role text null,
    /*主机组开放的权限列表,用于存放权限信息*/
    privilege text null,
    /*规则所匹配的文件列表*/
    filelist  longtext  null,
    /*最近一次操作时间*/
    c_time     char(19)     null,
    /*最近一次操作人*/
    c_user     varchar(35)   null
) character set utf8;