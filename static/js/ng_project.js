var commmodule=angular.module('commmodule',[])
commmodule.service('commservice',function($http){
        this.arguments_to_list=function(){
        var list=[]
        for(i in arguments[0]){
            list.push(arguments[0][i])
        }
        return list
    }
    this.get_callback=function(...list){
        if(list.length==0){
            console.log('get_callback err.parameter err.')
            return false
        }

        //var list=this.arguments_to_list(arguments)
        var fn_name=list.shift()
        // response 是调用时候传进来的数据
        function fn(response){
            //默认参数长10
            if(response!=undefined){
                return fn_name(response,list[0],list[1],list[2],list[3],list[4],list[5],list[6],list[7],list[8],list[9])
            }else{
                return fn_name(list[0],list[1],list[2],list[3],list[4],list[5],list[6],list[7],list[8],list[9])
            }
        }
        return fn
    };

    this.request_url=function(url,type,data,success,err){
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
                //post的参数在data
                var request_data={
                    method:type,
                    url:url,
                    data:data
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
    
    this.get_modal=function(id, label, title, ok_directive){
        if(ok_directive==undefined){
            var directive_attr=''
        }else{
            var directive_attr=ok_directive
        }
        var d='<div class="modal fade" id="'+id+'" role="dialog" aria-labelledby="'+label+'" aria-hidden="true"><div class="modal-dialog modal-lg"><div id="modal_id" class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="close" aria-hidden="true">&times;</button><h4 class="'+label+'">'+title+'</h4></div><div class="modal-body"></div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal">关闭</button><button type="button" class="btn btn-primary" '+directive_attr+'>确定</button></div></div></div></div>'
        
        return d
    };
    this.get_tabpanel=function(id, title, level, footer){
        //level: primary success info warning danger default
        var d='<div id="'+id+'" class="panel panel-'+level+'"><div class="panel-heading" style="height:30px;padding:0px">'+title+'</div><div class="panel-body" style="padding:0px;height:500px;overflow:auto"></div>'
        if(footer!=undefined){
            d+='<div class="panel-footer"></div>'
        }
        d+="</div>"
        return d
    };
    this.get_ul=function(ul_id, ul_txt){
        if(ul_id==undefined){
            var d='<ul class="nav nav-pills nav-stacked padding-1 margin-1" style="text-align:left"></ul>'
        }else{
            var d='<ul id="'+ul_id+'" class="nav nav-pills nav-stacked padding-1 margin-1" style="text-align:left"><li role="presentation"><a href="##" id="'+ul_id+'" style="padding:0px 0px 0px 5px;maring:2px">'+ul_txt+'</a></li></ul>'
        }
        
        return d
    };
    this.get_li=function(id, id_value, txt){
        var d='<li role="presentation" id="'+id+'" class="padding-1 margin-1" style="text-align:left"><a href="##" style="padding:0px 0px 0px 5px;maring:2px" id="'+id_value+'">'+txt+'</a></li>'
        return d
    };
    this.get_li_checkbox=function(id,id_value , txt, directive, scope_attr){
        if (directive!=undefined && scope_attr!=undefined){
            var d='<li role="presentation" id="'+id+'" class="padding-1 margin-1" style="text-align:left"><span><input class="checkbox" type="checkbox" style="float:left;margin-right:5px" '+directive+' '+scope_attr+'><a href="##" id="'+id_value+'">'+txt+'</a></span</li>'
        }else{
            var d='<li role="presentation" id="'+id+'" class="padding-1 margin-1" style="text-align:left"><span><input class="checkbox" type="checkbox" style="float:left;margin-right:5px"><a href="##" id="'+id_value+'">'+txt+'</a></span</li>'
        }
        
        return d
    };
    this.isempty=function(a){
        for ( i in a){
            return false
        }
        return true
    };
    this.get_upload_html=function(txt){
        var d='<div id="uploadfile" class="form-group has-error has-feedback"><lable class="control-label" style="float:left">'+txt+':</lable><form method="post" enctype="multipart/form-data" class="uploadfile form-control" style="clear:both"><input type="file" name="file"></form><p class="help-block"></p></div>'
        return d
    };
})


var clientmodule=angular.module('clientmodule',['commmodule'])

clientmodule.service('factoryServerice',function($http,commservice){
    this.arguments_to_list=commservice.arguments_to_list
    this.get_callback=commservice.get_callback
    this.request_url=commservice.request_url
    this.commservice=commservice
})
clientmodule.controller('clientctrl',function($scope,factoryServerice){
    $scope.batchdeploy=function(){
        //涉及dom操作，在directive里修改调用
    }
    $scope.batchdelete=function(){
        //涉及dom操作，在directive里修改调用
    }
    $scope.batchupdate=function(){
        //涉及dom操作，在directive里修改调用
    }
    $scope.ischecked=false;
    $scope.alltrdata={};
    $scope.servicefn=factoryServerice
    $scope.tabledatakey=false
    $scope.tabledata=''
    $scope.client_search_dom=''
    $scope.commservice=$scope.servicefn.commservice
    $scope.client_s_fn=function(d,dom,des){
        if(d==-9){
            body_alert_evenet('err',"链接twisted失败")
            return false
        }
        var info=''
        if(des=="textarea_search"){
            $scope.tabledatakey=true
            $scope.tabledata=d
        }else if(des=="client_deploy"){
            info="部署"
        }else if(des=="server_init"){
            info="初始化"
        }else if(des=="client_delete"){
            info="停止客户端"
        }else if(des=="client_update"){
            info="客户端升级"
        }else if(des=="batch_deploy"){
            info="客户端批量部署"
        }else if(des=="batch_delete"){
            info="客户端批量停止"
        }else if(des=="batch_update"){
            info="客户端批量升级"
        }
        if(info!=""){
            body_alert_evenet('err',info+ "请求完成;这个操作可能需要等待一段时间,请关注")
        }
        
        if($scope.client_search_dom!=""&&info!=""){
            $scope.client_search_dom.trigger('click')
            return false
        }else{
            //
        }
    }
    $scope.client_e_fn=function(d,dom,des){
        body_alert_evenet('err',d)
        return false
    }
    
    
})
clientmodule.directive('ckeckallbox',function(){
    return {
        scope:{
            ischecked : '=',
            alltrdata : '='
        },
        restrict:'A',
        link:function(scope,element,attrs){
            var dm=element.parent().parent()
            var st=dm.find('#status').text().trim()
            var ip=dm.find('#ip').text().trim()
            var pr=dm.find('#pro').attr('name')
            var ag=dm.find('#agent').attr('name')

            dm.find('#client_deploy').unbind('click').click(function(){
                scope.$parent.servicefn.request_url('client_deploy','post',{ip:ip,pro:pr,agent:ag,status:st},scope.$parent.servicefn.get_callback(scope.$parent.client_s_fn,element,'client_deploy'),scope.$parent.servicefn.get_callback(scope.$parent.client_e_fn,element,'client_deploy'))
            })
            
            dm.find('#server_init').unbind('click').click(function(){
                scope.$parent.servicefn.request_url('server_init','post',{ip:ip,pro:pr,agent:ag,status:st},scope.$parent.servicefn.get_callback(scope.$parent.client_s_fn,element,'server_init'),scope.$parent.servicefn.get_callback(scope.$parent.client_e_fn,element,'server_init'))
            })
            
            dm.find('#client_delete').unbind('click').click(function(){
                scope.$parent.servicefn.request_url('client_online_opertion','post',{des:'client_delete',ip:ip,pro:pr,agent:ag,status:st},scope.$parent.servicefn.get_callback(scope.$parent.client_s_fn,element,'client_delete'),scope.$parent.servicefn.get_callback(scope.$parent.client_e_fn,element,'client_delete'))
            })
            dm.find('#client_update').unbind('click').click(function(){
                scope.$parent.servicefn.request_url('client_online_opertion','post',{des:'client_update',ip:ip,pro:pr,agent:ag,status:st},scope.$parent.servicefn.get_callback(scope.$parent.client_s_fn,element,'client_update'),scope.$parent.servicefn.get_callback(scope.$parent.client_e_fn,element,'client_update'))
            })
            
            element.bind('click',function(){
                if(attrs.id=="allckeck"){
                    if(attrs.ngChecked=='false'){
                        scope.ischecked=true
                    }else if(attrs.ngChecked=='true'){
                        scope.ischecked=false
                    }
                }else{
                    var st=dm.find('#status').text().trim()

                    if(st=="offline"){
                        if(scope.alltrdata['online']){
                            body_alert_evenet('err',"只能选择状态为 online 的项")
                            return false
                        }
                    }else if(st=="online"){
                        if(scope.alltrdata['offline']){
                            body_alert_evenet('err',"只能选择状态为 offline 的项")
                            return false
                        }
                    }else{
                        return false
                    }

                    if(attrs.ngChecked=='false'||attrs.ngChecked==false){
                        //修改属性时候  属性名进行驼峰转换 ngChecked -》 ng-checked
                        attrs.$set('ngChecked','true')
                    }else if(attrs.ngChecked=='true'||attrs.ngChecked==true){
                        attrs.$set('ngChecked','false')
                    }else{
                        body_alert_evenet('err',"获取选项异常")
                        return false
                    }
                }
                //同步数据到界面
                scope.$apply()
            })
            attrs.$observe('ngChecked',function(){ 
                if(attrs.ngChecked=='false'){
                    
                    element.prop('checked',false)
                    if(st==""){
                        return false
                    }
                    try{
                        if(scope.alltrdata[st][ip]){
                            delete scope.alltrdata[st][ip]
                        }
                        if(isempty(scope.alltrdata[st])){
                            delete scope.alltrdata[st]
                        }
                    }catch(e){
                        //
                    }

                }else{
                    element.prop('checked',true)
                    if(st==""){
                        return false
                    }
                    if(!scope.alltrdata[st]){
                        scope.alltrdata[st]={}
                    }
                    if(!scope.alltrdata[st][ip]){
                        scope.alltrdata[st][ip]={}
                    }
                    if(scope.alltrdata[st][ip]){
                        scope.alltrdata[st][ip]['pro']=pr
                        scope.alltrdata[st][ip]['agent']=ag
                    }else{
                        console.log(3333)
                    }

                }

            })
        }
    }
})
clientmodule.directive('batchb',function(){
    return {
        restrict:'A',
        scope:{
            deleteclick : '='
        },
        link:function(scope,element,attrs){
            element.click(function(){
                var des=element.attr('id')

                scope.deleteclick=function(des){
                    var server_info=scope.$parent.alltrdata
                    if(isempty(server_info)){
                        body_alert_evenet('err',"没有选择操作项")
                        return false
                    }
                    scope.$parent.servicefn.request_url('client_batch_handle','post',{data:server_info,des:des},scope.$parent.servicefn.get_callback(scope.$parent.client_s_fn,element,des),scope.$parent.servicefn.get_callback(scope.$parent.client_e_fn,element,des))
                }
                
               scope.deleteclick(des)
            })
        }
    }
})
clientmodule.directive('batchc',function(){
    return {
        restrict:'A',
        scope:{
            updateclick : '='
        },
        link:function(scope,element,attrs){
            element.click(function(){
                var des=element.attr('id')

                scope.updateclick=function(des){
                    var server_info=scope.$parent.alltrdata
                    if(isempty(server_info)){
                        body_alert_evenet('err',"没有选择操作项")
                        return false
                    }
                    scope.$parent.servicefn.request_url('client_batch_handle','post',{data:server_info,des:des},scope.$parent.servicefn.get_callback(scope.$parent.client_s_fn,element,des),scope.$parent.servicefn.get_callback(scope.$parent.client_e_fn,element,des))
                }
                
               scope.updateclick(des)
            })
        }
    }
})
clientmodule.directive('batcha',function(){
    return {
        restrict:'A',
        scope:{
            deployclick : '='
        },
        link:function(scope,element,attrs){
            element.click(function(){
                var des=element.attr('id')
                
                scope.deployclick=function(des){
                    var server_info=scope.$parent.alltrdata
                    if(isempty(server_info)){
                        body_alert_evenet('err',"没有选择操作项")
                        return false
                    }

                    scope.$parent.servicefn.request_url('client_batch_handle','post',{data:server_info,des:des},scope.$parent.servicefn.get_callback(scope.$parent.client_s_fn,element,des),scope.$parent.servicefn.get_callback(scope.$parent.client_e_fn,element,des))
                }
                scope.deployclick(des)
            })
        }
    }
})

clientmodule.directive('clientsearch',function(){
    return{
        scope:{
            tbdata:'='
        },
        restrict:'E',
        template:'<button type="button" class="search-server btn btn-default btn-xs" style="font-size:20px"><span class="glyphicon glyphicon-search" aria-hidden="true" style="height:30px;float:left" ></span></button>',
        replace:true,
        controller:function(factoryServerice){
            // controller 和link可以互换,link私有,controller用于指令间数据共享/暴露API
        },
        link:function(scope,element,attrs){
            var ip_dom=element.parent().parent().parent()
            var s_dom=ip_dom.parent()
            var s_f_dom=s_dom.parent()
            
            var txt_d=ip_dom.find('textarea')
            var batch_dom=s_dom.find('.client_batch_opertion')
            
            scope.$parent.commservice.textarea_add_event(txt_d)
            
            element.bind('click',function(){
                var state=s_dom.find('.client_online_filter select').val()
                var iplist=s_dom.find('.client_ip_filter textarea').val().trim().replace(/\n/g,',')
                if (state==0&&iplist==""){
                    return false
                }
                scope.$parent.client_search_dom=element
                scope.$parent.servicefn.request_url('client_online_filter','post',{state:state,iplist:iplist},scope.$parent.servicefn.get_callback(scope.$parent.client_s_fn,element,'textarea_search'),scope.$parent.servicefn.get_callback(scope.$parent.client_e_fn,element,'textarea_search'))
            })
        }
    }
})
clientmodule.directive('tbchange',function(){
    return {
        scope:{},
        restrict:'A',
        controller:function($compile,$scope,$element,$attrs){
            $attrs.$observe('tbchange',function(){
                if($attrs.tbchange=="false"){
                    return false
                }else{
                    //$compile 服务传入需要编译的html和对应的scope（需要替换的值所在的scope）
                    dom=$compile("<tbody>"+$scope.$parent.tabledata+"</tbody>")($scope.$parent)
                    $element.html(dom)
                    $scope.$parent.tabledatakey=false
                }
            })
        }
    }
})




var usergroupmodule=angular.module('usergroupmodule',['commmodule'])


usergroupmodule.controller('usergroupctrl',function($compile, $scope, commservice){
    $scope.tabpane=''
    $scope.commservice=commservice
    $scope.tablechangekey=false
    $scope.tablechangedata=''
    $scope.group_change_id=false
    $scope.member_change_id=false
    $scope.leftcheckboxdata={}
    $scope.rightcheckboxdata={}
    $scope.changetype=''
    $scope.target_obj=''
    $scope.leftdata=[]
    $scope.lefthistory=[]

    
    
    
    $scope.addleftinfo=function(leftdom,rightdom,des){
        var ddm=leftdom.find(' ul  ul ')
        if(isempty($scope.rightcheckboxdata)){
            return false
        }

        for(i in $scope.rightcheckboxdata){
            var dt=""
            if(ddm.find('#'+i).length>0){
                ddm.find('#'+i).remove
            }

            dt=$scope.commservice.get_li_checkbox('user', $scope.rightcheckboxdata[i].find('a').attr('id'),$scope.rightcheckboxdata[i].find('a').text().trim(), 'leftcheckbox', 'leftcheckboxdata="leftcheckboxdata"')

            ddm.append($compile(dt)($scope))
            $scope.rightcheckboxdata[i].find('.checkbox').prop({'checked':false, 'disabled':true})
            $scope.leftdata.push(i)
        }
        
        ddm.find('li').css('padding-left','45px')
        ddm.find('.checkbox:checked').prop('checked',false)
        $scope.rightcheckboxdata={}
    }
    $scope.delleftinfo=function(leftdom,rightdom,des){
        if(des=="group_change"){
            var ddm=rightdom.find(' ul  ul ')
            
        }else if(des=="member_change"){
            
        }

        if(isempty($scope.leftcheckboxdata)){
            return false
        }

        for(i in $scope.leftcheckboxdata){
            var dt=""
            rightdom.find('a[id="'+i+'"]').prev().prop('disabled',false)         
            $scope.leftcheckboxdata[i].remove()
            $scope.leftdata.splice($scope.leftdata.indexOf(i), 1)
        }
        $scope.leftcheckboxdata={}
    }
    
    
    $scope.fn_sucuss=function(d,dom,des){
        if(d==-1){
            mod_alert_evenet('err','参数错误')
            return false
        }
        if(des=="user_add"||des=="group_add"||des=="cdn_add"){
            if(d==1&&des!="cdn_add"){
                mod_alert_evenet('err','当前用户已经存在')
                return false
            }else if(des=="cdn_add"&&d==-3){
                mod_alert_evenet('err','当前名称已经存在')
                return false
            }else if(d=="success"){
                dom.find('.modal-header button').trigger('click')
                return false
            }
        }else if(des=="user_search"||des=="privilege_search"||des=="zone_history_search"){
            $scope.tablechangekey=true
            $scope.tablechangedata=d
        }else if(des=="user_del"||des=="group_del"){
            if(d=="success"){
                dom.parent().parent().remove()
            }
        }else if(des=="group_change"||des=="member_change"||des=="privilege_change"||des=="cdn_member_change"){
            if(des=="member_change"){
                var title="成员变更"
                var id=$scope.member_change_id
            }else if(des=="group_change"){
                var title="组变更"
                var id=$scope.group_change_id
            }else if(des=="cdn_member_change"){
                if($scope.tabpane=="game_login_tool"){
                    var title="接口服务器成员变更"
                }else{
                    var title="CDN服务器成员变更"
                }
                
                var id=$scope.group_change_id
            }else if(des=="privilege_change"){
                var title="权限变更"
                var id=$scope.group_change_id
            }else{
                console.log('change type err.')
                return false
            }

            var label=id+"-label"
            var html=$compile($scope.commservice.get_modal(id, label, title, 'usergroupchangeokbuttion'))($scope)

            var tdm=dom.next().html(html)
            var mod_d=tdm.find('#'+id)
            if(des=="member_change"){
                var left_id=id+'_pane_left'
                var left_id_des='成员'
                var left_id_ul_id=left_id+"_owner"
                var left_id_ul_id_des='组成员信息'
                var left_id_level='info'
                var mod_id=id+'_pane_mod'
                var mod_id_des='操作'
                var mod_id_level='info'
                var right_id=id+'_pane_right'
                var right_id_ul_id=right_id+"_owner"
                var right_id_ul_id_des='用户信息列表'
                var right_id_des='用户列表'
                var right_id_level='info'
            }else if(des=="group_change"){
                var left_id=id+'_pane_left'
                var left_id_des='所属组'
                var left_id_ul_id=left_id+"_owner"
                var left_id_ul_id_des='所属组信息'
                var left_id_level='info'
                var mod_id=id+'_pane_mod'
                var mod_id_des='操作'
                var mod_id_level='info'
                var right_id=id+'_pane_right'
                var right_id_ul_id=right_id+"_owner"
                var right_id_ul_id_des='组信息列表'
                var right_id_des='组列表'
                var right_id_level='info'

            }else if(des=="privilege_change"){
                var left_id=id+'_pane_left'
                var left_id_des='所属组'
                var left_id_ul_id=left_id+"_owner"
                var left_id_ul_id_des='所属组信息'
                var left_id_level='info'
                var mod_id=id+'_pane_mod'
                var mod_id_des='操作'
                var mod_id_level='info'
                var right_id=id+'_pane_right'
                var right_id_ul_id=right_id+"_owner"
                var right_id_ul_id_des='权限信息列表'
                var right_id_des='权限列表'
                var right_id_level='info'
            }else if(des=="cdn_member_change"){
                var left_id=id+'_pane_left'
                var left_id_des='服务器成员'
                var left_id_ul_id=left_id+"_owner"
                var left_id_ul_id_des='成员信息'
                var left_id_level='info'
                var mod_id=id+'_pane_mod'
                var mod_id_des='操作'
                var mod_id_level='info'
                var right_id=id+'_pane_right'
                var right_id_ul_id=right_id+"_owner"
                var right_id_ul_id_des='服务器信息'
                var right_id_des='服务器信息列表'
                var right_id_level='info'
            }

            mod_d.on('show.bs.modal',function(){
                    $scope.leftdata=[]
                    var left=$scope.commservice.get_tabpanel(left_id, left_id_des, left_id_level)
                    var mod=$scope.commservice.get_tabpanel(mod_id, mod_id_des, mod_id_level)
                    var right=$scope.commservice.get_tabpanel(right_id, right_id_des, right_id_level)
                    var opertion_d=$compile('<button id="'+id+'" type="button" class="btn btn-primary  col-md-12" leftcheckboxdata="leftcheckboxdata"  lefttoright><span class="glyphicon  glyphicon-arrow-right  col-md-12"></span></button><button id="'+id+'" type="button" class="btn btn-info  col-md-12" rightcheckboxdata="rightcheckboxdata" righttoleft><span class="glyphicon  glyphicon-arrow-left  col-md-12"></span></button>')($scope)
                    var l_dm=mod_d.find('.modal-body').append(left).find('#'+left_id).addClass('col-md-5 padding-1').css({
                        'float':'left',
                        'margin-right':'10px'
                    }).find('.panel-body').html($scope.commservice.get_ul(left_id_ul_id, left_id_ul_id_des)).find('#'+left_id_ul_id).append($scope.commservice.get_ul()).find(' > ul').append(function(){
                        var dt=''
                        if(des=="member_change"){
                            for(n in d['member_list']){
                                if(d['member_list'][n]['member']==null){
                                    continue
                                }
                                var m_list=d['member_list'][n]['member'].split(',')
                                for(i in  m_list){
                                    if(m_list[i]==""){
                                        continue
                                    }
                                    dt+=$scope.commservice.get_li_checkbox('name', m_list[i], m_list[i], 'leftcheckbox', 'leftcheckboxdata="leftcheckboxdata"')
                                    $scope.leftdata.push(m_list[i])
                                }
                            }
                            
                        }else if(des=="group_change"){
                            for(n in d['owner_group_list']){
                                for(i in d['group_list']){
                                    var d_des=undefined
                                    if(d['group_list'][i]['name']==d['owner_group_list'][n]['name']){
                                        var d_des=d['group_list'][i]['des']
                                        break;
                                    }
                                }
                                dt+=$scope.commservice.get_li_checkbox('name', d['owner_group_list'][n]['name'], d_des, 'leftcheckbox', 'leftcheckboxdata="leftcheckboxdata"')
                                $scope.leftdata.push(d['owner_group_list'][n]['name'])
                            }
                        }else if(des=="privilege_change"){
                            for(n in d['owner_privilege_list']){
                                var privi_list=d['owner_privilege_list'][n]['privi_list']
                                if(privi_list==null){
                                    continue
                                }
                                privi_list=privi_list.split(',')
                                var d_des=undefined
                                var name=undefined
                                for(i in privi_list){
                                    var c_name=privi_list[i]
                                    if(c_name==""){
                                       continue 
                                    }
                                    if(c_name in d['privilege_list']){
                                        var d_des=d['privilege_list'][c_name]['des']
                                        var name=d['privilege_list'][c_name]['name']
                                    }
                                    if(name==undefined){
                                        continue
                                    }
                                    dt+=$scope.commservice.get_li_checkbox('name', name, d_des, 'leftcheckbox', 'leftcheckboxdata="leftcheckboxdata"')
                                    $scope.leftdata.push(name)
                                }
                            }
                        }else if(des=="cdn_member_change"){
                            if(d['cdn_member']==null){
                                return false
                            }
                            for(i in d['cdn_member']){
                                if(d['cdn_member'][i]==""){
                                    continue
                                }
                                dt+=$scope.commservice.get_li_checkbox('name', d['cdn_member'][i], d['cdn_member'][i], 'leftcheckbox', 'leftcheckboxdata="leftcheckboxdata"')
                                $scope.leftdata.push(d['cdn_member'][i])
                            }
                        }
                        
                        $scope.lefthistory=$scope.leftdata.concat()
                        return $compile(dt)($scope)
                    })
                    l_dm.find('li').css('padding-left','45px')
                    $scope.changetype=des
                    var mdm=mod_d.find('.modal-body').append(mod).find('#'+mod_id).addClass('col-md-1 padding-1').css({
                        'float':'left',
                        'margin-right':'10px'
                    }).find('.panel-body').html(opertion_d)

                    var height=mdm.height()
                    mdm.find('button:eq(0)').css('margin', height / 2 - 50 +'px 0px 10px')
                    var r_dm=mod_d.find('.modal-body').append(right).find('#'+right_id).addClass('col-md-5 padding-1').css('float','left').find('.panel-body').html($scope.commservice.get_ul(right_id_ul_id, right_id_ul_id_des)).find('#'+right_id_ul_id).append($scope.commservice.get_ul()).find(' > ul').append(function(){
                        var dt=''
                        
                        if(des=="member_change"){
                            for(n in d['user_list']){
                                for(nn in d['member_list']){
                                    if(d['member_list'][nn]['member']==null){
                                        continue
                                    }
                                    var m_list=d['member_list'][nn]['member'].split(',')                             
                                    for(i in  m_list){
                                        if(m_list[i]==""){
                                            continue
                                        }
                                        var isdisabled=''
                                        if(d['user_list'][n]['user']===m_list[i]){
                                            var isdisabled='disabled="true"'
                                            break
                                        }
                                    }
                                }

                                dt+=$scope.commservice.get_li_checkbox('user', d['user_list'][n]['user'],d['user_list'][n]['user'], 'rightcheckbox', 'rightcheckboxdata="rightcheckboxdata"'+isdisabled+'')
                            }
                        }else if(des=="group_change"){
                            for(n in d['group_list']){
                                if($scope.leftdata.indexOf(d['group_list'][n]['name'])!=-1){
                                    var isdisabled='disabled="true"'
                                }else{
                                    var isdisabled=''
                                }
                                dt+=$scope.commservice.get_li_checkbox('name',  d['group_list'][n]['name'],d['group_list'][n]['des'], 'rightcheckbox', 'rightcheckboxdata="rightcheckboxdata"'+isdisabled+'')
                            }
                        }else if(des=="privilege_change"){
                            for(n in d['privilege_list']){
                                if($scope.leftdata.indexOf(n)!=-1){
                                    var isdisabled='disabled="true"'
                                }else{
                                    var isdisabled=''
                                }
                                dt+=$scope.commservice.get_li_checkbox('name',  d['privilege_list'][n]['name'], d['privilege_list'][n]['des'], 'rightcheckbox', 'rightcheckboxdata="rightcheckboxdata"'+isdisabled+'')
                            }
                        }else if(des=="cdn_member_change"){
                            if(d['asset_list']==null){
                                return false
                            }
                            for(i in d['asset_list']){
                                if($scope.leftdata.indexOf(d['asset_list'][i])!=-1){
                                    var isdisabled='disabled="true"'
                                }else{
                                    var isdisabled=''
                                }
                                dt+=$scope.commservice.get_li_checkbox('name', d['asset_list'][i], d['asset_list'][i], 'rightcheckbox', 'rightcheckboxdata="rightcheckboxdata"'+isdisabled+'')
                            }
                        }

                        return $compile(dt)($scope)
                    })
                    r_dm.find('li').css('padding-left','45px')
            })


            mod_d.find('.modal-footer').css('clear','both')
            mod_d.modal('show')
        }
    }
    $scope.fn_err=function(dom,des){
        if(des=="user_add"||des=="group_add"){
            
        }else{}
    }
})

usergroupmodule.directive('tablechange',function(){
    return {
        scope:{},
        restrict:'A',
        controller:function($compile, $scope, $element, $attrs){
            $attrs.$observe('tablechange',function(){
                if($attrs.tablechange==false){
                    return false
                }else{
                    var dom=$compile("<tbody>"+$scope.$parent.tablechangedata+"</tbody>")($scope.$parent)
                    $element.html(dom)
                    $scope.$parent.tablechangekey=false
                }
            })
        }
    }
})

usergroupmodule.directive('tabpaneswitch',function(){
    return {
        restrict:'A',
        scope:{
            tabpanv:"="
        },
        link:function(scope,element,attrs){
            if(element.parent().is('li')&&element.parent().hasClass('active')){
                scope.tabpanv=attrs.href.split('#')[1]
            }
            element.unbind('click').click(function(){
                scope.tabpanv=attrs.href.split('#')[1]
                scope.$apply()
            })
        }
    }
})

usergroupmodule.directive('groupopertion', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var add_d=element.find(element.find('.add_group button').attr('data-target'))
            add_d.on('show.bs.modal',function(){
                var i_d=add_d.find('.modal-body')
                var d=scope.$parent.commservice.get_input('组名','输入组名;如XXX','groupname')+scope.$parent.commservice.get_input('描述','输入添加的组描述;如运维部','des')
                i_d.html(d)
                add_d.find('.modal-footer button:eq(1)').click(function(){
                    var name=i_d.find('#groupname input').val()
                    var des=i_d.find('#des input').val()
                    if(name==""||des==""){
                        mod_alert_evenet('err',"请填写完整")
                        return false
                    }
                    scope.$parent.commservice.request_url('group_add','post',{groupname:name,des:des},scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'group_add'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'group_add'))
                })
            })
        }
    }
})

