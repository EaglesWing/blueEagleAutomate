/*任务创建记录*/
use         {{db_name}};
create table if not exists {{table_name}} (
    id int auto_increment primary key,
    /*任务名称*/
    task_name  text null,
    /*自定义任务名称*/
    custom_name  text null,
    /*任务类型*/
    task_type text null,
    /*自定义任务类型*/
    custom_type text null,
    /*关联任务id*/
    relevance_id varchar(80) null,
    
    /*修改为存放任务状态,用于前端增序排序显示 failed:执行失败(1)/ready:倒计时状态(2)/running:执行状态(3)/cancel:取消执行(4)/success:执行成功(5)/done:标记为完成状态,不在接受处理状态(6), offline(7)*/
    status varchar(25) null,
    /*执行时间,为0则立即执行*/
    execute_time varchar(19) null,
    /*任务创建时间*/
    create_time varchar(19) null,
    /*任务详情信息在servers表*/

    /*是否包含预处理任务*/
    isprepro varchar(10)  null,
    /*预处理任务参数*/
    `parameters` text null,
    /*任务中主机所在的产品线-业务-类型-group信息;用于详情展示;ip唯一,详情页直接取ip*/
    server_info text null,
    /*关联任务详情信息*/
    task_info text null,
    /*操作人*/
    c_user  varchar(35) null,
    /*操作时间*/
    c_time  varchar(19) null
) character set utf8;