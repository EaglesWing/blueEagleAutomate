/*��Ϣ�ռ���¼*/
use   {{db_name}};
create table if not exists {{table_name}} (
    /*id*/
    id int auto_increment primary key,
    /*����ID��ֻ����Ӣ����ĸ*/
    template_id  varchar(100) null,
    /*ip��ַ*/
    ip  varchar(15) null,
    /*�ռ���Ϣ,json��ʽ��a=>b:::c=>d��ʽ(�൱��һά��ϣ;��ֵ֧��һά)*/
    info     longtext null,
    /*��Ϣ�ռ�ʱ��*/
    c_time char(19)    null
) character set utf8;