usergroupmodule.directive('usergroupfilter',function(){
    return {
        restrict:'AE',
        scope:{},
        link:function(scope,element,attrs){
            var txt_d=element.find('textarea')
            var mod_d=element.find(element.find('#add_default_info button').attr('data-target'))
            var search_d=element.find('.user_name_filter button')
            var group_d=element.find('.user_group_filter select')
            
            
            scope.$parent.commservice.textarea_add_event(txt_d)
            mod_d.on('show.bs.modal',function(){
                var i_d=mod_d.find('.modal-body')
                var d=scope.$parent.commservice.get_input('用户名','输入用户名/RTX;如XXX','username')+scope.$parent.commservice.get_input('描述','输入添加的用户描述;如运维部XXX','des')
                i_d.html(d)
                mod_d.find('.modal-footer button:eq(1)').click(function(){
                    var name=i_d.find('#username input').val()
                    var des=i_d.find('#des input').val()
                    if(name==""||des==""){
                        mod_alert_evenet('err',"请填写完整")
                        return false
                    }
                    scope.$parent.commservice.request_url('user_add','post',{username:name,des:des},scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'user_add'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'user_add'))
                })        
            })
            search_d.click(function(){
                var id=search_d.attr('id')
                if(id==undefined||id==""){
                    var group=group_d.val()
                    var user_list=txt_d.val().replace(/\n/g,',')

                    if(group==0&&user_list==""){
                        return false
                    }
                    scope.$parent.commservice.request_url("user_search",'post',{group:group,user_list:user_list},scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,"user_search"),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,"user_search"))
                }else{
                    var type=element.find('.zone_op_tp select').val()
                    var stat=element.find('.zone_op_st select').val()
                    var time=element.find('.zone_op_tm input').val()
                    var site=element.find('textarea').val().trim().replace(/\n/g,',')
                    if(type==0&&stat==0&&time==""&&site==""){
                        return false
                    }
                    
                    scope.$parent.commservice.request_url("zone_history_search",'post',{type:type,status:stat,time:time,site:site},scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,"zone_history_search"),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,"zone_history_search"))        
                }
 
            })
        }
    }
})


