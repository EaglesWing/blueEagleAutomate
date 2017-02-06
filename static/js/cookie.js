function setcookie(name,value,exp_time,split){
    //对k-v串进行简单的字符串编码
    var name=escape(name);
    var value=escape(value);
    var expires=new Date();
    //过期时间
    expires.setTime(expires.getTime() + exp_time*3600000);
    split = split == "" ? "" : ";split=" + split;  
    _expires = (typeof exp_time) == "string" ? "" : ";expires=" + expires.toUTCString();  
    document.cookie = name + "=" + value + _expires + split;
}

function getcookie(name){
    var name=escape(name);
    var cookies=document.cookie;
    name+="=";
    var position=cookies.indexOf(name);
    if(position != -1){
        var start=position+name.length;
        var end=cookies.indexOf(';',start);
        if (end == -1){
            end=cookies.length
        }
        var value=cookies.substring(start,end);
        return value
    }
    return '';
}

function deletecookie(name,split){
    var name=escape(name)
    var expires=new Date();
    split = split == "" ? "" : ";split=" + split;  
    document.cookie = name + "="+ ";expires=" + expires.toUTCString() + split;  
}

//记住登录cookie

signin=$(function(){
console.log(getcookie('user'))    
console.log(getcookie('pwd'))
    $('.form-signin input[type="user"]').val(getcookie('loginuser'))
    $('.form-signin input[type="password"]').val(getcookie('loginpassword'))
    $('.form-signin label').click(function(){
        if($(this).find(":checkbox").prop('checked')==true){
            signin.setcookie()
        }
    })
    signin.setcookie=function(){
        var uname=$('.form-signin input[type="user"]').val()
        var pwd=$('.form-signin input[type="password"]').val()
        setcookie("loginuser",uname,24,';');
        setcookie("loginpassword",pwd,24,';');
    }
})