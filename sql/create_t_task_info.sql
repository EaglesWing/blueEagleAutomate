/*����list��Ϣ*/
use   {{db_name}};
create table if not exists {{table_name}} (
    /*id*/
    id int auto_increment primary key,
    /*����ID��ֻ����Ӣ����ĸ*/
    task_id  varchar(100) null,
    /*��������/����*/
    des     text null,
    /*·��*/
    filename text null,
    /*��ע��Ϣ*/
    remark text null,
    /*����ʱ��*/
    c_time char(19)    null,
    /*������*/
    c_user varchar(35)   null
) character set utf8;