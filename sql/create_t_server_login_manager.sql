use  {{db_name}};
create table if not exists {{table_name}} (
    /*��Ե�̨���������õ�¼��Ϣ*/
    /*ip*/
    ip char(15) not null primary key,
    /*��������¼�û�*/
    `user`    varchar(35)  null,
    /*��������¼�˿�*/
    port      int(5) null,
    /*��������¼����*/
    pwd       text  null,
    /*����ʱ��*/
    c_time char(19)    null,
    /*������*/
    c_user varchar(35)   null
) character set utf8;