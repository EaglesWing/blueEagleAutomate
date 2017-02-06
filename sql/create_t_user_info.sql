use    {{db_name}};
create table if not exists {{table_name}} (
    /*用户名*/
    `user` varchar(30) not null,
    /*密码*/
    pwd  char(32)  null,
    /*描述信息[当前用户的描述信息]*/
    des text null,
    /*创建时间[管理员创建用户的时间]*/
    c_time char(19)  null,
    /*密码修改时间/没修改过密码则为注册时间*/
    m_pwd_time char(19) null,
    /*最后登录时间*/
    last_login char(19) null,
    /*操作类型[管理员创建用户/用户自己修改密码]*/
    `type` char(19) null,
    /*创建当前用户的操作人*/
    c_user varchar(30) null,
    primary key (user)
) character set utf8;
/*执行sql时候会创建admin用户并设置密码为空*/
replace into {{table_name}} (`user`, pwd, c_time, `type`, des, c_user) values ('admin', null, now(), 'create', '管理员', 'admin');