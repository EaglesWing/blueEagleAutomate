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
    /*主机组描述*/
    group_des text null,
    /*主机组模式,成员部署client和不部署client,组员可继承或修改;为yes则提供client部署能力,为no则不提供,执行任务时候区别对待*/
    modal  varchar(5)  null, 
    /*主机组备注*/
    remark text null,
    /*最近一次操作时间*/
    c_time     char(19)     null,
    /*最近一次操作人*/
    c_user     varchar(35)   null
) character set utf8;