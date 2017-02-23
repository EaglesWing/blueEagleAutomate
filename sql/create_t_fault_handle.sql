use {{db_name}};
create table if not exists {{table_name}} (
    /* */
    id int auto_increment primary key,
    /*故障名称*/
    name varchar(45) null,
    /*故障所发生的服务器*/
    ip varchar(15) null,
    /*故障key信息*/
    zone_name varchar(15) null,
    /*处理状态*/
    status varchar(30) null,
    /*故障描述*/
    faultdes text null,
    /*故障处理时候的详细信息*/
    remark text null,
    /*故障发生时间（入库）*/
    h_time varchar(19) null,
    /*处理时间*/
    c_time varchar(19) null,
    /*操作用户*/
    c_user varchar(19) null
);