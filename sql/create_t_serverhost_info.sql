use   {{db_name}};
create table if not exists {{table_name}} (
    /*id*/
    id int auto_increment primary key,
    /*��Ʒ��*/
    line varchar(50)  null,
    /*ҵ��*/
    product varchar(50)  null,
    /*Ӧ��(����Ϊ���),ͬ��line-product��Ψһ*/
    app varchar(50)  null,
    /*������id, ͬ��line-product-app��Ψһ*/
    group_id text null,
    /*�������Ա��Ϣ,ip1*/
    member varchar(15) null,
    /*������ģʽ,����client�򲻲���client,��������̳�,���޸�;Ϊyes���ṩclient��������,Ϊno���ṩ,ִ������ʱ������Դ�*/
    modal  varchar(5)  null,
    /*����appΪ�ʲ�������*/
    asset_app  varchar(35)   null,
    /*��ǩ*/
    label  text   null,
    /*���һ�β���ʱ��*/
    c_time     char(19)  null,
    /*���һ�β�����*/
    c_user     varchar(35)  null
) character set utf8;