usergroupmodule.directive('cndmanger',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope,element,attrs){
            var deld=element.find('#delete')
            var memd=element.find('#cdn_member')
            var chgd=element.find('#cdn_task_trigger')
            var nm=element.find('#name').text().trim()

            deld.click(function(){
                if(scope.$parent.tabpane=="game_login_tool"){
                    var dld="确定删除接口 "+ nm+" 记录？"
                }else{
                    var dld="确定删除CDN "+ nm+" 记录？"
                }
                if(confirm(dld)){
                    scope.$parent.commservice.request_url('cdn_del','post', {cdnname:nm,type:scope.$parent.tabpane},function(d){
                        if(d="success"){
                            element.remove()
                        }else{
                            body_alert_evenet('err',"删除失败")
                            return false
                        }
                    })
                }
            })
            
            memd.click(function(){
                scope.$parent.group_change_id=nm.replace(/\./g,'_')
                scope.$parent.target_obj=nm
                scope.$parent.commservice.request_url('cdn_member_change', 'post',{cdnname:nm,type:scope.$parent.tabpane}, scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,memd,'cdn_member_change'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,memd,'cdn_member_change'))
            })
            chgd.click(function(){
                if(chgd.prop('disabled')==true){
                    return false
                }
                if(scope.$parent.tabpane=="game_login_tool"){
                    var trd="确定触发接口 "+ nm+" 更新？"
                }else{
                    var trd="确定触发CDN "+ nm+" 更新？"
                }
                if(confirm(trd)){
                    scope.$parent.commservice.request_url('cdn_task_trigger','post', {cdnname:nm,type:scope.$parent.tabpane},function(d){
                        if(d="success"){
                            chgd.text("执行中...")
                            chgd.prop('disabled',true)
                        }else{
                            body_alert_evenet('err',"触发失败")
                            return false
                        }
                    })
                }
            })
        }
    }
    
})

