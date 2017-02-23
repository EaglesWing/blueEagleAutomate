/*任务list信息*/
use   {{db_name}};
create table if not exists {{table_name}} (
    /*id*/
    id int auto_increment primary key,
    /*任务ID，只接收英文字母*/
    task_id  varchar(100) null,
    /*任务描述/名称*/
    des     text null,
    /*路径*/
    filename text null,
    /*备注信息*/
    remark text null,
    /*操作时间*/
    c_time char(19)    null,
    /*操作人*/
    c_user varchar(35)   null
) character set utf8;