/*任务关联信息表*/
use         {{db_name}};
create table if not exists {{table_name}} (
    id int auto_increment primary key,
    /*任务关联的ID，唯一*/
    relevance_id varchar(100) null,
    /*关联的任务名*/
    relevance_name  text null,
    /*关联的任务描述*/
    relevance_remark  text null,
    /*关联的任务分类*/
    relevance_app  text null,
    /*关联的任务分类描述*/
    relevance_app_des  text null,
    /*关联的任务类型*/
    relevance_type  text null,
    /*关联的任务类型描述*/
    relevance_type_des text null,
    /*关联的任务依赖状态*/
    relevance_rely  text null,
    /*关联的任务文件推送路径,服务器modal为no时候需要确保路径存在(若为默认的/tmp/\$\{relevance_id\}/\$\{task_name\};则使用/tmp)*/
    relevance_path text null,
    /*关联的任务list*/
    task_list text null,
    /*操作时间*/
    c_time    varchar(19) null,
    /*操作人*/
    c_user varchar(50) null
) character set utf8;