usergroupmodule.directive('toolupload',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope,element,attrs){ 
            var mod_da=element.parent().find(element.attr('data-target'))
            var tdm=element.parent().parent().parent()
            var cdnname=tdm.find('#name').text().trim()
            
            mod_da.on('show.bs.modal',function(){
                if(scope.$parent.tabpane=="game_login_tool"){
                    var lable="请选择代理接口工具执行文件"
                    var tn='game_login_tool'
                }else{
                    var lable="请选择cnd工具执行文件"
                    var tn='cdn_tool'
                }
                mod_da.find('.modal-body').html(scope.$parent.commservice.get_upload_html(lable))
                upload_input_color_change(mod_da.find('.uploadfile input'))
                mod_da.find('.modal-footer button:eq(1)').click(function(){
                    var f=mod_da.find('.modal-body .uploadfile input').val()
                    var fn=f.split('\\')
                    fn=fn[fn.length-1]

                    
                    if(f!=""){
                        fileupload(mod_da.find('#uploadfile form'),{k:'third_party_tools',v:tn+"/"+cdnname},function(){
                            scope.$parent.commservice.request_url('add_cdn_task','post', {filename:f,tool:tn,cdnname:cdnname,type:scope.$parent.tabpane},function(d){
                                if(d==-2){
                                    body_alert_evenet('err', "任务文件上传成功,保存失败")
                                }
                                mod_da.find('.modal-footer button:eq(0)').trigger('click')
                                tdm.find('#file_path').text('./tools//'+tn+'/'+cdnname+'/'+fn+'')
                            })
                        })
                    }
                })
            })
        }
    }
})
usergroupmodule.directive('cdnfilter',function(){
    return {
        restrict:'AE',
        scope:{},
        link:function(scope,element,attrs){
            var txt_d=element.find('textarea')
            var mod_d=element.find(element.find('.add_cdn button').attr('data-target'))

            mod_d.on('show.bs.modal',function(){
                scope.$parent.commservice.request_url('cnd_add_before','post', {},function(d){
                    var i_d=mod_d.find('.modal-body')
                    if(scope.$parent.tabpane=="game_login_tool"){
                        var dt=scope.$parent.commservice.get_input('接口名称','输入接口名称','cdn_name')+scope.$parent.commservice.get_input('所属业务','选择接口所属业务','pro_owner')+scope.$parent.commservice.get_input('所属代理','选择接口所属的代理','agent_owner')
                        var s='<option value="0">选择接口所属业务</option>'
                        var ss='<option value="0">选择接口所属的代理</option>'
                    }else{
                        var dt=scope.$parent.commservice.get_input('cdn域名','输入cdn域名,xx.xx.xx','cdn_name')+scope.$parent.commservice.get_input('所属业务','选择cdn域名的所属业务','pro_owner')+scope.$parent.commservice.get_input('所属代理','选择cdn域名所属的代理','agent_owner')
                        var s='<option value="0">选择cdn域名的所属业务</option>'
                        var ss='<option value="0">选择cdn域名所属的代理</option>'
                    }
                
                    
                    i_d.html(dt)
                    mod_d.find('#pro_owner input').hide()
                    mod_d.find('#agent_owner input').hide()
                    mod_d.find('#pro_owner').append("<select class='form-control'></select>")
                    mod_d.find('#agent_owner').append("<select class='form-control'></select>")

                     
                    for(i in d){
                        s+="<option value='"+i+"'>"+d[i]['des']+"</option>"
                        for(ii in d[i]){
                            if(ii == "des"){
                                continue
                            }
                            ss+="<option pro='"+i+"' asset='"+d[i][ii]['asset']+"' value='"+ii+"'>"+d[i][ii]['des']+"</option>"
                        }
                    }
                    
                    mod_d.find('#pro_owner select').append(s)
                    mod_d.find('#pro_owner select').change(function(){
                        var pro_owner=i_d.find('#pro_owner select').val()
                        console.log(pro_owner)
                        console.log(mod_d.find('#agent_owner select option[pro="'+pro_owner+'"]').length)
                        if(pro_owner==0){
                            mod_d.find('#agent_owner select option').show() 
                        }else{
                            mod_d.find('#agent_owner select option:gt(0)').hide()
                            mod_d.find('#agent_owner select option[pro="'+pro_owner+'"]').show()
                        }
                    })
                    mod_d.find('#agent_owner select').append(ss)

                    mod_d.find('.modal-footer button:eq(1)').click(function(){
                        var name=i_d.find('#cdn_name input').val()
                        var pro_owner=i_d.find('#pro_owner select').val()
                        var agent_owner=i_d.find('#agent_owner select').val()
                        var asset=i_d.find('#agent_owner select option[value="'+agent_owner+'"]').attr('asset')
                        if(name==""||pro_owner==0||agent_owner==0){
                            mod_alert_evenet('err',"请填写完整")
                            return false
                        }

                        scope.$parent.commservice.request_url('cdn_add','post',{cdnname:name,pro:pro_owner,agent:agent_owner,asset:asset,type:scope.$parent.tabpane},scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'cdn_add'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'cdn_add'))
                    }) 
                })
       
            })
        }
    }
})

