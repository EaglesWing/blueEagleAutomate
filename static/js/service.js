var commmodule=angular.module('commmodule',[])
commmodule.service('commservice',function($http){
    this.arguments_to_list=function(){
        var list=[]
        for(i in arguments[0]){
            list.push(arguments[0][i])
        }
        return list
    }
    this.request_url=function(url,type,data,success,err, upload){
        if(!url){
            console.log('request_url err.url err.')
            return false
        }
        if(!type){
            var type='get'
        }
        if(!success){
            var success=function(){}
        }

        if(!data){
            var data={}
        }

        if(!err){
            var err=function(){}
        }
        if(type=="post"||type=="POST"||type=="get"||type=="GET"){
            if(type=="post"||type=="POST"){

                if(upload==true){
                    //这里要注意的是，因为是通过anjularjs的http请求来上传文件的，所以要让当前的request成为一个Multipart/form-data请求，anjularjs对于post和get请求默认的Content-Type header 是application/json。通过设置‘Content-Type’: undefined，这样浏览器不仅帮我们把Content-Type 设置为 multipart/form-data，还填充上当前的boundary，如果你手动设置为： ‘Content-Type’: multipart/form-data，后台会抛出异常：the current request boundary parameter is null.
                    
                    var request_data={
                        method:type,
                        url:url,
                        data:data,
                        headers: {'Content-Type':undefined}
                    } 
                }else{
                    //post的参数在data
                    var request_data={
                        method:type,
                        url:url,
                        data:data
                    } 
                }
            }else{
                //get的参数在params
                var request_data={
                    method:type,
                    url:url,
                    params:data
                } 
            }
            
            $http(request_data).then(function successCallback(response){
                    success(response['data'])
                }, function errorCallback(response){
                    if(response['status']==-1||response['status']==403){
                        //403服务重启,-1服务无响应时候跳转到登录界面
                        window.location.href='/'
                    }
                    err(response['data']) 
                })
        }else{
            console.log('request_url err.parameter err.')
            return false
        }
    };
    
    this.textarea_add_event=function(dom){
        var txt_d=dom
        var txt_h=txt_d.css('height')
        
        txt_d.bind('focus',function(){
            txt_d.css('height','300px')
        });
        txt_d.bind('blur',function(){
            txt_d.css('height',txt_h)
        });
    };
    
    this.tab_pane_switch=function(dom, d_val, s_val){
        if(d_val==s_val){
            dom.show()
            dom.addClass('active in')
        }else if(d_val!=""){
            dom.hide()
            dom.removeClass('active in')
        }else if(d_val==""){
            if(dom.hasClass('active')){
                dom.show()
            }else{
                dom.hide()
            }
        }
    };
    this.get_input=function(name,des,id){
        if(id!=undefined){
            var a='id="'+id+'"'
        }else{
            var a=''
        }
        var d='<div '+a+' class="input-group"><span class="input-group-addon">'+name+'</span><input type="text" class="form-control" placeholder="'+des+'"></div>'
        
        return d
    };
    this.alert_confirm=function(txt, ok_fn, cal_fn){
        if(confirm(txt)){
            ok_fn()
        }else{
            cal_fn()
        }
    };


    this.isempty=function(a){
        for ( i in a){
            return false
        }
        return true
    };
    this.field_input_check=function(field_dom){
        if(field_dom.find('input').val()==""){
            field_dom.addClass('error')
        }else{
            field_dom.removeClass('error')
        }
    };
    this.alert_message=function(level, info, detail, direction){
        if(level=="err"||level=="error"){
            var l='negative red'
        }else if(level=="success"||level=="info"){
            var l='success green '
        }else if(level=="warn"||level=="warning"){
            var l='warning brown'
        }
        if(detail==undefined){
            var detail=""
        }
        if(direction==undefined){
            var tpx="10px"
        }else{
            var tpx="35%"
        }
        var html='<div class="ui '+l+'  message raised liter" style="top:'+tpx+';z-index:9999" message><i class="close icon"></i><div class="header">'+info+'</div>'
        if(detail!=undefined){
            html+='<p>'+detail+'</p>'
        }
        html+='</div>'
        var dom=angular.element('.body')
        dom.append(html)
        setTimeout(function(){
            dom.find('i[class="close icon"]').parent().remove()
        }, 2000)
    };
    this.page_jump=function(url){
        if(url.toString().match(/^-{0,1}[0-9]+$/)){
            this.alert_message('err',"window.location.href失败，url错误（"+url+"）")
            return false
        }
        if(url==undefined||url==null){
            return false
        }
        window.location.href=url
    };
    this.open_page=function(url){
        //只能在click事件里使用,不能放timeout和ajax回调
        if(url==undefined||url==null){
            return false
        }
        var w=window.open();
        w.location=url
    };
    this.getcookie=function(name){
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
    };
    this.web_socket=function(ip_and_port,on_open,on_message,on_error,tp){
        //tp默认为ws，否则为wss
        if(tp==undefined){
            var protocol='ws'
        }else{
            var protocol=tp
        }
    
        if(protocol!="ws"&&protocol!="wss"||ip_and_port==undefined){
            return false
        }
    
        var wsserver=protocol+'://'+ip_and_port;

        var ws=new WebSocket(wsserver)
        ws.on_open=on_open
        ws.on_message=on_message
        ws.on_error=on_error
        
        ws.onopen=function(e){
            if(ws.on_open!=undefined){
                ws.on_open(e)
            }
        }
        ws.onmessage=function(e){
            if(ws.on_message!=undefined){
                ws.on_message(e.data)
            }
        }

        ws.onerror =function(e){
            console.log('webserver err.'+e)
            if(ws.on_error!=undefined){
                ws.on_error(e)
            }
            ws.close()
        }
        return ws
    }
    this.body_loading=function(){
        var dm=angular.element('.body')
        dm.find('ui.inverted.dimmer.transition').remove()
        dm.append('<div class="ui inverted dimmer transition visible active" style="display: block !important;"><div class="ui text loader">Loading</div></div>')
        return dm.find('.ui.inverted.dimmer.transition')
    };
    this.get_large_modal=function(title,context){
        return this.get_standard_modal(title, context, 'ui large modal')
    };
    this.get_fullscreen_modal=function(title,context){
        return this.get_standard_modal(title, context, 'ui fullscreen modal')
    };
    this.get_confirm_modal=function(title,context){
        return '<div class="ui small modal" modalhidden><i class="close icon"></i><div class="header">'+title+'</div><div class="content"><p>'+context+'</p></div><div class="actions"><div class="ui negative button">No</div><div class="ui positive right labeled icon button">Yes<i class="checkmark icon"></i></div></div>'
    };
    this.get_standard_modal=function(title,context, modaltype){
        if(context==undefined){
           var  context=''
        }
        if(modaltype==undefined){
            var  modaltype='ui modal'
        }
        return '<div class="'+modaltype+'" modalhidden><i class="close icon"></i><div class="header">'+title+'</div><div class="description" style="min-height:5em">'+context+'</div><div class="actions"><div class="ui black deny button">取消</div><div class="ui positive right labeled icon button">提交<i class="checkmark icon"></i></div></div>'
    };
    this.get_input=function(keyobj, formname){
        var d=''
        for(k in keyobj){
            if(keyobj[k]['other']==undefined){
                var other=''
            }else{
                var other=keyobj[k]['other']
            }
            if(keyobj[k]['fieldattr']==undefined){
                var fieldattr=''
            }else{
                var fieldattr=keyobj[k]['fieldattr']
            }
            
            if(keyobj[k]['select']!=undefined){
                d+='<div class="field"><label>'+keyobj[k]['name']+'</label>'+keyobj[k]['select']+'</div>'
            }else if(keyobj[k]['type']=="calendar"){
                d+='<div class="field"><label>'+keyobj[k]['name']+'</label>'+'<div class="ui date_end calendar" datetype="'+keyobj[k]['calendartype']+'" calendar><div class="ui input left icon"><i class="calendar icon"></i><input type="text" placeholder="'+keyobj[k]['des']+'"></div></div></div>'
                
            }else if(keyobj[k]['type']=="dropdown"){
                var mstr=''
                if(keyobj[k]['menu'] instanceof Array){
                    for(index in keyobj[k]['menu']){
                        var vu=keyobj[k]['menu'][index]
                        pty=''
                        if(vu['property']!=undefined){
                            for(p in vu['property']){
                                pty+='  '+p+'='+'"'+vu['property'][p]+'"'
                            }
                        }
                        mstr+='<option  '+pty+' value="'+vu['key']['name']+'">'+vu['key']['des']+'</option>'
                    }
                }else{
                    for(mk in keyobj[k]['menu']){
                        mstr+='<option   value="'+mk+'">'+keyobj[k]['menu'][mk]+'</option>' 
                    }
                }

                if(keyobj[k]['typekey']=="search"){
                    var cls="ui search dropdown"
                }else{
                    var cls="ui dropdown"
                }
                
                d+='<div class="field" '+other+'><label>'+keyobj[k]['name']+'</label><select class="'+cls+'" id="'+k+'">'+keyobj[k]['des']+' <i class="dropdown icon"></i>'+mstr+'</select></div>'   
            }else if(keyobj[k]['type']=="textarea"){
                if(keyobj[k]['text']!=undefined){
                    var txt=keyobj[k]['text']
                }else{
                    var txt=''
                }
                d+='<div class="field"><label>'+keyobj[k]['name']+'</label><textarea class="'+k+'" rows="1" placeholder="'+keyobj[k]['des']+'" style="height:120px" '+other+'>'+txt+'</textarea></div>'
            }else{
                if(formname!=undefined){
                    d+='<div class="field" '+fieldattr+'><label>'+keyobj[k]['name']+'</label><input type="text" name="'+k+'" placeholder="'+keyobj[k]['des']+'" ' +other+ '  required><span style="color:red" ng-show="'+formname+'.'+k+'.$dirty && '+formname+'.'+k+'.$invalid"><span ng-show="'+formname+'.'+k+'.$error.required">请输入"'+keyobj[k]['des']+'".</span></div>'
                }else{
                    d+='<div class="field" '+fieldattr+'><label>'+keyobj[k]['name']+'</label><input type="text" name="'+k+'" placeholder="'+keyobj[k]['des']+'" ' +other+ ' ></div>'
                }
            }

            
        }
        return d
    };
    this.get_input_form=function(name,keyobj){
        return '<form name="'+name+'" class="ui form" novalidate>' +this.get_input(keyobj,name)+ '</form>'
    };
    this.get_progress_bar=function(des){
        if(des==undefined){
            var des=''
        }
        return '<div class="ui teal progress" data-percent="0" id="progressbar"><div class="bar"><div class="progress"></div></div><div class="label">'+des+'</div></div>'
    };
    this.get_multipart=function(form_head_des, form_head_tail){
        if(form_head_des==undefined){
            var form_head_des='选择文件:'
        }
        if(form_head_tail==undefined){
            var form_head_tail=''
        }
        return '<div class="ui warning message" message><i class="close icon"></i><div class="header">'+form_head_des+' </div>'+form_head_tail+' </div><div class="ui column"><div class="ui form"><div class="field"><div class="ui fluid input"><input type="text" placeholder="选择文件" class="replaceuplaod" disabled></input></div></div></div><div style="margin:10px 30px 10px 0px"><button class="negative ui button" style="position:relative;">选择文件<i><form method="post" enctype="multipart/form-data" class="uploadfile form-control"><input type="file" name="file" style="position:absolute;top:0;left:0;height:100%;width:100%;filter:alpha(opacity:0);opacity: 0;"></form></i></button><button class="positive ui button upload">上传</button></div></div>'
    };
    this.get_upload=function(title, bar_des, form_head_des, form_head_tail){
        var context=this.get_multipart(form_head_des, form_head_tail)
        context+=this.get_progress_bar(bar_des)
        return this.get_standard_modal(title, '<div class="ui segment">'+context+"</div>")
    };
    this.uploadfile=function(id, add_data, s_fn, e_fn){
        if(typeof id=="string"){
            fromdata=new FormData(angular.element(id)[0])
        }else{
            fromdata=new FormData(id[0])
        }
        
        if(add_data!=''&&add_data!=null&&typeof(add_data)!=undefined){
            fromdata.append(add_data['k'],add_data['v'])
        }

        this.request_url('/upload', 'post', fromdata, s_fn, e_fn, true)
    };
    this.get_message=function(head, context, level){
        if(level=="info"){
            var color='info'
        }else if(level=="warn"||level=="warning"){
            var color='warning'
        }else if(level=="err"||level=="error"){
            var color='negative'
        }
        return '<div class="ui '+color+' message" message><i class="close icon"></i><div class="header">'+head+'</div><p>'+context+'</p></div>'
    };
    this.get_multiple_search_selection=function(id, ngrepeatoption){
        return '<div class="feild datacontent"><div class="ui form"><select class="ui fluid search dropdown" multiple="" id="'+id+'">'+ngrepeatoption+'</select></div></div>'
    };
    this.get_pagination_menu=function(sum, id, name){
        if(name!=undefined){
            name='name="'+name+'"'
        }else{
            name=''
        }

        var h='<div id="'+id+'"  '+name+' class="ui center pagination red menu" pagination><a class="icon item prev"><i class="left chevron icon"></i></a>'

        if(sum==undefined||sum==0||sum<1||sum==1||sum==""){
            return ''
        }
        for(var i=1;i<=sum;i++){
            if(i==1){
                h+='<a class="item active">'+i+'</a>'
            }else{
                if(i >3 && i< sum-2){
                    h+='<a class="item" style="display:none">'+i+'</a>'
                }else{
                    h+='<a class="item">'+i+'</a>'
                }
                        
                if(i==3&&sum > i){
                    h+='<div class="disabled item">...</div>'
                }
            }
    
        }
        h+='<a class="icon item next"><i class="right chevron icon"></i></a></div>'
        
        return h
    };
    this.get_structured_comp_table=function(head, trbody, ismodal, modaltp){
        if(ismodal!=undefined){
            return this.get_standard_modal(ismodal['title'],'<table class="ui celled structured table"><thead><tr>'+head+'</tr></thead><tbody>'+trbody+'</tbody></table>', modaltp)
        }else{
            return '<table class="ui celled structured table"><thead><tr>'+head+'</tr></thead><tbody>'+trbody+'</tbody></table>'
        }
        
    };
    this.json_to_obj=function(d){
        return JSON.parse(d)
    };
    this.obj_to_json=function(d){
        return JSON.stringify(d)
    };
    this.get_checkbox=function(checked, label){
        if(label!=undefined){
            label='<label>'+label+'</label>'
        }else{
            label=''
        }
        if(checked!=undefined){
            ischecked='checked'
        }else{
            ischecked=''
        }
        return '<div class="ui checkbox" checkbox><input type="checkbox" name="example" '+ischecked+'>'+label+'</div>'
    };
    this.get_celled_checkbox_list=function(master, slavehtml, key){
        var html='<div class="ui celled relaxed list" keylist="'+key+'" checkboxlist><div class="item"><div class="ui master checkbox"><input type="checkbox" name="all"><label>'+master+'</label></div><div class="list">'+slavehtml+'</div></div></div>'
        return html
    };
    this.dict_in_list=function(list, key){
        for(i in list){
            innerloop:
            for(k in list[i]){
                if(k==key){
                    return true
                }
                break innerloop
            }
        }
        return false
    }
})