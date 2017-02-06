use   {{db_name}};
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
    /*主机组成员信息,ip1*/
    member varchar(15) null,
    /*主机组模式,部署client或不部署client,从主机组继承,可修改;为yes则提供client部署能力,为no则不提供,执行任务时候区别对待*/
    modal  varchar(5)  null,
    /*这里app为资产的类型*/
    asset_app  varchar(35)   null,
    /*标签*/
    label  text   null,
    /*最近一次操作时间*/
    c_time     char(19)  null,
    /*最近一次操作人*/
    c_user     varchar(35)  null
) character set utf8;