usergroupmodule.directive('dotabpanswitch',function(){
    return {
        restrict:'A',
        scope:{
            tabpane:'='
        },
        link:function(scope,element,attrs){
            attrs.$observe('tabpanval',function(){
                scope.$parent.commservice.tab_pane_switch(element, scope.tabpane, attrs.id)
            })
        }
    }
})

usergroupmodule.directive('userdel', function(){
    return{
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.unbind('click').click(function(){
                var tr_d=element.parent().parent()
                var user=tr_d.find('#user').text().trim()
                scope.$parent.commservice.alert_confirm("是否删除用户 "+user+" 并移除加入的组?", function(){
                    scope.$parent.commservice.request_url('user_del', 'post',{user:user}, scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'user_del'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'user_del'))
                }, function(){
                    //
                })
            })
        }
    }
})
usergroupmodule.directive('groupchange', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.unbind('click').click(function(){
                var tr_d=element.parent().parent()
                var user=tr_d.find(' > #user').text().trim()
                scope.$parent.target_obj=user
                scope.$parent.group_change_id='user_'+user
                scope.$parent.commservice.request_url('group_change', 'post',{user:user}, scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'group_change'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'group_change'))
            })
        }
    }
})

usergroupmodule.directive('groupdel', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.unbind('click').click(function(){
                var tr_d=element.parent().parent()
                var group=tr_d.find('.group').text().trim()
                scope.$parent.commservice.alert_confirm("是否删除组 "+group+" 并移除加入的成员权限信息?", function(){
                    scope.$parent.commservice.request_url('group_del', 'post',{group:group}, scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'group_del'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'group_del'))
                }, function(){
                    //
                })
            })
        }
    }
})
usergroupmodule.directive('memberchange', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.unbind('click').click(function(){
                var tr_d=element.parent().parent()
                var group=tr_d.find('.group').text().trim()
                scope.$parent.target_obj=group
                
                scope.$parent.member_change_id='group_'+group
                scope.$parent.commservice.request_url('member_change', 'post',{group:group}, scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'member_change'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'member_change'))
            })
        }
    }
})

