/*信息收集模板信息*/
use  {{db_name}};
create table if not exists {{table_name}} (
    /*ID*/
    id int auto_increment primary key,
    /*任务ID，只接收英文字母*/
    template_id  varchar(100) null,
    /*任务描述*/
    des     text null,
    /*备注*/
    remark text null,
    /*操作时间*/
    c_time char(19)    null,
    /*操作人*/
    c_user varchar(35)   null
) character set utf8;
replace into {{table_name}} (`c_user`,`remark`,`des`,`template_id`, c_time) values('admin' ,'记录平台接口和浏览器请求信息' ,'平台审计' ,'platform_history' , now()) 