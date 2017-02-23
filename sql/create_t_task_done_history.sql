/*任务执行完成记录,分表;前端设置任务为完成后把数据从servers里移过来做记录*/
use         {{db_name}};
create table if not exists {{table_name}} (
    id int auto_increment primary key,
    /*任务名称*/
    task_name  text null,
    /*telecom_ip*/
    telecom_ip varchar(19)  null,
    /*主机模式*/
    modal varchar(10)  null,
    /*登录信息;modal为no时候;密码为密文*/
    login_info text null,
    /*所属主机组*/
    group_id text null,
    /*资产应用类型*/
    asset_app varchar(35)  null,
    /*执行的任务信息及状态*/
    task_info text null,
    /*服务器(ip)所在的产品线-业务-分类-主机key信息*/
    server_key text null,
    /*操作人*/
    c_user  varchar(35) null,
    /*操作时间*/
    c_time  varchar(19) null
) character set utf8;