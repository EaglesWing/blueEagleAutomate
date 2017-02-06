/*信息收集记录*/
use   {{db_name}};
create table if not exists {{table_name}} (
    /*id*/
    id int auto_increment primary key,
    /*任务ID，只接收英文字母*/
    template_id  varchar(100) null,
    /*ip地址*/
    ip  varchar(15) null,
    /*收集信息,json格式或a=>b:::c=>d格式(相当于一维哈希;且值支持一维)*/
    info     longtext null,
    /*信息收集时间*/
    c_time char(19)    null
) character set utf8;