usergroupmodule.directive('lefttoright',function(){
    return {
        scope:{
            leftcheckboxdata:"="
        },
        restrict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                if(isempty(scope.$parent.leftcheckboxdata)){
                    return  false
                }
                var id=element.attr('id')
                var leftdom=element.parent().parent().parent().find('#'+id+"_pane_left")
                var rightdom=element.parent().parent().parent().find('#'+id+"_pane_right")
                var des=scope.$parent.changetype
                scope.$parent.delleftinfo(leftdom, rightdom, des)
            })
        }
    }
})

usergroupmodule.directive('infolistdom', function(){
    return {
        scope:false,
        restrict:'A',
        controller:function($scope){
            console.log('&&&&&')
            this.addinfo=function(){
                console.log('addinfo')
            };
            this.delinfo=function(){
                console.log('delinfo')
            };
            console.log($scope)
        }
    }
})
usergroupmodule.directive('infolistdomchildren', function(){
    return {
        scope:false,
        restrict:'A',
        require:'^infolistdom',
        controller:function($scope){
            this.addinfo=function(){
                console.log('addinfo')
            };
            this.delinfo=function(){
                console.log('delinfo')
            };
        }
    }
})

usergroupmodule.directive('righttoleft',function(){
    return {
        scope:{
            rightcheckboxdata:"="
        },
        restrict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                if(isempty(scope.$parent.rightcheckboxdata)){
                    return  false
                }
                var id=element.attr('id')
                var leftdom=element.parent().parent().parent().find('#'+id+"_pane_left")
                var rightdom=element.parent().parent().parent().find('#'+id+"_pane_right")
                var des=scope.$parent.changetype
                scope.$parent.addleftinfo(leftdom, rightdom, des)
            })
        }
    }
})

