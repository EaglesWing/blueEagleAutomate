use  {{db_name}};
create table if not exists {{table_name}} (
    /*id*/
    id int auto_increment primary key,
    /*电信ip(主IP)-必须*/
    telecom_ip char(15) not null,
    /*联通ip-非必须*/
    unicom_ip char(15) null,
    /*内网ip-非必须*/
    inner_ip char(15) null,
    /*产品线-必须(字母)*/
    line varchar(50) not null,
    /*业务-必须(字母)*/
    product varchar(50) not null,
    /*应用-必须(字母)*/
    app varchar(50) not null,
    /*资产描述-必须;格式为(产品线-业务-应用)*/
    `describe` varchar(120) not null,
    /*机房-非必须*/
    idc  varchar(80) not null,
    /*资产编号-非必须*/
    serial_number    varchar(100)  null,
    /*负责人-非必须*/
    owner    varchar(100)  null,
    /*系统版本-非必须*/
    os    varchar(100)  null,
    /*内存-非必须*/
    mem text null,
    /*磁盘-非必须*/
    disk text null,
    /*CPU-非必须*/
    cpu text null,
    /*厂商-非必须*/
    firm text null,
    /*备注-非必须*/
    remark text null,
    /*最近一次操作时间*/
    c_time     char(19)     not null,
    /*最近一次操作人*/
    c_user     varchar(35)  not null
) character set utf8;