usergroupmodule.directive('leftcheckbox', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                var v=element.next().attr('id')
                var li_dm=element.parent().parent()
                if(element.prop('checked')==true){
                    scope.$parent.leftcheckboxdata[v]=li_dm
                }else{
                    delete scope.$parent.leftcheckboxdata[v]
                }
            })
        }
    }
})
usergroupmodule.directive('rightcheckbox', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                var v=element.next().attr('id')
                var li_dm=element.parent().parent()
                if(element.prop('checked')==true){
                    scope.$parent.rightcheckboxdata[v]=li_dm
                }else{
                    delete scope.$parent.rightcheckboxdata[v]
                }
            })
        }
    }
})

usergroupmodule.directive('usergroupchangeokbuttion', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                if(scope.$parent.changetype==false||scope.$parent.changetype==undefined){
                    mod_alert_evenet('err',"changetype err.")
                    return false
                }

                if(scope.$parent.lefthistory.length==scope.$parent.leftdata.length){
                    var haschanged=false
                    for(i in scope.$parent.leftdata){
                        if(scope.$parent.lefthistory.indexOf(scope.$parent.leftdata[i])==-1){
                            haschanged=true
                            break
                        }
                    }
                    if(!haschanged){
                        element.prop('disabled',false)
                        element.prev().trigger('click')
                        return false
                    }
                }else if(scope.$parent.changetype=="group_change"&&scope.$parent.leftdata.length<scope.$parent.lefthistory.length){
                    var leftnewdata=scope.$parent.leftdata.concat()
                    for(i in scope.$parent.leftdata){
                        var nm=scope.$parent.lefthistory.indexOf(scope.$parent.leftdata[i])
                        if(nm!=-1){
                            scope.$parent.lefthistory.splice(nm, 1)
                            leftnewdata.splice(leftnewdata.indexOf(scope.$parent.leftdata[i]), 1)
                        }
                    }

                    scope.$parent.leftdata=scope.$parent.lefthistory.concat(leftnewdata)

                }else if(scope.$parent.changetype=="group_change"&&scope.$parent.leftdata.length>scope.$parent.lefthistory.length){
                    for(i in scope.$parent.lefthistory){
                        var nm=scope.$parent.leftdata.indexOf(scope.$parent.lefthistory[i])
                        if( nm != -1){
                            scope.$parent.leftdata.splice(nm,1)
                        }
                    }
                }
                if(scope.$parent.leftdata.length==0){
                    return false
                }

                element.prop('disabled',true)
                scope.$parent.commservice.request_url(scope.$parent.changetype+"_commit", 'post', {changedata:scope.$parent.leftdata, target_obj:scope.$parent.target_obj,type:scope.$parent.tabpane},function(){
                    element.prev().trigger('click')
                    element.prop('disabled',false)
                }, function(){
                    mod_alert_evenet('err','变更失败')
                    element.prop('disabled',false)
                })
            })
        }
    }
})

usergroupmodule.directive('privilegefilter', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var search_d=element.find('.user_name_filter button')
            var group_d=element.find('.user_group_filter select')
            search_d.click(function(){
                var group=group_d.val()
                if(group==0){
                    return false
                }
                scope.$parent.commservice.request_url('privilege_search','post',{group:group},scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'privilege_search'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'privilege_search'))
            })
        }
    }
})

usergroupmodule.directive('privilegechange', function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.unbind('click').click(function(){
                var tr_d=element.parent().parent()
                var group=tr_d.find(' > #name').text().trim()
                scope.$parent.target_obj=group
                scope.$parent.group_change_id='privilege_'+group
                scope.$parent.commservice.request_url('privilege_change', 'post',{group:group}, scope.$parent.commservice.get_callback(scope.$parent.fn_sucuss,element,'privilege_change'),scope.$parent.commservice.get_callback(scope.$parent.fn_err,element,'privilege_change'))
            })
        }
    }
})


