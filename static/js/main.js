var mainmodule=angular.module('mainmodule',['commmodule'])
mainmodule.controller('mainctrl', function($scope, commservice, $compile){
    //避免在directive中引用
    $scope.commservice=commservice
    $scope.compile=$compile
    $scope.input_check=function(){
        commservice.field_input_check(angular.element(event.target).parent())
    };

    $scope.preproset=function(a){}
    $scope.stset=function(){}
    $scope.idchange=function(tid){
        for(i in $scope.task.taskcreate.relevance.relevancelist){
            if(tid==undefined){
                $scope.task.taskcreate.relevance.relevancelist[i]['id']=Number(i)+1
            }else if($scope.task.taskcreate.relevance.relevancelist[i]['id']>tid){
                $scope.task.taskcreate.relevance.relevancelist[i]['id']-=1
            }
        }
    };
    $scope.relevancebreadcrumbset=function(dom, selector){
        if(selector==undefined||selector==''){
            var selector='taskrelevance'
        }else{
            var selector=selector
        }
        dom.find('div#'+selector+' #relevanceapp,div#'+selector+' #relevancetype,div#'+selector+' .secondary.menu a').click(function(){
            var tdmm=angular.element(event.target)
            var name=tdmm.attr('name')
            var des=tdmm.text().trim()
            var id=tdmm.attr('id')
            var key=id

            if(id=="relevanceapp"){
                if(selector=="servergroup"){
                    key="relevanceline"
                    delete $scope.breadcrumblist['relevanceproduct']
                    delete $scope.breadcrumblist['relevanceappa']
                }else if(selector=="taskrelevance"){
                    $scope.breadcrumblist={}
                }
            }else if(id=="relevancetype"){
                var pkey='relevanceapp'
                var pn=tdmm.parent().parent().prev().attr('name')
                var pndes=tdmm.parent().parent().prev().text().trim()
                if(selector=="servergroup"){
                    key="relevanceproduct"
                    pkey='relevanceline'
                    delete $scope.breadcrumblist['relevanceappa']
                }else{
                    delete $scope.breadcrumblist['relevance']
                    delete $scope.breadcrumblist['relevanceline']
                    delete $scope.breadcrumblist['relevanceproduct']
                    delete $scope.breadcrumblist['relevanceapp']
                }
                $scope.breadcrumblist[pkey]={'key':pn,'des':pndes}
            }else if(id=="relevance"){
                var ppkey='relevanceapp'
                var pkey='relevancetype'
                var pn=tdmm.parent().parent().prev().attr('name')
                var pndes=tdmm.parent().parent().prev().text().trim()
                var ppn=tdmm.parent().parent().parent().parent().prev().attr('name')
                var ppndes=tdmm.parent().parent().parent().parent().prev().text().trim()

                if(selector=="servergroup"){
                    key="relevanceappa"
                    ppkey='relevanceline'
                    pkey='relevanceproduct'
                }else{
                    $scope.breadcrumblist={}
                }

                $scope.breadcrumblist[ppkey]={'key':ppn,'des':ppndes}
                $scope.breadcrumblist[pkey]={'key':pn,'des':pndes}
            }
            delete $scope.breadcrumblist[key]
            $scope.$apply($scope.breadcrumblist)
            $scope.breadcrumblist[key]={'key':name,'des':des}
            $scope.$apply($scope.breadcrumblist)
        })
    }
    $scope.recover=function(){
        var ttid=$scope.task.taskcreate.relevance.preproid
        var ttlist=$scope.task.taskcreate.relevance.preprolist
        var tl=''

        for(i in ttlist){
            if(i==0){
                tl=$scope.task.taskcreate.relevance.relevancelist[i]
                tl['prepro']='no'
                delete tl['preprotype']
            }
            //始终删除第一个
            $scope.task.taskcreate.relevance.relevancelist.splice(0, 1)
        }
        $scope.task.taskcreate.relevance.preprolist=[]
        $scope.task.taskcreate.relevance.prepro='no'
        $scope.task.taskcreate.relevance.relevancelist.splice(ttid, 0 , tl)
    }
    $scope.searchinfo=function(id, name, pageid){
        var check=$scope.asset.assetmanager
        var d={}
        var url=id+'_searchinfo'
        var dom=''
        var fdm=''
        
        if(id=="assetfilter"){
            dom=angular.element('button#assetfilter[name="'+name+'"]')
            var other_key=dom.parent().parent().parent().find('div.other .text').text().trim()
            if(!other_key.match(/:/)){
                other_key=""
            }
            var adt=$scope.asset.assetmanager.accountfilter
            if(check.isfirst(name)){
                url=name+'_searchinfo'
                d['line']=adt.tatisticslinevalue
                d['product']=adt.tatisticsproductvalue
                d['app']=adt.tatisticsappvalue
                d['idc']=adt.tatisticsidcvalue
                d['other_key']=other_key
                d['iplist']=adt.tatisticsiplist
            }else if(check.issecond(name)){
                url=name+'_searchinfo'
                d['line']=adt.historylinevalue
                d['product']=adt.historyproductvalue
                d['app']=adt.historyappvalue
                d['idc']=adt.historyidcvalue
                d['other_key']=other_key
                d['iplist']=adt.historyiplist
            }else if(check.isthird(name)){
                if(name=="serverinit"||name=="loginmanager"){
                    url=name+'_searchinfo'
                    var initstatus=angular.element('.initype').val()
                    d['initype']=initstatus
                }
                d['line']=adt.linevalue
                d['product']=adt.productvalue
                d['app']=adt.appvalue
                d['idc']=adt.idcvalue
                d['other_key']=other_key
                d['iplist']=adt.iplist
            }

            if(pageid!=undefined){
                d['pageid']=pageid
            }
            if(name=="loginmanager"){
                if(!d['iplist']){
                    return false
                }
            }else{
                if(!d['line']&&!d['product']&&!d['app']&&!d['idc']&&!d['other_key']&&!d['iplist']){
                    if(name=="serverinit"){
                        if(!d['initype']){
                            return false
                        }
                    }else{
                        return false
                    }
                    
                }
            }
        }else if(id=="relevancesearch"||id=="taskrelevancehistory"){
            dom=angular.element('button#relevancesearch[searchinfo=""]')
            url='get_task_relevance_history'
            var key=dom.prev().val().trim()
            if(!key&&!pageid){
                return false
            }
            d['pageid']=pageid
            d['name']=key
        }else if(id=="informationcollect"){
            dom=angular.element('button#informationcollect[searchinfo=""]')
            var pdm=dom.parent().parent()
            var tmpid=pdm.prev().find('div.dropdown').dropdown('get value').replace(/0/,'')
            var dtime=pdm.find('input').val()
            d['name']=tmpid
            d['datetime']=dtime
            url='get_collecttemplate_history'

            if(!pageid && !tmpid && !dtime){
                return false
            }else{
                d['pageid']=pageid
            }
        }else if(id=="fault"){
            dom=angular.element('button#fault[searchinfo=""]')
            var tdmmm=dom.parent().parent().parent()
            d['name']=tdmmm.find('.faulttype').dropdown('get value')
            d['status']=tdmmm.find('.faultstate').dropdown('get value')
            d['htime']=tdmmm.find('.calendar input').val()
            d['zone']=tdmmm.find('.faultzone input').val()
            d['iplist']=$scope.gmzonesearchlist
            if(!d['name']&&!d['status']&&!d['htime']&&!d['zone']&&!d['iplist']){
                return false
            }
            d['pageid']=pageid
            
        }else if(id=="taskhistory"){
            dom=angular.element('button#taskhistory[searchinfo=""]')
            var tpdm=dom.parent().parent().parent()
            $scope.task.taskhistory.historysearch={}
            $scope.task.taskhistory.historysearch['relevanceapp']=tpdm.find('div.relevanceapp').dropdown('get value')
            $scope.task.taskhistory.historysearch['relevanceinfo']=tpdm.find('div.relevanceinfo').dropdown('get value')
            $scope.task.taskhistory.historysearch['status']=tpdm.find('div.status').dropdown('get value')
            $scope.task.taskhistory.historysearch['date_start']=tpdm.find('div.date_start').find('input').val()
            $scope.task.taskhistory.historysearch['date_end']=tpdm.find('div.date_end').find('input').val()
            $scope.task.taskhistory.historysearch['custominfo']=tpdm.find('div.custominfo input').val()
            url='get_ngrepeat_data_taskhistoryinfo'
            var uphtm='<tbody name="taskhistory"  list="taskmanager.taskhistory.taskhistorylist.taskhistoryinfo" repeatdataupdate></tbody>'

            if(!pageid){
                return $scope.compile(uphtm)($scope)
            }
            d['pageid']=pageid
            d['data']=$scope.task.taskhistory.historysearch

        }else if(id=="taskcustom"){
            dom=angular.element('button#taskcustom[searchinfo=""]')
            url='get_ngrepeat_data_taskinfo'

            var uphtm='<tbody name="taskcustom"  list="taskmanager.taskcustom.taskinfolist.taskinfo" repeatdataupdate></tbody>'
            if(dom.is('i')){
                var trdm=dom.parent().prev()
            }else{
                var trdm=dom.prev()
            }
            var key=trdm.val().trim()
            
            if(!pageid){
                if(key==""){
                    return false
                }
                $scope.taskcustomkey=key
                d['key']=$scope.taskcustomkey
                return $scope.compile(uphtm)($scope)
            }
            d['pageid']=pageid
            if(key){
                d['key']=key
            }
        }else if(id=="servergroup"||id=="serverhost"){
            var dd=$scope.breadcrumblist
            var list=$scope.servergroupsearchlist
            d['line']=dd['line']['key']
            d['product']=dd['product']['key']
            if(name=="group"||name=="groupdetails"){
                dom=angular.element('button#servergroup[name="group"]')
                var uphtm='<div  name="groupdetails" list="servermanager.servergroup.grouplist.'+dd['line']['key']+'_and_'+dd['product']['key']+'_and_'+dd['app']['key']+'" repeatdataupdate></div>'
                url='get_ngrepeat_data_groupdetails'
                d['app']=dd['app']['key']
                
            }else if(name=="member"||name=="groupmember"||name=="serverdetails"){
                dom=angular.element('button#servergroup[name="member"]')
                var uphtm='<div  name="serverdetails" list="servermanager.servergroup.serverdetails.'+dd['line']['key']+'_and_'+dd['product']['key']+'_and_'+dd['app']['key']+'_and_'+dd['server']['key']+'" repeatdataupdate></div>'
                url='get_ngrepeat_data_serverdetails'
                d['group']=dd['server']['key']
            }
            
            if(!pageid){
                if(list==""){
                    return false
                }
                return $scope.compile(uphtm)($scope)
            }

            d['pageid']=pageid
        }
        dom.addClass('loading')
        commservice.request_url(url, 'post', d, function(dt){
            dom.removeClass('loading')
            if(id=="assetfilter"){
                if(dt['data'].length==0){
                    dt['data']=[]    
                }
                if(pageid){
                    if(check.isfirst(name)){
                        $scope.asset.assetmanager.asset.tatisticsassetlist.push.apply($scope.asset.assetmanager.asset.tatisticsassetlist, dt['data'])
                    }else if(check.issecond(name)){
                        $scope.asset.assetmanager.asset.historyassetlist.push.apply($scope.asset.assetmanager.asset.historyassetlist, dt['data'])
                    }else if(check.isthird(name)){
                        $scope.asset.assetmanager.asset.assetlist.push.apply($scope.asset.assetmanager.asset.assetlist, dt['data'])
                    } 
                }else{
                    if(check.isfirst(name)){
                        $scope.asset.assetmanager.asset.tatisticsassetlist=dt['data']
                    }else if(check.issecond(name)){
                        $scope.asset.assetmanager.asset.historyassetlist=dt['data']
                    }else if(check.isthird(name)){
                        $scope.asset.assetmanager.asset.assetlist=dt['data']
                    } 
                }

            }else if(id=="servergroup"||id=="serverhost"){
                if(name=="groupdetails"){
                    var key=dd['line']['key']+'_and_'+dd['product']['key']+'_and_'+dd['app']['key']
                    $scope.servermanager.servergroup.grouplist[key].push.apply($scope.servermanager.servergroup.grouplist[key], dt['data'])
                }else if(name=="groupmember"||name=="serverdetails"){
                    var key=dd['line']['key']+'_and_'+dd['product']['key']+'_and_'+dd['app']['key']+'_and_'+dd['server']['key']
                    $scope.servermanager.servergroup.serverdetails[key].push.apply($scope.servermanager.servergroup.serverdetails[key], dt['data'])
                }
            }else if(id=="taskhistory"){
                fdm=dom.parent().parent().parent()
                $scope.taskmanager.taskhistory.taskhistorylist.taskhistoryinfo.push.apply($scope.taskmanager.taskhistory.taskhistorylist.taskhistoryinfo, dt['data'])
            }else if(id=="relevancesearch"||id=="taskrelevancehistory"){
                fdm=dom.parent().parent()
                if(id=="relevancesearch"){
                    $scope.task.taskcreate.taskrelevancehistory=dt['data']
                }else{
                    $scope.task.taskcreate.taskrelevancehistory.push.apply($scope.task.taskcreate.taskrelevancehistory, dt['data'])
                }
            }else if(id=="fault"){
                if(pageid){
                    $scope.faultinfodata.push.apply($scope.faultinfodata, dt['data'])
                }else{
                    $scope.faultinfodata=dt['data']
                }
                
            }else if(id=="informationcollect"){
                fdm=dom.parent().parent().parent()
                if(pageid){
                    $scope.taskmanager.collecttemplate.collecttemplatehistory.push.apply($scope.taskmanager.collecttemplate.collecttemplatehistory, dt['data'])
                }else{
                    $scope.taskmanager.collecttemplate.collecttemplatehistory=dt['data']
                }
            }else if(id=="taskcustom"){
                $scope.taskmanager.taskcustom.taskinfolist.taskinfo.push.apply($scope.taskmanager.taskcustom.taskinfolist.taskinfo, dt['data'])
            }
            if(!fdm){
                fdm=dom.parent().parent().parent().parent().parent()
            }

            var pdm=fdm.next()
            var plen=Math.ceil(dt['data_len']/dt['tr_len'])
            $scope.get_pagination_info(pdm, pageid, plen, id, name)
        })
    };
    $scope.statelist={
        'error':'red',
        'offline':'purple',
        'filenotexists':'pink',
        'logininfoerr':'pink',
        'timeout':'pink',
        'failed':'red',
        'running':'teal',
        'cancel':'orange',
        'ready':'blue',
        'success':'green',
        'done':'green',
    }
    $scope.check_iplist=[];
    $scope.data_check=function(data){
        for(k in data){
            if(data[k]==""||data[k]==undefined){
                return true
            }
        }
        return false
    };
    $scope.removaldata={}
    $scope.breadcrumblist={};
    $scope.servergroupevent=function(dom){};
    $scope.get_accordion_content=function(data, dom, des){
        if(!dom.next().is('div.content')){
            dom.after('<div class="content"></div>')
            if(data.length!=0){
                dom.next().append('<div class="ui fluid massive secondary vertical pointing text menu"></div>')
            }
        }else if(dom.next().find('div.secondary.menu').length==0){
            dom.next().append('<div class="ui fluid massive secondary vertical pointing text menu"></div>')
        }
        for(i in data){
            for(k in data[i]){
                if(dom.next().find('div.secondary.menu a[name="'+k+'"]').length==0){
                    if(!des){
                        var st=''
                    }else{
                        var st='stype="'+des+'"'
                    }
                    dom.next().find('div.secondary.menu').append('<a name="'+k+'" '+st+' id="server" class="item bread">'+data[i][k]+'</a>')
                }
            }
        }
        $scope.servergroupevent()
    };
    $scope.get_pagination_info=function(pdm, pageid, plen, id, name, style){
        if(style==undefined){
            style=''
        }
        if(pageid==undefined&&plen){
            var phtml=commservice.get_pagination_menu(plen, id, name)
            var pd=$scope.compile('<div class="ui bottom fixed red  menu container" '+style+'><div class="ui center aligned segment">'+phtml+'</div></div>')($scope)
            pdm.find('.ui.bottom.fixed.red.menu.container').remove()
            if(phtml){
                pdm.append(pd)
            }
        }else if(plen==0){
            pdm.find('.ui.bottom.fixed.red.menu.container').remove()
        }
    }
    $scope.alert_modal=function(dom, head, message, url, dt, fn){
        var loadinged=false
        var dm=angular.element($scope.commservice.get_confirm_modal(head,message,'ui small modal'))
        dm.modal('setting', 'onHidden', function(){
            if(!loadinged){
                dom.removeClass('loading')
            } 
        }).modal('show')
        dom.addClass('loading')
        dm.find('.actions').find('.negative.button').click(function(){
            dom.removeClass('loading')
        })
        dm.find('.actions').find('.right.button').click(function(){
            loadinged=true
            $scope.commservice.request_url(url, 'post', dt, fn, function(){
                $scope.commservice.alert_message('err',"alert_modal 请求失败")
                return false
            })
        })
    };
    $scope.getresult=function(des, data, otherkey){
        var title=''
        var head=''
        var trbody=''
        
        trbody=''
        head=''
        if(des=='logincheck'){
            title='检测结果'
            var d={'ip':'ip', 'ret':'检测结果'}
        }else if(des=="taskcustom"){
            title='历史记录'
            var d={'filename':'文件名', 'oprttion':'操作'}
        }else if(des=="collecttemplatehistory"){
            title='信息收集详情'
            var d={'key':'key', 'value':'value'}
        }else if(des=="status"){
            title='客户端状态'
            var d={'ip':'ip', 'ret':'状态'}
        }else if(des=="deploy"){
            title='客户端部署结果'
            var d={'ip':'ip', 'ret':'结果'}
        }else if(des=="serverinit"){
            title='初始化结果'
            var d={'ip':'ip', 'ret':'初始化结果'}
        }

        for(k in d){
            head+='<th rowspan="1" class="'+k+'">'+d[k]+'</th>'
        }
        for(i in data){
            trbody+='<tr>'
            if(des=='taskcustom'){
                trbody+='<td class="task_id" style="display:none">'+otherkey+'</td></td><td class="filename">'+data[i]+'</td><td class="option"><button id="'+des+'" class="ui green basic button ng-isolate-scope" download>下载</button><button id="'+des+'file" class="ui red basic button ng-isolate-scope" trdeletebutton>删除</button></td>'
            }else{
                if(data[i]=="failed"||data[i]=="offline"){
                    trbody+='<td class="ip">'+i+'</td><td class="ret red">'+data[i]+'</td>'
                }else{
                    trbody+='<td class="ip">'+i+'</td><td class="ret green">'+data[i]+'</td>'
                }
            }

            trbody+="</tr>"
        }
        angular.element($scope.compile($scope.commservice.get_structured_comp_table(head, trbody, {'title':title}))($scope)).modal('show')
    };
    $scope.dialogdata={
        left:[],
        right:[],
        leftcheckeddata:[],
        leftkeyvalue:[],
        leftkey:function(d){
            if($scope.dialogdata.leftkeyvalue.indexOf(d)==-1){
                $scope.dialogdata.leftkeyvalue.push(d)
            }
        },
        rightcheckeddata:[],
        rightkeyvalue:[],
        rightkey:function(d){
            if($scope.dialogdata.rightkeyvalue.indexOf(d)==-1){
                $scope.dialogdata.rightkeyvalue.push(d)
            }
        }
    }
    $scope.main={
        
    };
    $scope.trdata={}
    $scope.asset={
        assetmanager:{
            dropmeninfoinit:function(){
                $scope.asset.assetmanager.accountfilter={}

                $scope.asset.assetmanager.accountfilter.line={}
                $scope.asset.assetmanager.accountfilter.product={}
                $scope.asset.assetmanager.accountfilter.app={}
                $scope.asset.assetmanager.accountfilter.idc={}
                $scope.asset.assetmanager.accountfilter.other={}
                $scope.asset.assetmanager.accountfilter.linevalue=''
                $scope.asset.assetmanager.accountfilter.productvalue=''
                $scope.asset.assetmanager.accountfilter.appvalue=''
                $scope.asset.assetmanager.accountfilter.idcvalue=''
                $scope.asset.assetmanager.accountfilter.iplist=''
                $scope.asset.assetmanager.accountfilter.other_key=''

                $scope.asset.assetmanager.accountfilter.historyline={}
                $scope.asset.assetmanager.accountfilter.historyproduct={}
                $scope.asset.assetmanager.accountfilter.historyapp={}
                $scope.asset.assetmanager.accountfilter.historyidc={}
                $scope.asset.assetmanager.accountfilter.historyother={}
                $scope.asset.assetmanager.accountfilter.historylinevalue=''
                $scope.asset.assetmanager.accountfilter.historyproductvalue=''
                $scope.asset.assetmanager.accountfilter.historyappvalue=''
                $scope.asset.assetmanager.accountfilter.historyidcvalue=''
                $scope.asset.assetmanager.accountfilter.historyiplist=''
                $scope.asset.assetmanager.accountfilter.historyother_key=''
                
                $scope.asset.assetmanager.accountfilter.tatisticsline={}
                $scope.asset.assetmanager.accountfilter.tatisticsproduct={}
                $scope.asset.assetmanager.accountfilter.tatisticsapp={}
                $scope.asset.assetmanager.accountfilter.tatisticsidc={}
                $scope.asset.assetmanager.accountfilter.tatisticsother={}
                $scope.asset.assetmanager.accountfilter.tatisticslinevalue=''
                $scope.asset.assetmanager.accountfilter.tatisticsproductvalue=''
                $scope.asset.assetmanager.accountfilter.tatisticsappvalue=''
                $scope.asset.assetmanager.accountfilter.tatisticsidcvalue=''
                $scope.asset.assetmanager.accountfilter.tatisticsiplist=''
                $scope.asset.assetmanager.accountfilter.tatisticsother_key=''

                $scope.asset.assetmanager.assetlist=[]
                $scope.asset.assetmanager.historyassetlist=[]
                $scope.asset.assetmanager.tatisticsassetlist=[]
            },
            isfirst:function(name){
                if(name=="assetstatistics"||name=="logintools"||name=="initoolsmanager"){
                    return true
                }else{
                    return false
                }
            },
            issecond:function(name){
                if(name=="assetchangehistory"||name=="logindefault"||name=="logininit"){
                    return true
                }else{
                    return false
                }
            },
            isthird:function(name){
                if(name=="assetmanager"||name=="loginmanager"||name=="serverinit"){
                    return true
                }else{
                    return false
                }
            }
        }
    };
    $scope.privilege={
        usergroup:{
            username:'',
            userdes:'',
            groupname:'',
            groupdes:'',
            userlist:['a','b'],
            grouplist:['a','b']
        },
        key:{
            id:"",
            des:"",
            value:"",
            keylist:['a','b']
        },
        privilege:{
            privilegelist:['a','b'],
            privilegepool:['a','b']
        },
        inform:{
            accountname:'',
            accountdes:'',
            contactname:'',
            contactdes:'',
            type:'',
            typelist:['email', 'wechat'],
            contactlist:[],
            accountlist:[],
            accountpwd:'',
            accountserver:'',
            accountsmtp_port:'',
            accountsmtp_ssl_port:'',
            accountwechatid:'',
            accountwechatsecret:'',
            //修改状态
            slider_checked:false,
            checkbox_checked:function(d){
                if(d=="on"){
                    $scope.privilege.inform.slider_checked=true
                }else if(d=="off"||d==""){
                    $scope.privilege.inform.slider_checked=false
                }else{
                    $scope.privilege.inform.slider_checked=undefined
                }
                
                return true
            }
        }
    };
    $scope.host={
        
    };

    $scope.task={
        taskcreate:{
            relevance:{

            }
        },
        taskhistory:{
            historysearch:{
                
            },
            tasklog:[]
        }
    };
    $scope.loginstatus={};
    $scope.datetime={};
})
mainmodule.directive('datatime',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            setInterval(function() {
                var now = (new Date()).toLocaleString();
                element.text(now);
            }, 1000);
        }
    }
})

mainmodule.directive('loginout',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                scope.$parent.commservice.request_url('loginout.html','post',{},function(){
                    scope.$parent.commservice.page_jump("/")
                })
            })
        }
    }
})

mainmodule.directive('gettaskhistory',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var uphtm='<tbody name="taskhistory"  list="taskmanager.taskhistory.taskhistorylist.taskhistoryinfo" repeatdataupdate></tbody>'
            scope.$parent.compile(uphtm)(scope.$parent)
            var a=window.setInterval(function(){
                if(angular.element('.taskhistorypage').length==0){
                    window.clearInterval(a)
                    return false
                }
                if(!scope.$parent.taskhistory_refreshpage){
                    return false
                }
                scope.$parent.compile(uphtm)(scope.$parent)
            }, 5000)
        }
    }
})
mainmodule.directive('feildset',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var tdm=element.find('> .feild:not(.notneed)')
            var sw=window.screen.width
            if(tdm.length == 6 && sw < 1400){
                tdm.css({
                    'padding-left':'.4em',
                    'padding-right':'.4em'
                })
            }else if(tdm.length > 6 && sw < 1400){
                tdm.css({
                    'padding-left':'0em',
                    'padding-right':'0em'
                })
                setTimeout(function(){
                    tdm.find('.selection.dropdown').css('min-width', '12.8em')
                }, 3)
            }
        }
        
    }
})

mainmodule.directive('calendar',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var type=element.attr('datetype')
            scope.date_str_format=function(date_str){
                if(Number(date_str) < 10){
                    date_str='0'+date_str
                }
                return date_str
            }
            scope.getdate_str=function(date, type){
                //返回数据库now() 类型的时间
                if (!date) return '';
                var day = scope.date_str_format(date.getDate());
                var month = scope.date_str_format(date.getMonth() + 1);
                var year = date.getFullYear();
                var hours = scope.date_str_format(date.getHours());
                var minutes = scope.date_str_format(date.getMinutes());
                var seconds = scope.date_str_format(date.getSeconds());
                //var milliseconds = date.getMilliseconds()
                if(type=="dateonly"){
                    return year + '-' + month + '-'+ day;
                }else if(type=="datetime"){
                    return year + '-' + month + '-'+ day + " " + hours + ':' + minutes + ':'+ seconds;
                }
            }
            var tdate=function (date, settings) {
                return scope.getdate_str(date, type)
            }
            if(type=="dateonly"){
                var dp='date'
            }else if(type=="datetime"){
                var dp='datetime'
                var datetime=function (date, settings) {
                    return scope.getdate_str(date, type)
                }
            }
            element.calendar({
                type: dp,
                text:{
                    months: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                    monthsShort: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
                },
                monthFirst: false,
                ampm:false,
                formatter: {
                    date: tdate,
                    datetime: datetime
                }
            });
        }
    }
})
mainmodule.directive('localsearch',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.keyup(function(){
                var sdm=element.parent().parent()
                sdm.addClass('loading')
                setTimeout(function(){
                    var id=element.attr('id')
                    var value=element.val()
                    var tdm=sdm.parent().next()
                    var keyselector='tr:gt(0)'
                    var ttm=''
                    
                    if(id=="user"||id=="group"||id=="privilege"||id=="privilegepool"){
                        var selector="td.name:contains("+value+")"
                        if(id=="privilegepool"){
                            selector="td.des:contains("+value+"),td.remark:contains("+value+")"
                        }
                    }else if(id=="taskgroupselect"){
                        tdm=sdm.parent().parent().parent().next()
                        var selector='div.item[keyname="'+value+'"]'
                        keyselector='div.item'
                        ttm=tdm.find(selector)
                    }else if(id=="serverprivilege"){
                        var selector="td#serverprivilege:contains("+value+")"
                    }else if(id=="collecttemplate"){
                        var selector="td.template_id:contains("+value+"),td.des:contains("+value+")"
                    }
                    if(!value){
                        tdm.find(keyselector).show()
                        sdm.removeClass('loading')
                        return false
                    }
                    tdm.find(keyselector).hide()
                    if(!ttm){
                        tdm.find(selector).parent().show() 
                    }else{
                        ttm.show() 
                    }
                    sdm.removeClass('loading')
                }, 800)
            })
        }
    }
})


mainmodule.directive('repeatdataupdate',function(){
    return {
        scope:{
            list:'='
        },
        restrict:'EA',
        replace:false,
        link:function(scope, element, attrs){
            var id=element.attr('list')
            var name=element.attr('name')
            var idd=element.attr('id')
            if(id=="privilege.key.keylist"){
                var url='get_keylist'
            }
            var commservice=scope.$parent.commservice
            var idl=id.split('.')
            var url="get_ngrepeat_data_"+idl[idl.length-1]
            var dt={}
            if(name=="servergroup"||name=="appdetails"||name=="groupdetails"||name=="serverdetails"||name=="serverprivilegedetails"){
                scope.list=[]

                if(idd=="taskservershistory"){
                    dt['task_name']=scope.$parent.task_name
                    url='get_ngrepeat_data_taskservers'

                    if(scope.$parent.taskserverip){
                        dt['ip']=scope.$parent.taskserverip
                    }
                }else if(name=="serverprivilegedetails"){
                    url='get_ngrepeat_data_serverprivilegedetails'
                }else{
                    url='get_ngrepeat_data_'+ name
                }
                var list=scope.$parent.servergroupsearchlist
                if(list!=""&&list!=undefined){
                    dt['list']=list
                }
                dt['line']=idl[idl.length-1].split('_and_')[0]
                dt['product']=idl[idl.length-1].split('_and_')[1]
                if(name=="groupdetails"||name=="serverdetails"||name=="serverprivilegedetails"){
                    dt['app']=idl[idl.length-1].split('_and_')[2]
                }
                if(name=="serverdetails"||name=="serverprivilegedetails"){
                    dt['group']=idl[idl.length-1].split('_and_')[3]
                }
                if(idd=="taskcreate"){
                    dt['gettype']="taskcreate"
                }
            }else if(name=='taskhistory'){
                url='get_ngrepeat_data_taskhistoryinfo'
                dt['data']=scope.$parent.task.taskhistory.historysearch
            }else if(name=='relevancehistory'){
                url='get_task_relevance_info'
                
            }else if(name=='taskrelevancehistory'){
                url='get_task_relevance_history'
            }else if(name=="taskcustom"){
                var taskcustomkey=scope.$parent.taskcustomkey
                var tasktype=element.attr('tasktype')
                if(tasktype=="relevance"){
                    scope.list=[]
                    return false
                }
                if(taskcustomkey!=undefined){
                    dt['key']=taskcustomkey
                }
            }

            commservice.request_url(url, "post", dt, function(d){
                if(id=="privilege.inform.contactlist"){
                    scope.$parent.privilege.inform.contactlist=d
                }else if(id=="privilege.inform.accountlist"){
                    scope.$parent.privilege.inform.accountlist=d
                }else if(id=="privilege.privilege.privilegelist"){
                    scope.$parent.privilege.privilege.privilegelist=d
                }else if(id=="privilege.privilege.privilegepool"){
                    scope.$parent.privilege.privilege.privilegepool=d
                }else if(id=="privilege.usergroup.userlist"){
                    scope.$parent.privilege.usergroup.userlist=d
                }else if(id=="privilege.usergroup.grouplist"){
                    scope.$parent.privilege.usergroup.grouplist=d
                }else if(id=="privilege.key.keylist"){
                    scope.$parent.privilege.key.keylist=d
                }else if(idd=="taskservershistory"){
                    scope.list=d['data']
                    if(d['localhost']){
                        scope.$parent.task.taskhistory.localhost=[d['localhost']]
                    }
                    if(scope.$parent.taskserverip){
                        scope.$parent.task.taskhistory.serversinfo={}
                        setTimeout(function(){
                            scope.$parent.task.taskhistory.serversinfo=d['serverinfo']
                            scope.$parent.$apply(scope.$parent.task.taskhistory.serversinfo)
                        }, 5)
                    }

                }else if(id=='taskmanager.taskcustom.taskinfolist.taskinfo'||name=='taskrelevancehistory'||name=="taskhistory"){
                    scope.list=d['data']
                    var plen=Math.ceil(d['data_len']/d['tr_len'])
                    var pdm=angular.element('tbody[name="'+name+'"]')

                    var pageid=undefined
                    var tidd=name

                    scope.$parent.get_pagination_info(pdm, pageid, plen, tidd, name)
                    scope.$parent.taskcustomkey=''

                }else if(name=="serverprivilegedetails"){
                    scope.list=d['data']
                }else if(id.match(/servermanager.servergroup.applist/)||id.match(/servermanager.servergroup.grouplist/)||id.match(/servermanager.servergroup.serverdetails/)){
                    scope.list=d['data']
                    var rightdm=angular.element('.rightdm')
                    var plen=Math.ceil(d['data_len']/d['tr_len'])
                    var pdm=rightdm.find('table')
                    var pageid=undefined
                    if(id.match(/servermanager.servergroup.applist/)){
                        var tidd='serverapp'
                    }else if(id.match(/servermanager.servergroup.grouplist/)){
                        var tidd='servergroup'
                    }else if(id.match(/servermanager.servergroup.serverdetails/)){
                        var tidd='serverhost'
                    }

                    scope.$parent.get_pagination_info(pdm, pageid, plen, tidd, name, 'style=left:1em')
                    scope.$parent.servergroupsearchlist=''
                }else{
                    scope.list=d
                }
            })
        }
    }
})

mainmodule.directive('serverinitreset',function(){
    return {
        scope:{
            key:'='
        },
        restarict:'A',
        link:function(scope, element, attrs){
            var name=element.attr('name')
            if(name=='status' && scope.key.length > 17){
                var state=scope.key[18]
                if(state['value']!='success'){
                    element.hide()
                }
                element.click(function(){
                    setTimeout(function(){
                        var dd=scope.$parent.trdata
                        scope.$parent.alert_modal(element, '请确认', '确定设置 '+dd['telecom_ip']+ '为失败?', 'serverinit_reset', {ip:dd['telecom_ip']}, function(d){
                            scope.$parent.commservice.alert_message(d['status'], d['code'], d['message'])
                            if(d['status']=='err'){
                                return false
                            }
                            element.parent().parent().remove()
                        })
                    },500)
                })
            }else if(name=='icondetail' && scope.key.length > 5){
                var user=scope.key[5]['value'].replace(/未设置/g,'')
                var port=scope.key[6]['value'].replace(/未设置/g,'')
                var pwd=scope.key[7]['value'].replace(/未设置/g,'')
                if(!(user||port||pwd)){
                    element.addClass('red')
                }else{
                    element.addClass('green')
                }
            }else if(name=="loginmanger"){
                var user=scope.key[3]['value'].replace(/未设置/g,'')
                var port=(''+scope.key[4]['value']+'').replace(/未设置/g,'')
                var pwd=scope.key[5]['value'].replace(/未设置/g,'')

                if(!(user||port||pwd)){
                    element.addClass('red')
                }else{
                    element.addClass('green')
                }
            }
        }
    }
})
mainmodule.directive('requestbutton',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            var dt={}
            var id=element.attr('id')
            var name=element.attr('name')
            
            scope.dorequest=function(url, data, tet){
                var title='请确认'
                var dm=angular.element(scope.$parent.commservice.get_confirm_modal(title , tet,'ui small modal'))
                dm.modal('show')
                dm.find('div.actions').find('div.button:eq(1)').click(function(){
                    if(url=="task_restart"){
                        var skipsuccess=dm.find('form select#skipsuccess').val()
                        var exectimetype=dm.find('form select#exectimetype').val()
                        data['skipsuccess']=skipsuccess
                        data['exectimetype']=exectimetype
                    }
                    commservice.request_url(url, 'post', data, function(d){
                        if(d['status']=='err'){
                            commservice.alert_message(d['status'], d['code'], d['message'], true)
                            return false
                        }else if(id=='serverprivilegelist'){
                            commservice.alert_message(d['status'], d['code'], '请求发送成功', true)
                        }

                        var tasktb=element.parent().parent().parent()
                        tasktb.find('.buttons button').removeClass('disabled')
                        if(url=="task_restart"){
                            tasktb.find('td.status').text('running')
                            tasktb.find('td.status').css('color', scope.$parent.statelist['running'])
                            tasktb.find('.tasktimemodify,.taskrestart').addClass('disabled')
                        }else if(url=="get_server_privilegelist"){
                            var md=angular.element(compile(commservice.get_standard_modal('服务器权限信息['+dt['ip']+']', d))(scope.$parent))
                            var tddd=md.find('#serverprivilegelist.dropdown')
                            tddd.dropdown('setting', 'onChange', function(value, text, $choice){
                                tddd.addClass('loading')
                                var tv=tddd.dropdown('get value')
                                var serverid=$choice.attr('serverid')

                                commservice.request_url('search_server_privilege_filelist', 'post', {ip:dt['ip'], role:tv, serverid:serverid}, function(ddddd){
                                    if(ddddd['status']=='err'){
                                        commservice.alert_message(ddddd['status'], ddddd['code'], ddddd['message'])
                                        return 
                                    }
                                    //获取文件列表
                                    setTimeout(function(){
                                        scope.$parent.serverprivilegefilelist=[]
                                        scope.$parent.serverprivilegelist=[]
                                        scope.$parent.serverprivilegeid=serverid
                                        dt['serverid']=serverid
                                        commservice.request_url('get_server_privilege_filelist', 'post', dt, function(ad){
                                            scope.$parent.serverprivilegefilelist=ad['filelist']
                                            scope.$parent.serverprivilegelist=ad['privilege']
                                            tddd.removeClass('loading')
                                        })
                                    }, 3000)
                                })
                            })
                            $.fn.modal.settings.allowMultiple=true
                            md.modal('setting', 'onHide', function(){
                                $.fn.modal.settings.allowMultiple=false
                            })
                            md.modal('show')
                        }else if(url=="task_cancel"){
                            tasktb.find('td.status').text('cancel')
                            tasktb.find('td.status').css('color', scope.$parent.statelist['cancel'])
                        }
                    })
                })
            };

            element.click(function(){
                dt={}
                tet=''
                if(id=="taskhistory"){
                    setTimeout(function(){
                        var tdata=scope.$parent.trdata
                        var urllist=['task_cancel', 'task_restart', 'task_single_restart']
                        var urllist={
                            'task_cancel':{
                                'url':'task_cancel',
                                'des':'取消执行'
                            },
                            'task_restart':{
                                'url':'task_restart',
                                'des':'重新执行'
                            },
                            'task_single_restart':{
                                'url':'task_single_restart',
                                'des':'重新执行'
                            }
                        }
                        var des=urllist[name]['des']
                        var tinfo=tdata['task_name']
                        var url=urllist[name]['url']
                        dt['name']=tinfo
                        tet="确定"+des+"任务 "+tinfo+" ?"
                        if(name=="task_restart"){
                            var ddt={
                                'skipsuccess':{
                                    'type':'dropdown',
                                    'name':'是否跳过执行成功的任务;yes/跳过,no则反',
                                    'des':'是否跳过执行成功的任务',
                                    'menu':{
                                        'yes':'yes',
                                        'no':'no'
                                    }
                                },
                                exectimetype:{
                                    'type':'dropdown',
                                    'name':'是否立即运行任务,yes/立即运行,no/按照执行时间运行',
                                    'des':'是否立即运行任务,yes/立即运行,no/按照执行时间运行',
                                    'menu':{
                                        'yes':'yes',
                                        'no':'no'
                                    }
                                }
                            }
                            tet='<div class="ui segment">'+commservice.get_input_form("keyform", ddt)+'</div>'
                        }else if(name=="task_single_restart"){
                            var task_name=scope.$parent.task_name
                            var pdm=element.parent().prev()
                            tinfo=pdm.find('div.header').attr('filename')
                            dt['ip']=angular.element('.taskdetailipadd').text().trim()
                            dt['filename']=tinfo
                            dt['name']=task_name
                            element.parent().parent().parent().attr('status','running')
                            element.parent().parent().parent().find('.progress').attr('status','running')
                            tet="确定"+des+"任务 "+tinfo+" ?"
                        }
                        scope.dorequest(url, dt, tet)
                    }, 10)
                }else if(id=="serverprivilegelist"){
                    var trdm=element.parent().parent()
                    url='serverprivilege_file_execute'
                    dt['ip']=scope.$parent.serverprivilegeipadd
                    dt['id']=scope.$parent.serverprivilegeid
                    dt['file']=trdm.find('td:eq(0)').text().trim()
                    tet="确定执行 "+ dt['file']+" ?"
                    scope.dorequest(url, dt, tet)
                    
                }else if(id=="hostprivilegelist"){
                    var trdm=element.parent().parent()
                    var iptext=trdm.find('td.member').text().trim()
                    url='get_server_privilegelist'
                    dt['ip']=iptext.split('&')[0]
                    dt['line']=element.attr('line')
                    dt['product']=element.attr('product')
                    dt['app']=element.attr('app')
                    dt['group']=element.attr('group')
                    scope.$parent.serverprivilegeipadd=dt['ip']
                    tet="确定对 "+ dt['ip']+" 进行操作 ?"
                    if(iptext.split('&')[2] != 'yes'){
                        commservice.alert_message('err', '造作失败', ''+dt['ip']+'模式不为yes', true)
                        return 
                    }
                    scope.dorequest(url, dt, tet)
                }
            })
            if(name=="task_single_restart"){
                var task_name=scope.$parent.task_name
                var pdm=element.parent().prev()
                dt['ip']=angular.element('.taskdetailipadd').text().trim()
                dt['name']=task_name
                element.parent().parent().parent().attr('status','running')
                element.parent().parent().parent().find('.progress').attr('status','running')

                pdm.click(function(){
                    //显示执行日志
                    if (pdm.hasClass('showdone')){
                        return false
                    }
                    pdm.parent().parent().parent().find('.showlog').removeClass('showdone')
                    pdm.addClass('showdone')
                    var state=pdm.find('.attached.progress').attr('status')
                    if(state=="success"||state=="done"){
                        scope.$parent.task.taskhistory.tasklog=['show log error.status can not be '+state+'.']
                        return false
                    }
                    tinfo=pdm.find('div.header').attr('filename')
                    dt['filename']=tinfo
                    dt['request']='show_task_log'
                    scope.$parent.task.taskhistory.tasklog=[]
                    scope.$parent.$apply(scope.$parent.task.taskhistory.tasklog)
                    scope.$parent.taskwebsocket.send(commservice.obj_to_json(dt))
                })
                element.prev().click(function(){
                    //下载日志
                    tinfo=pdm.find('div.header').attr('filename')
                    dt['filename']=tinfo
                    dt['request']='task_log_download'
                    commservice.request_url('task_log_download', 'post', dt , function(d){
                        if(d['status']=='err'){
                            commservice.alert_message(d['status'], d['code'], d['message'], true)
                            return false
                        }
                        scope.$parent.commservice.page_jump(d)
                    })
                })
            }
            
        }
    }
})
mainmodule.directive('trmodifybutton',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                var id=element.attr('id')
                var trdm=element.parent().parent()
                if(id=="logininit"||id=="logininitools"||id=="logindefault"||id=="initoolsmanager"){
                    var trdm=trdm.parent()
                }else if(id=="serverapp"||id=="servergroup"||id=="groupmember"||id=="serverappremoval"||id=="servergroupremoval"||id=="groupmemberremoval"||id=="taskhistory"){
                    var trdm=trdm.parent().parent()
                }
                
                var url="modify_"+id+"_info"
                var commservice=scope.$parent.commservice
                var compile=scope.$parent.compile
                var d={}
                var ddt={}
                var historydata={}
                var title=''
                var dropdown=false

                scope.modify=function(id, dt, value_data){        
                    var context='<div class="ui segment">'+commservice.get_input_form("keyform", dt)+'</div>'
                    var md=angular.element(compile(commservice.get_standard_modal(title, context))(scope))
                    md.modal('show')

                    if(dropdown){
                        md.find('.dropdown').dropdown()
                        md.find('input[name="line_des"],input[name="product_des"],input[name="app_des"],input[name="group_des"]').parent().hide()
                        angular.forEach(md.find('.ui.dropdown'), function(data){
                            var ttm=angular.element(data)
                            var name=ttm.find('select').attr('id')
                            var frist=ttm.find('.menu .item:eq(0)')
                            var txt=frist.text().trim()
                            var value=frist.attr('data-value')
                            scope.$parent.removaldata[name]={}
                            scope.$parent.removaldata[name]['key']=value
                            scope.$parent.removaldata[name]['des']=txt
   
                            ttm.dropdown('set text', txt)
                            ttm.dropdown('set value', value)
                            ttm.removeClass('active visible')
                            ttm.find('.menu .item').removeClass('active selected')
                            frist.addClass('active selected')
                        })
                        md.find('div.ui.dropdown').dropdown('hide')
                        scope.$parent.input_check()
                        setTimeout(function(){
                            //上面的hide不生效,规避处理
                            md.find('div.ui.dropdown').dropdown('hide')
                        }, 570)
                        
                    }
                    if(id=="key"){
                        md.find('form input[name="value"]').val(value_data)
                    }
                    md.find('input.check').keyup(function(){
                        scope.$parent.input_check()
                    })
                    md.find('.actions').find('.right.button').click(function(){
                        if(id=="key"){
                            var nv=md.find('form input[name="value"]').val()
                            if(nv==value_data){
                                return false
                            }
                            d['name']=keyname
                            d['data']=nv
                        }else if(id=="taskhistory"){
                            d['name']=scope.$parent.trdata['task_name']
                            d['execute_time']=md.find('form .calendar input').val()
                            if(!d['execute_time']){
                                commservice.alert_message('err', '修改执行时间失败', '执行时间不能为空', true)
                                return false
                            }
                        }
                        var iscommit=false
                        
                        if(id=="assetmanager"||id=="logindefault"||id=="loginmanager"||id=="logintools"||id=="logininit"||id=="serverapp"||id=="servergroup"||id=="groupmember"){
                            var check_data={}
                            angular.forEach(md.find('input,textarea,select'), function(data){
                                var ttm=angular.element(data)
                                if(ttm.is('select')){
                                    var newk=ttm.attr('id')
                                }else if(ttm.is('textarea')){
                                    var newk=ttm.attr('class')
                                }else{
                                    var newk=ttm.attr('name')
                                }
                                var newv=ttm.val().trim()
                                
                                if(historydata[newk]!=newv && newk!="id" && newk!="c_time" && newk!="c_user"&&id=="assetmanager"){
                                    check_data[newk]=newv
                                    iscommit=true
                                }else if(id=="logindefault"||id=="loginmanager"||id=="logintools"||id=="logininit"||id=="serverapp"||id=="servergroup"||id=="groupmember"){
                                    check_data[newk]=newv
                                    if(historydata[newk]!=newv){
                                        iscommit=true
                                    }
                                }
                            })
                            if(iscommit){
                                d['data']=check_data
                                if(id=="assetmanager"){
                                    d['ip']=ip
                                }
                            }else{
                                md.modal('hide')
                                return false
                            }
                            if(id=="serverapp"||id=="servergroup"||id=="groupmember"){
                                d['data']['line']=scope.$parent.breadcrumblist['line']['key']
                                d['data']['product']=scope.$parent.breadcrumblist['product']['key']
                                if(id=="servergroup"||id=="groupmember"){
                                    d['data']['app']=scope.$parent.breadcrumblist['app']['key']
                                }
                                if(id=="groupmember"){
                                    d['data']['group_id']=scope.$parent.breadcrumblist['server']['key']
                                }
                            }

                            
                        }else if(id=='serverappremoval'||id=='servergroupremoval'||id=='groupmemberremoval'){
                            var checkdata=scope.$parent.removaldata
                            var cd={}
                            for(k in checkdata){
                                var cdt=checkdata[k]
                                cd[k]=cdt['key']
                                cd[k.split('_')[0]+'_des']=cdt['des']
                                if(cdt['des']==""||(md.find('select#'+k+'').next().next().text().trim() == ""&&cdt['des']=="")){
                                    commservice.alert_message('err', '提交失败' , '请输入完整'+k+'信息', true)
                                    return false
                                }
                            }
                            if(checkdata['line']['key']!=historydata['line']['name']||checkdata['product']['key']!=historydata['product']['name']||checkdata['app']['key']!=historydata['app']['name']){
                                iscommit=true
                            }

                            if((id=='servergroupremoval'||id=='groupmemberremoval') && checkdata['group_id']['key']!=historydata['server']){
                                iscommit=true
                            }
                            if(!iscommit){
                                md.modal('hide')
                                return false
                            }
                            cd['member']=scope.$parent.trdata['member']
                            d['data']=cd
                            d['old']=historydata
                        }
                        commservice.request_url(url, 'post', d, function(dt){
                            commservice.alert_message(dt['status'],"code:"+dt['code'],dt['message'])
                            if(dt['status']=="err"){
                                return false    
                            }
                            //更新数据
                            if(id=="key"){
                                var uphtm='<div list="privilege.key.keylist" repeatdataupdate></div>'
                                compile(uphtm)(scope.$parent)
                            }else if(id=="loginmanager"||id=="logindefault"||id=="logintools"||id=="logininit"||id=='assetmanager'){
                                trdm.find('td.user').text(d['data']['user'])
                                trdm.find('td.port').text(d['data']['port'])
                                trdm.find('td.pwd').text(d['data']['pwd'])
                                if(id=="assetmanager"&&d['data']['telecom_ip']!=undefined&&d['data']['telecom_ip']!=""){
                                    trdm.find('.telecom_ip').text(d['data']['telecom_ip'])
                                }
                            }else if(id=="serverapp"||id=="servergroup"||id=="groupmember"){
                                trdm.find('td.app_des').text(d['data']['app_des'])
                                trdm.find('td.group_des').text(d['data']['group_des'])
                                trdm.find('td.remark').text(d['data']['remark'])
                                trdm.find('td.modal').text(d['data']['modal'])
                            }else if(id=="groupmemberremoval"||id=="servergroupremoval"||id=="serverappremoval"){
                                trdm.remove()
                                var linedm=angular.element('.leftdm div#line[name="'+historydata['line']['name']+'"]')
                                var productdm=linedm.next().find('div#product[name="'+historydata['product']['name']+'"]')
                                var appdm=productdm.next().find('div#app[name="'+historydata['app']['name']+'"]')
                                var groupdm=appdm.next().find('a[name="'+scope.$parent.trdata['group_id']+'"]')
                                var apphtml=angular.element('.rightdm div#line[name="'+historydata['line']['name']+'"]')
                                
                                var nldm=angular.element('.leftdm div#line[name="'+d['data']['line']+'"]')
                                var npdm=nldm.next().find('div#product[name="'+d['data']['product']+'"]')
                                var nadm=npdm.next().find('div#app[name="'+d['data']['app']+'"]')
                                var ngdm=nadm.next().find('a[name="'+d['data']['group_id']+'"]')
                                var nghtml=angular.element('.rightdm table tbody')

                                // line 和 product 固定
                                if(nadm.length==0){
                                    var dml='<repeatdataupdate name="servergroup" list="servermanager.servergroup.appgrouplist.'+d['data']['line']+'_and_'+d['data']['product']+'" class="ng-isolate-scope"></repeatdataupdate>'
                                    compile(dml)(scope.$parent)

                                }
                                if(ngdm.length==0){
                                    groupdm.attr('name', d['data']['group_id']).text(d['data']['group_des'])
                                    groupdm.appendTo(nadm.next().find('.menu'))
                                }

                                scope.$parent.servergroupevent()
                            }
                        }, function(){
                            commservice.alert_message('err',"请求失败")
                            return false
                        })
                    })
                }

                if(id=="key"){
                    title='key值修改'
                    var value_data=trdm.find('td.value').text().trim()
                    var keyname=trdm.find('td.name').text().trim()
                    var dt={
                        'value':{
                            'name':'value',
                            'des':'ID对应的key值',
                            'other':'keyname="'+keyname+'"'
                        }
                    }
                    scope.modify(id, dt, value_data)
                }else if(id=="taskhistory"){
                    setTimeout(function(){
                        var ttttdd=scope.$parent.trdata
                        if(['done', 'running'].indexOf(ttttdd['status'])!=-1){
                            commservice.alert_message('err', '修改执行时间失败', '状态不能为'+ttttdd['status']+'', true)
                            return false
                        }
                        if(ttttdd['custom_name']){
                            var tnm=ttttdd['task_name']+'/'+ttttdd['custom_name']
                        }else{
                            var tnm=ttttdd['task_name']
                        }
                        
                        title='任务执行时间修改['+tnm+']'
                        scope.$parent.taskchangedata=ttttdd
                        var dt={
                            'value':{
                                'name':'选择任务执行时间',
                                'type':'calendar',
                                'calendartype':'datetime',
                                'des':'选择任务执行时间',
                                'other':'keyname="taskchangedata"'
                            }
                        }
                        scope.modify(id, dt)
                    }, 20)
                }else if(id=="assetmanager"){
                    var ip=trdm.find('.telecom_ip').text().trim()
                    title='资产信息['+ip+']'
                    commservice.request_url('get_asset_info', 'post', {ip:ip}, function(d){
                        var data=d['data']
                        var k=d['key']
                        for(i in k){
                            for(kk in k[i]){
                                var ck=kk
                                var des=k[i][kk]
                            }
                            for(ii in data){
                                if(data[ii]['telecom_ip']==ip){
                                    ddt[ck]={}
                                    ddt[ck]['name']=des
                                    ddt[ck]['des']=des
                                    historydata[ck]=data[ii][ck]
                                    if(ck=="id" || ck=="c_time" || ck=="c_user"){
                                        ddt[ck]['other']='value="'+data[ii][ck]+'"  disabled'
                                    }else{
                                        ddt[ck]['other']='value="'+data[ii][ck]+'"'
                                    }
                                }
                            }
                        }
                        scope.modify(id, ddt, '')
                    })
                }else if(id=="logindefault"||id=="loginmanager"||id=="logintools"||id=="logininit"){
                    var ddt={}
                    if(id=="loginmanager"){
                        var tip=trdm.find('td.telecom_ip').text().trim()
                        var uip=trdm.find('td.unicom_ip').text().trim()
                        var iip=trdm.find('td.inner_ip').text().trim()
                        historydata['telecom_ip']=tip
                        historydata['unicom_ip']=uip
                        historydata['inner_ip']=iip
                        ddt['telecom_ip']={
                            'name':'电信ip',
                            'des':'电信ip',
                            'other':'value="'+tip+'" disabled class="check"'
                        }
                        ddt['unicom_ip']={
                            'name':'联通ip',
                            'des':'联通ip',
                            'other':'value="'+uip+'" disabled class="check"'
                        }
                        ddt['inner_ip']={
                            'name':'内网ip',
                            'des':'内网ip',
                            'other':'value="'+iip+'" disabled class="check"'
                        }
                        title='服务器登录信息设置['+tip+']'
                    }else{
                        if(id=="logindefault"){
                            title='服务器默认登录信息设置'
                        }else if(id=="logintools"){
                            title='服务器动态登录信息设置'
                        }else if(id=="logininit"){
                            title='服务器初始化登录信息设置'
                        }
                        var line=trdm.find('td.line').text().trim()
                        var product=trdm.find('td.product').text().trim()
                        var app=trdm.find('td.app').text().trim()
                        var idc=trdm.find('td.idc').text().trim()
                        var owner=trdm.find('td.owner').text().trim()
                        ddt['line']={
                            'name':'产品线',
                            'des':'产品线名称',
                            'other':'value="'+line+'" disabled class="check"'
                        }
                        ddt['product']={
                            'name':'业务',
                            'des':'产品线下的业务名称',
                            'other':'value="'+product+'" disabled class="check"'
                        }
                        ddt['app']={
                            'name':'应用',
                            'des':'业务下的应用名称',
                            'other':'value="'+app+'" disabled class="check"'
                        }
                        ddt['idc']={
                            'name':'机房',
                            'des':'机房名称',
                            'other':'value="'+idc+'" disabled class="check"'
                        }
                        ddt['owner']={
                            'name':'资产负责人',
                            'des':'资产负责人',
                            'other':'value="'+owner+'" disabled class="check"'
                        }
                    }
                    var user=trdm.find('td.user').text().trim().replace(/未设置/,'')
                    var port=trdm.find('td.port').text().trim().replace(/未设置/,'')
                    var pwd=trdm.find('td.pwd').text().trim().replace(/未设置/,'')
                    historydata['line']=line
                    historydata['product']=product
                    historydata['app']=app
                    historydata['idc']=idc
                    historydata['owner']=owner
                    historydata['user']=user
                    historydata['port']=port
                    historydata['pwd']=pwd
                    ddt['user']={
                        'name':'登录用户',
                        'des':'登录系统的用户名',
                        'other':'value="'+user+'" class="check"'
                    }
                    ddt['port']={
                        'name':'登录端口',
                        'des':'登录系统的端口号',
                        'other':'value="'+port+'" class="check"'
                    }
                    ddt['pwd']={
                        'name':'登录密码',
                        'des':'登录系统的用户密码',
                        'other':'value="'+pwd+'" class="check"'
                    }
                    scope.modify(id, ddt, '')
                }else if(id=="serverapp"||id=="servergroup"||id=="groupmember"){
                    setTimeout(function(){
                        var data=scope.$parent.trdata
                        if(id=="serverapp"){
                            title='分类信息['+data['app']+']'
                            historydata['app']=data['app']
                            historydata['app_des']=data['app_des']
                            ddt['app']={
                                'name':'分类id',
                                'des':'分类id',
                                'other':'value="'+data['app']+'" class="check" disabled'
                            }
                            ddt['app_des']={
                                'name':'分类id描述(名称)',
                                'des':'分类id描述(名称)',
                                'other':'value="'+data['app_des']+'" class="check"'
                            }
                        }else if(id=="servergroup"){
                            title='主机组信息['+data['group_id']+']'
                            historydata['group_id']=data['group_id']
                            historydata['group_des']=data['group_des']
                            historydata['modal']=data['modal']
                            if(data['modal']=="yes"){
                                var modal={
                                    'yes':'yes',
                                    'no':'no'
                                }
                            }else if(data['modal']=="no"){
                                var modal={
                                    'no':'no',
                                    'yes':'yes'
                                }
                            }
                            historydata['remark']=data['remark']
                            ddt['group_id']={
                                'name':'主机组id',
                                'des':'主机组id',
                                'other':'value="'+data['group_id']+'" class="check" disabled'
                            }
                            ddt['modal']={
                                'type':'dropdown',
                                'name':'主机组模式',
                                'des':'主机组模式',
                                'menu':modal,
                                'other':'value="'+data['modal']+'" class="check"'
                            }
                            ddt['group_des']={
                                'name':'主机组描述(名称)',
                                'des':'主机组描述(名称)',
                                'other':'value="'+data['group_des']+'" class="check"'
                            }
                            ddt['remark']={
                                'type':'textarea',
                                'name':'主机备注',
                                'des':'主机备注信息',
                                'text':data['remark']
                            }
                        }else if(id=="groupmember"){
                            title='主机组成员信息['+data['member']+']'
                            historydata['member']=data['member']
                            historydata['modal']=data['modal']
                            historydata['asset_app']=data['asset_app']
                            if(data['modal']=="yes"){
                                var modal={
                                    'yes':'yes',
                                    'no':'no'
                                }
                            }else if(data['modal']=="no"){
                                var modal={
                                    'no':'no',
                                    'yes':'yes'
                                }
                            }
                            ddt['member']={
                                'name':'主机组成员ip',
                                'des':'主机组成员ip',
                                'other':'value="'+data['member']+'" class="check" disabled'
                            }
                            ddt['asset_app']={
                                'name':'成员ip业务类型',
                                'des':'成员ip业务类型',
                                'other':'value="'+data['asset_app']+'" class="check" disabled'
                            }
                            ddt['modal']={
                                'type':'dropdown',
                                'name':'主机组模式',
                                'des':'主机组模式',
                                'menu':modal,
                                'other':'value="'+data['modal']+'" class="check"'
                            }
                        }
                        
                        scope.modify(id, ddt, '')
                        
                    }, 300)
                }else if(id=="serverappremoval"||id=="servergroupremoval"||id=="groupmemberremoval"){
                    setTimeout(function(){
                        var data=scope.$parent.breadcrumblist
                        var trdata=scope.$parent.trdata
                        if(id=="serverappremoval"){
                            var app=trdata['app']
                        }else{
                            var app=data['app']['key']
                        }
                        
                        commservice.request_url('get_servergroup_removal', 'post', {'type':id,line:data['line']['key'], product:data['product']['key'] ,app:app,group_id:trdata['group_id'],member:trdata['member']}, function(db){
                            //line和product不支持自定义
                            historydata['line']=db['line'][0]['key']
                            historydata['product']=db['product'][0]['key']
                            historydata['app']=db['app'][0]['key']
                            if (db['group']!=undefined&&db['group'][0]!=undefined){
                                historydata['group_id']=db['group'][0]['key']
                            }else{
                                historydata['group_id']=''
                            }
                            
                            ddt['line']={
                                'type':'dropdown',
                                'name':'产品线(*从下拉菜单选择*)',
                                'des':'产品线',
                                'menu':db['line'],
                                'other':' name="serverline" selectfilter'
                            }
                            ddt['line_des']={
                                'name':'自定义产品线描述',
                                'des':'产品线描述,自定义新的产品线名称描述信息',
                                'other':'class="check" style="display:none"'
                            }
                            ddt['product']={
                                'type':'dropdown',
                                'name':'业务(*从下拉菜单选择*)',
                                'des':'业务',
                                'menu':db['product'],
                                'other':' name="serverproduct"  selectfilter'
                            }
                            ddt['product_des']={
                                'name':'自定义业务描述',
                                'des':'自定义业务描述,自定义新的业务名称描述信息',
                                'other':' class="check" style="display:none"'
                            }
                            ddt['app']={
                                'type':'dropdown',
                                'typekey':'search',
                                'name':'类型(*从下拉菜单选择,也可以自定义*)',
                                'des':'类型',
                                'menu':db['app'],
                                'other':'  name="serverapp" selectfilter'
                            }
                            ddt['app_des']={
                                'name':'自定义类型描述',
                                'des':'自定义类型描述,自定义新的类型名称描述信息',
                                'other':' class="check" style="display:none"'
                            }
                            if(id=="serverappremoval"){
                                title='分类迁移['+app+']'
                            }else if(id=="servergroupremoval" || id=="groupmemberremoval"){
                                if(id=="servergroupremoval"){
                                    title='主机组迁移['+trdata['group_id']+']'
                                }else if(id=="groupmemberremoval"){
                                    title='主机组成员迁移['+trdata['member']+']'
                                }
                                
                                ddt['group_id']={
                                    'type':'dropdown',
                                    'typekey':'search',
                                    'name':'主机组(*从下拉菜单选择,也可以自定义*)',
                                    'des':'主机组',
                                    'menu':db['group'],
                                    'other':'  name="servergroup" selectfilter'
                                }
                                ddt['group_des']={
                                    'name':'自定义主机组描述',
                                    'des':'自定义主机组描述,自定义新的自定义主机组描述名称描述信息',
                                    'other':' class="check" style="display:none"'
                                }
                            }
                            dropdown=true
                            scope.modify(id, ddt, db)
                            })
                    }, 100)
                }
            })
        }
    }
})

mainmodule.directive('selectfilter',function(){
    return{
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            element.unbind('click').click(function(){
                var name=element.attr('name')
                var id=element.find('select').attr('id')
                var pdm=element.parent()
                if(name=="serverline"||name=="serverproduct"||name=="serverapp"||name=="servergroup"){
                    element.find('input').blur(function(){
                        var tm=angular.element(event.target).next()
                        var tv=tm.text().trim()
                        if(tv==""){
                            scope.$parent.$parent.removaldata[id]['key']=tv
                            scope.$parent.$parent.removaldata[id]['des']=''
                            tm.next().next().dropdown('clear')
                        }
                    })
                    element.find('input').keyup(function(){
                        var kcode=event.keyCode;
                        //40下,38上

                        if(kcode!=38&&kcode!=40){
                            var dm=angular.element(event.target)
                            var tv=dm.val().trim()
                            var tpm=dm.parent().find('div.menu')
                            var textv=dm.parent().find('.text').text().trim()
                            dm.parent().find('select option[value="'+textv+'"]').remove()
                            var tp='<option class="custom" value="'+tv+'">'+tv+'</option>'
                            var dp='<div class="custom item" data-value="'+tv+'">'+tv+'</div>'
                            //dm.parent().find('.text').text(tv)
                            
                            scope.$parent.$parent.removaldata[id]['key']=tv
                            scope.$parent.$parent.removaldata[id]['des']=''
                            if(tv==""){
                                dm.parent().parent().next().hide()
                                return false
                            }
                            if(tpm.find('.item[data-value="'+tv+'"]').length==0){
                                dm.parent().parent().next().show().children().show()
                                dm.parent().parent().next().keyup(function(){
                                    var tdd=angular.element(event.target)
                                    var tvv=tdd.val()
                                    scope.$parent.$parent.removaldata[id]['des']=tvv
                                })
                            } 
                            dm.parent().find('select option:eq(0)').before(tp)
                            dm.parent().find('div.menu .item:eq(0)').before(dp)
                            element.find('.ui.search.dropdown').dropdown('set text', tv)
                            element.find('.ui.search.dropdown').dropdown('set value', tv)                     
                        }else{
                            var dm=element.find('.menu .item.active.selected')
                            var index=element.find('.menu .item').index(dm)
                            var tdm=element.find('select option:eq('+index+')')
                            var key=tdm.attr('value')
                            var des=tdm.text().trim()

                            scope.$parent.$parent.removaldata[id]['key']=key
                            scope.$parent.$parent.removaldata[id]['des']=des
                        }
                    })
                    element.find('div.menu  div.item').unbind('click').click(function(){
                        var dm=angular.element(event.target)
                        var tdm=dm.parent().find('select')
                        var index=dm.parent().find('div.item').index(dm)

                        var value=dm.attr('data-value')
                        var des=dm.text().trim()

                        scope.$parent.$parent.removaldata[id]['key']=value
                        scope.$parent.$parent.removaldata[id]['des']=des

                        element.next().hide()
                        if(!dm.hasClass('custom')){
                            tdm.find('.custom').remove()
                            dm.find('.custom').remove()
                        }
                        var sdm=element.find('select option:eq('+index+')')

                        if(name=="serverline"){
                            var ln=sdm.attr('value')
                        }else{
                            var ln=sdm.attr('line')
                        }
                        if(name=="serverproduct"){
                            var prt=sdm.attr('value')
                        }else{
                            var prt=sdm.attr('product')
                        }
                        if(name=="serverapp"){
                            var app=sdm.attr('value')
                        }else{
                            var app=sdm.attr('app')
                        }

                        if(sdm){
                            var cdt=scope.$parent.$parent.removaldata
                            
                            if(sdm.is('.custom')){
                                element.next().show().children().show()
                                scope.$parent.$parent.removaldata[id]['des']=''
                            }else{
                                element.next().show().children().hide()
                            }

                            if(name=="serverapp" && (ln!=cdt['line']['key']||prt!=cdt['product']['key']) || (name=="servergroup" && (ln!=cdt['line']['key']||prt!=cdt['product']['key'] || app!=cdt['app']['key']))){
                                scope.$parent.$parent.commservice.alert_message('warn', '选项告警', '此选项不属于当前业务/代理/类型;', true)
                            }
                        }

                        if(name=="serverline"){
                            var hdseletor='div[name="serverproduct"],div[name="serverapp"],div[name="servergroup"] '
                        }else if(name=="serverproduct"){
                            var hdseletor='div[name="serverapp"],div[name="servergroup"]'
                        }else if(name=="serverapp"){
                            var hdseletor='div[name="servergroup"]'
                        }

                        pdm.find(hdseletor).find('div.menu div.item').hide()
                        angular.forEach(pdm.find(hdseletor), function(data){
                            
                            var tttm=angular.element(data)
                            var tn=tttm.attr('name')
                            var id=tttm.find('select').attr('id')
                            tttm.find('.dropdown').dropdown('clear')

                            var key_str=''
                            if(name=="serverline"){
                                key_str='[line="'+ln+'"]'
                            }else if(name=="serverapp"){
                                key_str='[line="'+ln+'"][product="'+prt+'"][app="'+app+'"]'
                            }else if(name=="serverproduct"){
                                key_str='[line="'+ln+'"][product="'+prt+'"]'
                            }
                            scope.$parent.$parent.removaldata[id]['key']=''
                            scope.$parent.$parent.removaldata[id]['des']=''
                            
                            if(key_str){
                                var tl=tttm.find('select option')
                                var tv=tttm.find('select option'+key_str+'')

                                angular.forEach(tv, function(td){
                                    var ttt=angular.element(td)
                                    var index=tl.index(ttt)

                                    tttm.find('.menu .item:eq('+index+')').show()
                                    //由用户选择
                                    //tttm.find('.text').text(tttm.find('.menu .item:eq('+index+')').attr('data-value'))
                                })
                            }
                        })
                    })
                }
            })
        }
    }
})
mainmodule.directive('logindetail',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                var fd=element.parent().parent()
                var user=fd.find('td.user').text().trim()
                var port=fd.find('td.port').text().trim()
                var pwd=fd.find('td.pwd').text().trim()
                //scope.$parent.trdata获取数据
                var data={}
                var head=''
                var trbody=''
                
                var keys={
                    'user':{
                        'des':'用户',
                        'value':user
                    },
                    'port':{
                        'des':'端口',
                        'value':port
                    },
                    'pwd':{
                        'des':'密码',
                        'value':pwd
                    }
                }
                var title='登录信息'
                data['head']={
                        'Name':'名称', 
                        'value':'值'
                    }

                for(k in data['head']){
                    head+='<th rowspan="1" class="'+k+'">'+data['head'][k]+'</th>'
                }
                
                for(i in keys){
                    trbody+='<tr>'
                    trbody+='<td class="'+i+'">'+keys[i]['des']+'</td>'+'<td><i id="download" keyvalue="'+keys[i]['value']+'" class="'+i+'" tdicon></i>'+keys[i]['value']+'</td>'
                    trbody+="</tr>"
                }

                angular.element(scope.$parent.compile(scope.$parent.commservice.get_structured_comp_table(head, trbody, {'title':title}))(scope.$parent)).addClass('fullscreen').modal('show')
            })
        }
    }
})

mainmodule.directive('tdlable',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            var compile=scope.$parent.compile
            var commservice=scope.$parent.commservice
            
            attrs.$observe('class', function(){
              setTimeout(function(){
                var cls=element.attr('class')
                if((id=="servergroup"||id=="groupmember") && (cls=="group_id"||cls=="member")){
                    var pdm=element.parent()
                    var modal=pdm.find('td.modal').text().trim()
                    var asset_app=pdm.find('td.asset_app').text().trim()
                    if(modal=="yes"){
                        var color='teal'
                    }else{
                        var color='brown'
                    }

                    if(id=="servergroup"){
                        var lable='<a class="active item"><div class="ui mini '+color+' label" style="float:right">'+modal+'</div></a>'
                    }else if(id=="groupmember"){
                        var lable='<a class="ui mini '+color+' image label" style="float:right">'+asset_app+'<i style="display:none">&</i><div class="detail">'+modal+'</div></a>'
                    }
                    element.append('<i style="display:none">&</i>'+lable)
                }else if(id=="fault"){
                    var cl={
                           '1':{'des':'未处理', 'col':'red'},
                           '2':{'des':'已处理', 'col':'green'}
                    }
                    var num=element.text().trim()
                    if(element.hasClass("status")){
                        element.after('<td class="state_des" style="color:'+cl[num]['col']+'">'+cl[num]['des']+'</td>')
                    }
                }else if(id=="serverprivilegelist"){
                    var pd=scope.$parent.serverprivilegelist
                    var ht='<td class="opertion">'
                    var ttt=''
                    var pds={
                        'execute': {
                            'des': '执行',
                            'hd': 'requestbutton',
                            'col': 'red'
                        },
                        'download': {
                            'des': '下载',
                            'hd': 'download',
                            'col': 'green'
                        },
                        'update': {
                            'des': '更新',
                            'hd': 'upload',
                            'col': 'teal'
                        }
                    }

                    for(i in pd){
                        if(pd[i]!=""){
                            if(!pd[i] in pds){
                                continue
                            }
                            ttt+='<button id="'+id+'" class="ui small '+pds[pd[i]]['col']+' basic button" class="'+pd[i]+'"  '+pds[pd[i]]['hd']+'>'+pds[pd[i]]['des']+'</button>'
                        }
                    }
                    ht+=ttt+'</td>'
                    element.after(ht)
                    compile(element.parent().find('td.opertion'))(scope.$parent)
                }else if(id=="taskhistory"){
                    if(['id', 'custom_name', 'custom_type', 'task_type' , 'timestatus', 'create_time'].indexOf(cls)!=-1){
                        element.hide() 
                    }

                    if(cls=='task_name'){
                        var custom_name=element.parent().find('.custom_name').text().trim()
                        if(custom_name){
                            element.parent().find('.custom_name').show()
                            element.hide()
                        }
                    }
                    if(cls=="status"){
                        var state=element.attr('keyname')
                        var cl=scope.$parent.statelist[state]
                        if(state=="ready"){
                            var cl='blue'
                            var rdtxt=element.parent().find('.timestatus').text().trim()
                            if(rdtxt==0||rdtxt.match(/^-/)){
                                rdtxt="任务异常"
                            }else{
                                rdtxt='倒计时 '+rdtxt + ' s'
                            }
                            element.text(rdtxt)
                        }
                        element.css('color', cl)
                        element.parent().find('.buttons button').removeClass('disabled')
                        if(state=="running"){
                            element.parent().find('.tasktimemodify,.taskrestart').addClass('disabled')
                        }else if(state=='done'){
                            element.parent().find('.buttons button').addClass('disabled')
                        }
                        
                    }else{
                        element.removeAttr('keyname')
                    }
                }else if(id=="relevancetype"){
                    var apptype=element.attr('apptype')
                    if(!apptype){
                        element.removeAttr('apptype')
                    }else{
                        element.remove()
                    }
                }else if(id=="taskcustom"){
                    var tasktype=element.attr('tasktype')
                    if((cls=="task_id"||cls=="remark"||cls=="c_time"||cls=="c_user")&&tasktype=="relevance"){
                        element.hide() 
                    }
                }
              }, 1)
            })

        }
    }
})

mainmodule.directive('tdicon',function(){
    return {
        scope:{
            key:'='
        },
        restarict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            var commservice=scope.$parent.commservice
            download_file=function(){
                var cls=element.attr('class')
                var keyvalue=element.attr('keyvalue')
                if(keyvalue){
                    keyvalue=keyvalue.replace(/未设置/g,'')
                } 
                if(cls=="user"){
                    var ddd=scope.key[5]['value'].replace(/未设置/g,'')
                }else if(cls=="port"){
                    var ddd=scope.key[6]['value'].replace(/未设置/g,'')
                }else if(cls=="pwd"){
                    var ddd=scope.key[7]['value'].replace(/未设置/g,'')
                }else if(cls=="tool_path"){
                    var ddd=scope.key[5]['value'].replace(/未设置/g,'')
                }
                if(keyvalue!=undefined&&keyvalue!=''){
                    ddd=true
                }
                if(!ddd){
                    element.addClass('loading red large cloud download link icon')
                }else{
                    element.addClass('loading blue large cloud download link icon')
                }
                
                element.click(function(){
                    var tv=element.parent().text().trim().replace(/未设置/g,'')
                    if(!tv){
                        return false
                    }
                    if(element.hasClass('user')){
                        var tt=100
                        var k='user'
                    }else if(element.hasClass('port')){
                        var tt=100
                        var k='port'
                    }else if(element.hasClass('pwd')){
                        var tt=100
                        var k='pwd'
                    }else if(element.hasClass('tool_path')){
                        var tt=500
                        var k='tool_path'
                    }else{
                        return false
                    }
                    setTimeout(function(){
                        var d=scope.$parent.trdata
                        if(!d['keytype']||d['keytype']==undefined){
                            return false
                        }
                        var dt={}
                        dt['filetype']=d['keytype']
                        dt['line']=d['line']
                        dt['product']=d['product']
                        dt['app']=d['app']
                        dt['idc']=d['idc']
                        dt['owner']=d['owner']
                        dt['filekey']=k
                        dt[k]=d[k]
                        var url='loginfile_download'
                        commservice.request_url(url, 'post', dt, function(dd){
                            if(!dd){
                                return false
                            }
                            commservice.page_jump(dd)
                        })
                    }, tt)
                })
            }
            if(id=="download"){
                var key=['user', 'port', 'pwd', 'tool_path']
                for(i in key){
                    if(element.hasClass(key[i])){
                       download_file() 
                    }
                }
                attrs.$observe('class', function(){
                    var cls=element.attr('class')
                    if(cls=="user"||cls=="port"||cls=="pwd"||cls=="tool_path"){
                        download_file()
                    }
                })
            }
        }
    }
})
mainmodule.directive('resultbutton',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            
            element.click(function(){
                var id=element.attr('id')
                var trdm=element.parent().parent()
                var url='get_result_'+id
                var d={}
                
                if(id=="taskcustom"){
                    var task_id=trdm.find('.task_id').text().trim()
                    d['name']=task_id
                }else if(id=="fault"){
                    var remark=element.parent().parent().find('.remark').text().trim()
                    var dt={
                        'remark':{
                            'type':'textarea',
                            'name':'故障记录',
                            'des':'故障处理记录'
                        }
                    }
                    var context='<div class="ui segment">'+commservice.get_input_form("keyform", dt)+'</div>'
                    var md=angular.element(commservice.get_standard_modal('故障处理记录', context))
                    md.find('.remark').val(remark)
                    md.modal('show')
                    return false
                }else if(id=="collecttemplatehistory"){
                    var template_id=trdm.find('td.template_id').text().trim()
                    var tid=trdm.find('td.id').text().trim()
                    d['name']=template_id
                    d['id']=tid
                }
                commservice.request_url(url, 'post', d, function(dt){
                    commservice.alert_message(dt['code'], dt['message'], dt['status'])
                    if(dt['status']=="err"){
                        return false
                    }
                    if(id=="taskcustom"){
                        scope.$parent.getresult(id, dt['data'], task_id)
                    }else {
                        scope.$parent.getresult(id, dt['data'])
                    }
                })
            })
        }
    }
})
mainmodule.directive('getserversdata',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var line=element.attr('line')
            var product=element.attr('product')
            var app=element.attr('app')
            var group=element.attr('name')
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            
            setTimeout(function(){
                var task_name=scope.$parent.task_name
                var html='<repeatdataupdate id="taskservershistory" name="serverdetails" list="task.taskhistory.servers.'+line+'_and_'+product+'_and_'+app+'_and_'+group+'" ></repeatdataupdate>'
                compile(html)(scope.$parent)
                
                window.setInterval(function(){
                    compile(html)(scope.$parent)
                }, 6000)
            }, 30)
        }
    }
})
mainmodule.directive('taskservers',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            var task_name=element.attr('taskname')
            var sw=window.screen.width
            if(sw < 1400){
                element.find('.pusher').css('width', '81%')
            }
            scope.$parent.task_name=task_name
            element.height(document.body.clientHeight-180)
            commservice.request_url('task_servers_check', 'post', {task_name:task_name}, function(d){
                if(d['status']=='err'){
                    commservice.alert_message(d['status'], d['code'], d['message'], true)
                    return false
                }
                commservice.request_url('get_web_server_info', 'post', {}, function(url){
                    var url=url['url']
                    scope.$parent.taskwebsocket=commservice.web_socket(url, function(){
                        //on_open
                    },function(d){
                        //on_message
                        d=commservice.json_to_obj(d)
                        if(!(d instanceof Array)){
                            d=[d]
                        }
                        scope.$parent.task.taskhistory.tasklog.push.apply(scope.$parent.task.taskhistory.tasklog, d)
                        scope.$parent.$apply(scope.$parent.task.taskhistory.tasklog)
                    },function(){
                        //on_error
                    })
                })
            })
        }
    }
})
mainmodule.directive('newpage',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            var dt={}
            
            element.click(function(){
                var id=element.attr('id')
                if(id=="taskhistory"){
                    task_name=element.parent().parent().find('.task_name').text().trim()
                    commservice.open_page('get_task_servers_page?task_name='+task_name+'')
                }
            })
        }
    }
})
mainmodule.directive('trdeletebutton',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                var id=element.attr('id')
                var url="delete_"+id+"_info"
                var type=element.attr('name')
                var trdm=element.parent().parent()
                
                if(type=="logincheck"){
                    var url="logincheck_"+id
                    var des_key='检测'
                }else if(type=="status"){
                    var url="statuscheck_"+id
                    trdm=trdm.parent().parent()
                }else if(type=="deploy"){
                    var url="deploy_"+id
                    trdm=trdm.parent().parent()
                }else{
                    var des_key='删除'
                }
                var d={}
                
                if(id=="user"||id=="group"||id=="account"||id=="key"||id=="contact"||id=="assetmanager"||id=="loginmanager"||id=="serverapp"||id=="servergroup"||id=="groupmember"||id=="taskcustom"||id=="taskcustomfile"||id=="collecttemplate"||id=="collecttemplatehistory"||id=="taskrelevancehistory"||id=="taskhistory"||id=="serverprivilege"){
                    if(id=="assetmanager"||id=="loginmanager"){
                        var nid='td.telecom_ip'
                    }else if(id=="servergroup"){
                        var nid='td.group_id'
                    }else if(id=="taskhistory"){
                        var nid='td.task_name'
                        trdm=trdm.parent()
                    }else if(id=="serverprivilege"){
                        var nid='td.role'
                    }else if(id=="groupmember"){
                        var nid='td.member'
                    }else if(id=="taskcustom"||id=="taskcustomfile"){
                        var nid='td.task_id'
                    }else if(id=="collecttemplate"||id=="collecttemplatehistory"){
                        var nid='td.template_id' 
                    }else if(id=="taskrelevancehistory"){
                        var nid='td.relevance_id'
                    }else if(id=="serverapp"){
                        var nid='td.app'
                    }else{
                        var nid='td.name'
                    }
                    if(id=="servergroup"||id=="groupmember"){
                        d['id']=id
                        d['type']=type
                        d['line']=scope.$parent.breadcrumblist['line']['key']
                        d['product']=scope.$parent.breadcrumblist['product']['key']
                        d['app']=scope.$parent.breadcrumblist['app']['key']
                        if(scope.$parent.trdata['group_id']!=undefined){
                            d['group']=scope.$parent.trdata['group_id']
                        }else{
                            d['group']=scope.$parent.breadcrumblist['server']['key']
                        }
                        
                        var modal=trdm.find('td.modal').text().trim()
                        if(modal=="no"){
                            return scope.$parent.commservice.alert_message('warn', '检测/部署失败', "modal为no,若需要继续操作请先修改modal为yes")
                        }
                    }
                    var name=trdm.find(nid).text().trim().split('&')[0]
                    d['name']=name
                    if(id=="user"){
                        var message='确定删除用户  ['+name+"] 以及移除所在的组 ?"
                    }else if(id=="servergroup" && type =="status"){
                        var message='确定检测主机组  ['+name+"] 下的主机客户端状态,这可能需要一些时间 ?"
                    }else if(id=="servergroup" && type =="deploy"){
                        var message='确定对主机组  ['+name+"] 下的主机进行客户端部署操作,这可能需要一些时间 ?"
                    }else if(id=="serverprivilege"){
                        var message='确定删除规则  ['+name+"]?"
                        d['id']=trdm.find('td.id').text().trim()
                    }else if(id=="taskrelevancehistory"){
                        var message='确定删除关联任务  ['+name+"]?"
                    }else if(id=="taskhistory"){
                        var custom_name=trdm.find('td.custom_name').text().trim().split('&')[0]
                        if(custom_name){
                            name=name+"/"+custom_name
                        }
                        var message='确定修改任务  ['+name+"] 为完成状态?"
                    }else if(id=="servergroup"){
                        var message='确定删除主机组  ['+name+"] 以及移除主机组下的主机信息 ?"
                    }else if(id=="groupmember" && type =="status"){
                        var message='确定检测主机  ['+name+"] 客户端状态,这可能需要一些时间 ?"
                    }else if(id=="groupmember" && type =="deploy"){
                        var message='确定在主机  ['+name+"] 上部署客户端,这可能需要一些时间 ?"
                    }else if(id=="collecttemplatehistory"){
                        var message='确定删除信息收集记录 ['+name+"] ?"
                        d['id']=trdm.find('td.id').text().trim().split('&')[0]
                    }else if(id=="collecttemplate"){
                        var message='确定删除信息收集模板  ['+name+"]  以及当前模板下的所有记录?"
                    }else if(id=="groupmember"){
                        var message='确定删除主机成员  ['+name+"] ?"
                    }else if(id=="serverapp"){
                        var message='确定删除类型  ['+name+"] 以及移除类型下的主机组和主机信息 ?"
                    }else if(id=="group"){
                        var message='确定删除组  ['+name+"] 以及成员和权限信息?"
                    }else if(id=="account"){
                        var type=trdm.find('td.type').text().trim()
                        d['type']=type
                        if(type=="wechat"){
                            name=trdm.find('td.weid').text().trim()
                            d['name']=name
                            var message='确定删除wechat账号  ['+name+"] ?"
                        }else{
                            var message='确定删除email账号  ['+name+"] ?"
                        }
                    }else if(id=="key"){
                        var message='确定删除key  ['+name+"] ?"
                    }else if(id=="taskcustom"||id=='taskcustomfile'){
                        if(id=="taskcustomfile"){
                            var filename=trdm.find('.filename').text().trim()
                            d['type']='file'
                            d['filename']=filename
                            var message='确定删除任务文件  ['+filename+"] ?"
                            url="delete_taskcustom_info"
                        }else{
                            var message='确定删除任务信息  ['+name+"] ?"
                        }
                    }else if(id=="contact"){
                        var message='确定删除联系人 ['+name+"] ?"
                    }else if(id=="assetmanager"){
                        var message='确定删除ip为 ['+name+"] 的信息?"
                    }else if(id=="loginmanager"){
                        d['user']=trdm.find('td.user').text().trim().replace(/未设置/,'')
                        d['port']=trdm.find('td.port').text().trim().replace(/未设置/,'')
                        d['pwd']=trdm.find('td.pwd').text().trim().replace(/未设置/,'')
                        var message='确定'+des_key+'ip为 ['+name+"] 的登录信息?"
                    }
                }else if(id=="taskcustomhistory"){
                    var task_id
                    
                   
                }else if(id=="logindefault"||id=="logininit"||id=="logintools"||id=="logininitools"||id=="initoolsmanager"){
                    d['line']=trdm.find('td.line').text().trim()
                    d['product']=trdm.find('td.product').text().trim()
                    d['app']=trdm.find('td.app').text().trim()
                    d['idc']=trdm.find('td.idc').text().trim()
                    d['owner']=trdm.find('td.owner').text().trim()
                    d['user']=trdm.find('td.user').text().trim().replace(/未设置/,'')
                    d['port']=trdm.find('td.port').text().trim().replace(/未设置/,'')
                    d['pwd']=trdm.find('td.pwd').text().trim().replace(/未设置/,'')
                    d['tool_path']=trdm.find('td.tool_path').text().trim().replace(/未设置/,'')
                    if(id=="logininitools"){
                        var des="初始化"
                    }else if(id=="initoolsmanager"){
                        var des="服务器初始化工具"
                    }else{
                        var des="默认"
                    }
                    var message='是否'+des_key+' "'+d['line']+'产品线- '+d['product']+'业务- '+d['app']+'应用 -'+d['idc']+'机房 -'+d['owner']+'负责人" 的'+des+'登录信息?'
                }else{
                    scope.$parent.commservice.alert_message('err',id+""+des_key+"失败","获取ID失败")
                    return  false
                }

                if(id=="logindefault"||id=="logininit"||id=="logintools"||id=="loginmanager"||id=="logininitools"){
                    if(!d['user']||!d['port']||!d['pwd']){
                        scope.$parent.commservice.alert_message('warn',''+des_key+'登录信息失败',"未设置登录信息", true)
                        return  false
                    }
                }else if(id=="initoolsmanager" && !d['tool_path']){
                    scope.$parent.commservice.alert_message('warn',''+des_key+des+'失败',"未设置"+des+"", true)
                    return  false
                } 
                var loadinged=false
                var dm=angular.element(scope.$parent.commservice.get_confirm_modal('请确认',message,'ui small modal'))
                dm.modal('setting', 'onHidden', function(){
                    if(!loadinged){
                        element.removeClass('loading')
                    }
                }).modal('show')
                element.addClass('loading')
                dm.find('.actions').find('.negative.button').click(function(){
                    element.removeClass('loading')
                })
                dm.find('.actions').find('.right.button').click(function(){
                    loadinged=true
                    scope.$parent.commservice.request_url(url, 'post', d, function(dt){
                        element.removeClass('loading')
                        scope.$parent.commservice.alert_message(dt['status'],"code:"+dt['code'],dt['message'])
                        if(dt['status']=="err"){
                            return false
                        }
                        if(type=="logincheck"||type == "status" || type == "deploy"){
                            var data=dt['data']
                            	//var data=scope.$parent.commservice.json_to_obj(dt['data'])
                            scope.$parent.getresult(type, data)
                        }else{
                            if(id=="initoolsmanager"){
                                trdm.find('td.tool_path').text('未设置')
                            }else{
                                trdm.remove()
                                if(id=="serverapp"){
                                    var dt=scope.$parent.breadcrumblist
                                    var lfdm=angular.element('.leftdm div#line[name="'+dt['line']['key']+'"]').next().find('div#product[name="'+dt['product']['key']+'"]').next().find('div#app[name="'+name+'"]')
                                    lfdm.next().remove()
                                    lfdm.remove()
                                }else if(id=="servergroup"){
                                    var dt=scope.$parent.breadcrumblist
                                    var lfdm=angular.element('.leftdm div#line[name="'+dt['line']['key']+'"]').next().find('div#product[name="'+dt['product']['key']+'"]').next().find('div#app[name="'+dt['app']['key']+'"]')
                                    lfdm.next().find('a[name="'+name+'"]').remove()
                                }
                            }
                        }

                    }, function(){
                        scope.$parent.commservice.alert_message('err',"请求失败")
                        return false
                    })
                })
            })
        }
    }
})

mainmodule.directive('slider',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var trdm=element.parent().parent()
            var name=element.attr('name')
            if(name=="refreshpage"){
                var sw=window.screen.width
                if(sw < 1400){
                    element.parent().css('left', '65px')
                }
                element.checkbox('setting', 'onChange', function(){
                    if(element.checkbox('is checked')){
                        scope.$parent.taskhistory_refreshpage=true
                        var uphtm='<tbody name="taskhistory"  list="taskmanager.taskhistory.taskhistorylist.taskhistoryinfo" repeatdataupdate></tbody>'
                        scope.$parent.compile(uphtm)(scope.$parent)
                    }else{
                        scope.$parent.taskhistory_refreshpage=false
                    }
                })  
                element.checkbox('check')
                return false
            }
            if(scope.$parent.privilege.inform.slider_checked==true){
                element.find('input').prop('checked', true)
            }
            element.find('input').click(function(){
                var tdm=angular.element(event.target)
                var ret=tdm.prop('checked')
                var url=name+"slider_status_change"

                if(ret==true){
                    //一个类型的账号只允许开启一个,使用一个
                    var status="on"
                    if(name=="account"){
                        var type=trdm.find('td.type').text().trim()
                        if(type=="email"){
                            var account=trdm.find('td.name').text().trim()
                        }else if(type=="wechat"){
                            var account=trdm.find('td.weid').text().trim()
                        }
                        
                        var ddm=trdm.parent().find('td.type:contains('+type+')').parent()
                        ddm.find('td.status').text('off').css('color','red')
                        ddm.find('div[name="account"] input').prop('checked',false)
                        trdm.find('td.status').text('on').css('color','green')
                        tdm.prop('checked',ret)
                    }
                }else{
                    var status="off"
                    if(name=="account"){
                        var type=trdm.find('td.type').text().trim()
                        if(type=="email"){
                            var account=trdm.find('td.name').text().trim()
                        }else if(type=="wechat"){
                            var account=trdm.find('td.weid').text().trim()
                        }
                        trdm.find('td.status').text('off').css('color','red')
                    }
                }

                scope.$parent.commservice.request_url(url,'post',{type:type, name:account, status:status},function(d){
                    if(d['status']=="err"){
                        scope.$parent.commservice.alert_message(d['status'],d['code'],d['message'])
                        return false
                    }
                },function(){
                    scope.$parent.commservice.alert_message(d['status'],d['code'],d['message'])
                    return false
                })
            })
        }
    }
})

mainmodule.directive('opertiondialog',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var compile=scope.$parent.compile
            var commservice=scope.$parent.commservice
            element.click(function(){
                var id=element.attr('id')
                var fdm=element.parent().parent()
                var url='get_dialog_info_'+id
                var commiturl='commit_dialog_info_'+id
                
                if(id=="user"){
                    var title="组变更"
                    var child_title_left='所属组'
                    var child_title_right='组列表'
                    var name=fdm.find('td:eq(0)').text().trim()
                }else if(id=="group"){
                    var title="成员变更"
                    var child_title_left='成员信息'
                    var child_title_right='成员列表'
                    var name=fdm.find('td:eq(0)').text().trim()
                }else if(id=="serverprivilege"){
                    var title="主机组权限配置"
                    var child_title_left='权限信息'
                    var child_title_right='权限列表'
                    var name=fdm.find('td:eq(1)').text().trim()
                }else if(id=="privilege"){
                    var title="权限变更"
                    var child_title_left='权限信息'
                    var child_title_right='权限列表'
                    var name=fdm.find('td:eq(0)').text().trim()
                }else if(id=="account"){
                    var title="通知-账号管理"
                    var child_title_left='联系人成员'
                    var child_title_right='联系人列表'
                    var name=fdm.find('td:eq(1)').text().trim()
                }else{
                    return false
                }
                var dt={}
                if(id=="account"){
                    var type=fdm.find('td.type').text().trim()
                    dt['type']=type
                    
                    if(type=="email"){
                        name=fdm.find('td.name').text().trim()
                    }else if(type=="wechat"){
                        name=fdm.find('td.weid').text().trim()
                    }
                }else if(id=="serverprivilege"){
                    dt['id']=fdm.find('td.id').text().trim()
                }
                var d={title:title,left_title:child_title_left,right_title:child_title_right, type:id, name:name}
                dt['name']=name
                commservice.request_url('get_opertion_dialog.html',"post",d,function(d){
                    var md=angular.element(compile(d)(scope.$parent))
                    scope.$parent.dialogdata.left=[]
                    scope.$parent.dialogdata.leftkeyvalue=[]
                    scope.$parent.dialogdata.rightkeyvalue=[]
                    scope.$parent.dialogdata.right=[]
                    scope.$parent.dialogdata.rightcheckeddata=[]
                    scope.$parent.dialogdata.leftcheckeddata=[]
                    md.modal('show')
                    commservice.request_url(url,"post",dt,function(d){
                        if(id=="user"||id=="group"||id=="privilege"||id=="account"||id=="serverprivilege"){
                            scope.$parent.dialogdata.left=d['leftdata']
                            scope.$parent.dialogdata.right=d['rightdata']
                        }
                        md.find('div.middledata .button:eq(0)').click(function(){
                            var leftdata=scope.$parent.dialogdata.leftcheckeddata
                            if(leftdata.length!=0){
                                var rdm=md.find('div.rightdata')
                                for(i in leftdata){
                                        if(id=="user"||id=="privilege"){
                                            if(leftdata[i] in scope.$parent.dialogdata.left){
                                                delete scope.$parent.dialogdata.left[leftdata[i]]
                                            }
                                        }else if(id=="group"||id=="account"||id=="serverprivilege"){
                                            if(scope.$parent.dialogdata.left.indexOf(leftdata[i]) != -1){
                                                scope.$parent.dialogdata.left.splice(scope.$parent.dialogdata.left.indexOf(leftdata[i]), 1)  
                                            }
                                        }
                                        
                                        scope.$parent.dialogdata.leftkeyvalue.splice(scope.$parent.dialogdata.leftkeyvalue.indexOf(leftdata[i]), 1)
                                    
                                        //同下
                                    angular.forEach(rdm.find('input'), function(data){
                                        var tdm=angular.element(data)
                                        if(tdm.attr('name')==leftdata[i]){
                                            tdm.attr({
                                                "disabled":false,
                                                'checked':false
                                            })
                                        }
                                    })
                                    //leftdata.splice(leftdata.indexOf(leftdata[i]),1)    
                                }
                                scope.$parent.$apply()
                            }
                        })
                        md.find('div.middledata .button:eq(1)').click(function(){
                            var rightdata=scope.$parent.dialogdata.rightcheckeddata    
      
                            if(rightdata.length!=0){
                                var rdm=md.find('div.rightdata')
                                var rrdm=''
                                for(i in rightdata){
                                    if(id=="user"){
                                        scope.$parent.dialogdata.left[rightdata[i]]=scope.$parent.dialogdata.right[rightdata[i]]
                                    }else if(id=="privilege"){
                                        var tk=rightdata[i]
                                        rrdm=md.find('.rightdata').find('input[name="'+tk+'"]')

                                        if(rrdm.parent().is('#father')){
                                            var tv=scope.$parent.dialogdata.right[rightdata[i]]['des']
                                        }else if(rrdm.parent().is('#child')){
                                            var pname=rrdm.parent().parent().parent().parent().parent().parent().prev().find('input').attr('name')
                                            var tv=scope.$parent.dialogdata.right[pname]['childlist'][rightdata[i]]
                                        }

                                        scope.$parent.dialogdata.left[tk]=tv

                                    }else if(id=="group"||id=="account"||id=="serverprivilege"){
                                        scope.$parent.dialogdata.left.push(rightdata[i])
                                    }

                                    // 触发dialogrightcheck 监听的left失败,angular bug,原因未知,使用jq
                                    angular.forEach(rdm.find('input'), function(data){
                                        var tdm=angular.element(data)
                                        if(tdm.attr('name')==rightdata[i]){
                                            tdm.attr({
                                                "disabled":true,
                                                'checked':true
                                            })
                                        }
                                    })
                                    //rightdata.splice(rightdata.indexOf(rightdata[i]),1)
                                }
                                scope.$parent.$apply()
                            }
                        })
                        md.find('div.actions div.right.button').click(function(){
                            //是原始值 leftkeyvalue
                            var d={}
                            d['data']=scope.$parent.dialogdata.leftkeyvalue
                            d['name']=name
                            if(id=="account"){
                                d['type']=type
                            }else if(id=="serverprivilege"){
                                d['id']=dt['id']
                            }
                            commservice.request_url(
                                commiturl, 
                                'post', 
                                d, 
                                function(dt){
                                    commservice.alert_message(dt['status'],dt['code'], dt['message'])
                                },function(){
                                
                            })
                        })
                        
                    },function(){
                        commservice.alert_message('err','请求失败')
                    })
                })
            })
        }
    }
})

mainmodule.directive('dialogrightcheck',function(){
    return {
        scope:{
            left:'='
        },
        restrict:'A',
        link:function(scope, element, attrs){
            attrs.$observe('left',function(value){
                //右边监听左边
                var name=element.attr('name')
                var pdm=element.parent()
                
                for(i in scope.$parent.dialogdata.leftkeyvalue){
                    if(scope.$parent.dialogdata.leftkeyvalue[i] == name){
                        element.prop({
                            'checked':true,
                            'disabled':true
                        })
                        if(pdm.is('#child')){
                            pdm.parent().parent().parent().parent().parent().prev().find('label').css('color', 'red')
                        }
                        scope.$parent.dialogdata.rightkeyvalue.splice(scope.$parent.dialogdata.rightkeyvalue.indexOf(scope.$parent.dialogdata.leftkeyvalue[i]),1)
                    }
                }
            })
        }
    }
})
mainmodule.directive('dialogleftcheck',function(){
    return {
        scope:{
            right:'='
        },
        restrict:'A',
        link:function(scope, element, attrs){
             //左边监听右边
            attrs.$observe('right',function(){
                var name=element.attr('name')

            })
        }
    }
})
mainmodule.directive('leftchecked',function(){
    return {
        scope:{
            right:'='
        },
        restrict:'A',
        link:function(scope, element, attrs){
            element.prev().click(function(){
                var dm=element.prev()
                var name=dm.attr("name")
                var id=dm.attr('id')
                if(dm.prop('checked')==true){
                    if(scope.$parent.dialogdata.leftcheckeddata.indexOf(name)==-1){
                        scope.$parent.dialogdata.leftcheckeddata.push(name)
                    }
                }else{
                    if(scope.$parent.dialogdata.leftcheckeddata.indexOf(name)!=-1){
                        scope.$parent.dialogdata.leftcheckeddata.splice(scope.$parent.dialogdata.leftcheckeddata.indexOf(name), 1)
                    }
                }
            })
        }
    }
})
mainmodule.directive('rightchecked',function(){
    return {
        scope:{
            right:'='
        },
        restrict:'A',
        link:function(scope, element, attrs){
            element.prev().click(function(){
                var dm=element.prev()
                var name=dm.attr("name")
                var id=dm.attr('id')
                
                var pdm=element.parent()
                
                scope.addv=function(n){
                    if(scope.$parent.dialogdata.rightcheckeddata.indexOf(n)==-1){
                        scope.$parent.dialogdata.rightcheckeddata.push(n)
                    }
                }
                scope.removev=function(nn){
                    if(scope.$parent.dialogdata.rightcheckeddata.indexOf(nn)!=-1){
                        scope.$parent.dialogdata.rightcheckeddata.splice(scope.$parent.dialogdata.rightcheckeddata.indexOf(nn), 1)
                    }
                }
                if(dm.prop('checked')==true){
                    if(pdm.is('#father')){
                        scope.addv(name)
                        angular.forEach(pdm.parent().next().find('div.item'), function(d){
                            var tttd=angular.element(d)
                            var nnn=tttd.find('#child input').attr('name')
                            if(!tttd.find('#child input').prop('disabled')){
                                tttd.find('#child input').prop('checked', true)
                            }
                            scope.addv(nnn)
                        })
                    }else{
                        scope.addv(name)
                    }
                }else{
                    if(pdm.is('#father')){
                        scope.removev(name)
                        angular.forEach(pdm.parent().next().find('div.item'), function(d){
                            var tttd=angular.element(d)
                            var nnn=tttd.find('#child input').attr('name')
                            if(!tttd.find('#child input').prop('disabled')){
                                tttd.find('#child input').prop('checked', false)
                            }
                            scope.removev(nnn)
                        })
                    }else{
                        scope.removev(name)
                    }
                }
            })
        }
    }
})
mainmodule.directive('calladdinfo',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            scope.input_del=function(dom){
                dom.find('button#labledel').click(function(){
                    var tdm=angular.element(event.target)
                    var ppm=tdm.parent().parent().parent()
                    if(tdm.is('i')){
                        ppm=ppm.parent()
                    }
                    var ptm=ppm.parent()
                    var index=1
                    ppm.remove()
                    
                    angular.forEach(ptm.find('input:not(input[name="addlabel"],input[name="clonelabel"])'), function(data){
                        var tttt=angular.element(data)
                        var ppm=tttt.parent().parent().parent()
                        var ln="label"+index
                        ppm.find('label').text(ln)
                        ppm.find('input').attr('name', ln)
                        index+=1
                       
                    })
                    
                })
            }
            if(id=="memberlabel"){
                element.click(function(){
                    var dm=element.parent().parent()
                    var ip=dm.find('.member').text().trim().split('&')[0]
                    var data=scope.$parent.breadcrumblist
                    commservice.request_url('get_memberlabel', 'post', {line:data['line']['key'], product:data['product']['key'], app:data['app']['key'], group:data['server']['key'], member:ip}, function(d){
                        var title='主机成员标签管理['+ip+']'
                        var md=angular.element(compile(commservice.get_standard_modal(title, d))(scope))
                        md.modal('show')
                        scope.input_del(md)
                        md.find("#lableadd").click(function(){
                            var tdm=angular.element(event.target)
                            var pdm=tdm.parent().parent().parent()
                            if(tdm.is('i')){
                                pdm=pdm.parent()
                            }
                            var ndm=pdm.prev().clone()
                            var len=md.find('input:not(input[name="addlabel"],input[name="clonelabel"])').length
                            ndm.find('label').text('lable'+(Number(len) + 1))
                            ndm.css('display', 'block').find('input').attr('name', 'lable'+(Number(len) + 1))
                            pdm.prev().before(ndm)
                            scope.input_del(ndm)
                            md.modal('refresh')
                        })
                        md.find('.actions div:eq(1)').click(function(){
                            var dd={}
                            angular.forEach(md.find('input:not(input[name="addlabel"],input[name="clonelabel"])'), function(data){
                                var tdm=angular.element(data)
                                var id=tdm.attr('name')
                                var value=tdm.val()
                                if (value){
                                    dd[id]=value
                                }
                            })
                            if(commservice.isempty(dd)){
                                return false
                            }
                            var ddt={}
                            ddt['line']=data['line']['key']
                            ddt['product']=data['product']['key']
                            ddt['app']=data['app']['key']
                            ddt['group']=data['server']['key']
                            ddt['member']=ip
                            ddt['lable']=dd
                            commservice.request_url('serverhost_addlable', 'post', {data:ddt}, function(tt){
                                if(tt['status']=="err"){
                                    commservice.alert_message(tt['status'],"code:"+tt['code'],tt['message'])
                                }
                            })
                        })
                    })
                })
            }
        }
    }
})
mainmodule.directive('getdropmen',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            var url="get_dropmenu_"+id
            var commservice=scope.$parent.commservice
            if(id=="informationcollect"){
                element.click(function(){
                    delete window.sessionStorage[url]
                    element.find('div.dropdown').dropdown({
                        allowAdditions: true,
                        apiSettings: {
                            url: url
                        }
                    })
                })
            }
            element.find('div.dropdown').dropdown({
                onAdd:function(){
                    element.find('div.dropdown').dropdown('refresh')
                }
            })
        }
    }
})
mainmodule.directive('modalhidden',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.modal('setting', 'onHidden', function(){
                element.remove()
            })
        }
    }
})
mainmodule.directive('checkbox',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            var commservice=scope.$parent.commservice
            
            
            element.checkbox()
            if(id=="taskrelevance"){
                if(typeof scope.$parent.task.taskcreate.relevance.relevancelist=='string'){
                    scope.$parent.task.taskcreate.relevance.relevancelist=[]
                }
                if(typeof scope.$parent.task.taskcreate.relevance.relevancechecklist=='string'){
                    scope.$parent.task.taskcreate.relevance.relevancechecklist=[]
                }

                element.checkbox('setting', 'onChecked' ,function(){
                    var trdm=element.parent().parent()
                    var file=trdm.find('.filename').text().trim()
                    var name=trdm.find('.des').text().trim()
                    var taskid=trdm.find('.task_id').text().trim()
                    var index=scope.$parent.task.taskcreate.relevance.relevancechecklist.indexOf(taskid)
                    var tdd={}
                    tdd['task_id']=taskid
                    tdd['filename']=file
                    tdd['des']=name
                    tdd['prepro']='no'
                    tdd['isexcute']='yes'
                    tdd['scope']='all'
                    tdd['preprotime']=''
                    tdd['preprofile']=''
                    tdd['collecttemplate']=''
                    tdd['preprotype']=''
                    tdd['id']=scope.$parent.task.taskcreate.relevance.relevancelist.length+1
                    
                    if(file==""||name==""){
                        commservice.alert_message('err', '选择失败', '无文件/名称信息', true)
                        element.checkbox('uncheck')
                        return false
                    }
    
                    if(index==-1){
                        scope.$parent.task.taskcreate.relevance.relevancelist.push(tdd)
                        scope.$parent.task.taskcreate.relevance.relevancechecklist.push(taskid)
                        scope.$parent.$apply()
                    }
                })
                element.checkbox('setting', 'onUnchecked' ,function(){
                    var trdm=element.parent().parent()
                    var file=trdm.find('.filename').text().trim()
                    var name=trdm.find('.des').text().trim()
                    var taskid=trdm.find('.task_id').text().trim()

                    if(scope.$parent.task.taskcreate.relevance.preproid!=""){
                        scope.$parent.recover()
                    }
                    var index=scope.$parent.task.taskcreate.relevance.relevancechecklist.indexOf(taskid)

                    if(index!=-1){
                        scope.$parent.task.taskcreate.relevance.relevancelist.splice(index, 1)
                        scope.$parent.task.taskcreate.relevance.relevancechecklist.splice(index, 1)
                        scope.$parent.idchange()
                        scope.$parent.$apply()
                    }
                })

            }

        }
    }
})
mainmodule.directive('taskrelevance',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.find('div.dropdown').dropdown()
            var pdm=element.parent()
            var fdm=element.find('.opertion > .buttons:eq(0) .buttons:eq(0)')
            var cdm=element.find('.opertion > .buttons:eq(0) .buttons:eq(1)')
            var prdm=element.find('.opertion > .buttons:eq(1)')
            var cfgdm=element.find('td.relevanceconfig .form .fields')
            scope.$parent.preproset=function(a){
                var trl=pdm.find('tr')

                if(a==undefined){
                    trl.find('.opertion > .buttons:eq(0) .buttons:eq(1)').find('button:eq(1)').prop('disabled', true)
                }else{
                    trl.find('.opertion > .buttons:eq(0) .buttons:eq(1)').find('button:eq(1)').prop('disabled', false)
                }
            }
            scope.$parent.stset=function(){
                var trl=pdm.find('tr[prepro="no"]')

                trl.find('.opertion > .buttons:eq(0) .buttons:eq(0)').find('button:eq(0)').prop('disabled', false)
                trl.find('.opertion > .buttons:eq(0) .buttons:eq(0)').find('button:eq(1)').prop('disabled', false)
                trl.slice(0,1).find('.opertion > .buttons:eq(0) .buttons:eq(0) button:eq(0)').prop('disabled', true)
                trl.slice(-1).find('.opertion > .buttons:eq(0) .buttons:eq(0) button:eq(1)').prop('disabled', true)
            }

            setTimeout(function(){
                scope.$parent.stset()
                var tttd=Number(element.find('td.id').text().trim())-1
                cfgdm.find('.field:eq(0) div.checkbox').checkbox('setting', 'onChange' ,function(){
                    //是否执行
                    var isexcute=cfgdm.find('.field:eq(0) input').prop('checked')
                    if(isexcute){
                        isexcute="yes"
                    }else{
                        isexcute='no'
                    }
                    scope.$parent.task.taskcreate.relevance.relevancelist[tttd]['isexcute']=isexcute
                })
                cfgdm.find('.field:eq(1) .dropdown').dropdown('setting', 'onChange' ,function(){
                    //信息收集
                    var collecttemplate=cfgdm.find('.field:eq(1) .dropdown').dropdown('get value')[0]
                    scope.$parent.task.taskcreate.relevance.relevancelist[tttd]['collecttemplate']=collecttemplate
                })
                cfgdm.find('.field:eq(2) .dropdown').dropdown('setting', 'onChange' ,function(){
                    //执行范围
                    var tscope=cfgdm.find('.field:eq(2) .dropdown').dropdown('get value')[0]
                    scope.$parent.task.taskcreate.relevance.relevancelist[tttd]['scope']=tscope
                })
                cfgdm.find('.field:eq(3) input').keyup(function(){
                    //预处理执行时间
                    var preprotime=angular.element(event.target).val()
                    scope.$parent.task.taskcreate.relevance.relevancelist[tttd]['preprotime']=preprotime
                })
                cfgdm.find('.field:eq(4) input').keyup(function(){
                    //推送文件
                    var preprofile=angular.element(event.target).val()
                    scope.$parent.task.taskcreate.relevance.relevancelist[tttd]['preprofile']=preprofile
                })
            }, 50)

            cdm.find('button:eq(0)').click(function(){
                //删除
                var id=Number(element.find('td.id').text().trim())
                var taskid=element.find('td.task_id').text().trim()
                pdm=element.parent()
                var index=scope.$parent.task.taskcreate.relevance.relevancechecklist.indexOf(taskid)
                if(index!=-1){
                    scope.$parent.task.taskcreate.relevance.relevancechecklist.splice(index, 1)
                }
                scope.$parent.task.taskcreate.relevance.relevancelist.splice(id-1, 1)
                scope.$parent.idchange(id)
                scope.$parent.$apply()
                scope.$parent.stset()
            })
            prdm.find('.buttons:eq(1) button:eq(0)').click(function(){
                //处理推送文件删除
                var tid=Number(element.find('td.id').text().trim()) - 1
                pdm=element.parent()

                scope.$parent.task.taskcreate.relevance.preprolist.splice(tid, 1)
                scope.$parent.task.taskcreate.relevance.relevancelist.splice(tid, 1)
                scope.$parent.idchange()
                scope.$parent.$apply()
            })
            prdm.find('button:eq(1)').click(function(){
                //添加预处理推送文件
                pdm=element.parent()
                var tlen=scope.$parent.task.taskcreate.relevance.preprolist.length
                var ttid=scope.$parent.task.taskcreate.relevance.preproid
                var tl={}
                tl['task_id']=''
                tl['filename']='推送文件'+tlen
                tl['des']='预处理文件'
                tl['prepro']='yes'
                tl['id']=tlen
                tl['preprotype']='slave'
                tl['isexcute']='yes'
                tl['scope']='all'
                tl['preprotime']=''
                tl['preprofile']=''
                tl['collecttemplate']=''

                scope.$parent.task.taskcreate.relevance.relevancelist.splice(tlen, 0, tl)
                scope.$parent.task.taskcreate.relevance.preprolist.push(tlen)
                scope.$parent.idchange()
                scope.$parent.$apply()
            })
            prdm.find('button:eq(0)').click(function(){
                //取消预处理
                pdm=element.parent()
                var tid=element.find('td.id').text().trim()
                var ttid=scope.$parent.task.taskcreate.relevance.preproid
                var ttlist=scope.$parent.task.taskcreate.relevance.preprolist
                var tl=''

                if(element.attr('prepro')!="yes"&&tid!=1&&ttid==""){
                    return false
                }
                scope.$parent.recover()
                scope.$parent.idchange()
                scope.$parent.$apply()
                setTimeout(function(){
                    scope.$parent.stset()
                    scope.$parent.preproset('recover')
                }, 200)
            })
            cdm.find('button:eq(1)').click(function(){
                //预处理
                var tdm=angular.element(event.target)
                var id=Number(element.find('td.id').text().trim())
                pdm=element.parent()
                if(tdm.is(':disabled')){
                    return false
                }
                scope.$parent.task.taskcreate.relevance.prepro='yes'
                scope.$parent.commservice.alert_message('warn', '提示', '你设置了预处理任务,请对预处理任务进行配置', true)
                scope.$parent.task.taskcreate.relevance.preproid=id-1
                var tv=scope.$parent.task.taskcreate.relevance.relevancelist[id-1]
                tv['id']=1
                tv['prepro']='yes'
                tv['preprotype']='master'

                scope.$parent.task.taskcreate.relevance.preprolist.push(0)
                scope.$parent.task.taskcreate.relevance.relevancelist.splice(id-1, 1)
                scope.$parent.task.taskcreate.relevance.relevancelist.splice(0, 0, tv)
                scope.$parent.idchange()
                scope.$parent.$apply()

                setTimeout(function(){
                    scope.$parent.stset()
                    scope.$parent.preproset()
                }, 200)
            })
            fdm.find('button:eq(0)').click(function(){
                var id=Number(element.find('td.id').text().trim())
                var tdm=angular.element(event.target)
                pdm=element.parent()
                
                if(tdm.is(':disabled')){
                    return false
                }

                var ttinfo=scope.$parent.task.taskcreate.relevance.relevancelist[id-1]
                var rtinfo=scope.$parent.task.taskcreate.relevance.relevancelist[id-2]
                scope.$parent.task.taskcreate.relevance.relevancelist[id-2]['id']=id-2
                scope.$parent.task.taskcreate.relevance.relevancelist[id-2]=ttinfo
                scope.$parent.task.taskcreate.relevance.relevancelist[id-1]['id']=id-1
                scope.$parent.task.taskcreate.relevance.relevancelist[id-1]=rtinfo
                scope.$parent.idchange()
                scope.$parent.$apply()
                setTimeout(function(){
                    scope.$parent.stset()
                }, 200)
            })
            fdm.find('button:eq(1)').click(function(){
                var id=Number(element.find('td.id').text().trim())
                var tdm=angular.element(event.target)
                pdm=element.parent()
                
                if(tdm.is(':disabled')){
                    return false
                }
                var ttinfo=scope.$parent.task.taskcreate.relevance.relevancelist[id-1]
                var rtinfo=scope.$parent.task.taskcreate.relevance.relevancelist[id]
                scope.$parent.task.taskcreate.relevance.relevancelist[id-1]['id']=id-1
                scope.$parent.task.taskcreate.relevance.relevancelist[id-1]=rtinfo
                scope.$parent.task.taskcreate.relevance.relevancelist[id]['id']=id
                scope.$parent.task.taskcreate.relevance.relevancelist[id]=ttinfo
                scope.$parent.idchange()
                scope.$parent.$apply()
                setTimeout(function(){
                    scope.$parent.stset()
                }, 200)
            })
        }
    }
})
mainmodule.directive('accordion',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.accordion({selector: {trigger: '.title'}})
        }
    }
})
mainmodule.directive('relevancecontent',function(){
    //ng-repeat3层嵌套没效果,指令来实现
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            attrs.$observe('name', function(){
                var td=scope.$parent.task.taskcreate.relevancehistory
                var trdmu=angular.element('.ui.taskrelevance.left.sidebar.menu')
                var srdmu=angular.element('.ui.servergroup.left.sidebar.menu')
                var pusher=angular.element('.ui.bottom.pushable .pusher')
                var html=''
                
                var name=element.attr('name')
                var ddd=td[name]['type']
                var html='<div class="content">'

                for(i in ddd){
                    html+='<div class="accordion"><div name="'+i+'"  id="relevancetype" class="title bread active"><i class="dropdown icon"></i>'+ddd[i]['des']+'</div><div class="content active"><div class="ui fluid massive secondary vertical pointing text menu transition visible" style="padding-left:2.5em !important">'
                    for(k in ddd[i]['tasklist']){
                        html+='<a id="relevance" class="item bread" name="'+k+'" prepro="'+ddd[i]['tasklist'][k]['prepro']+'" secondarymenu>'+ddd[i]['tasklist'][k]['des']+'</a>'
                    }
                    html+='</div></div></div>'
                }
                html+="</div>"
                element.after(scope.$parent.compile(html)(scope.$parent))
                trdmu.find('.secondary.vertical.menu').find('a').click(function(){
                    var tdddm=angular.element(event.target)
                    scope.$parent.task.groupselect={}
                    scope.$parent.task.groupselect.taskname=tdddm.attr('name')
                    scope.$parent.task.groupselect.prepro=tdddm.attr('prepro')
                    scope.$parent.task.groupselect.tasktypecustom=''
                    scope.$parent.task.groupselect.taskalias=''
                    scope.$parent.task.groupselect.executetime=''
                    scope.$parent.task.groupselect.grouplist={}
                    
                    srdmu.sidebar({context: '.ui.bottom.pushable', 'closable':false}).sidebar('show')
                    trdmu.sidebar('hide')
                    pusher.removeClass('dimmed')
                })
                srdmu.find('.taskback .link').unbind('click').click(function(){
                    trdmu.sidebar({context: '.ui.bottom.pushable', 'closable':false}).sidebar('show')
                    srdmu.sidebar('hide')
                    pusher.addClass('dimmed')
                    pusher.css('margin-left','14%')
                })
                scope.$parent.relevancebreadcrumbset(trdmu, '')
            })
        }
    }
})
mainmodule.directive('setvalue',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var a=attrs.$observe('key',function(){
                var id=element.attr('id')
                var key=element.attr('key')

                if(element.is('.input')){
                    element.find('input').val(key)
                }else if(element.is('.search.selection.dropdown')){
                    setTimeout(function(){
                        element.dropdown('set selected', key)
                    }, 30)
                    
                }else if(element.is('.checkbox')){
                    if(key=="yes"){
                        var k='check'
                    }else{
                        var k='uncheck'
                    }
                    element.checkbox(k)
                }
                a()
            })
        }
    }
})
mainmodule.directive('dotaskrelevance',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            element.unbind('click').click(function(){
                var url='get_taskrelevance'
                var url1='get_ngrepeat_data_collecttemplatelist'
                var url2='get_relevance_accountfilter'
                var tasktype=element.attr('tasktype')
                commservice.request_url(url1, 'post', {}, function(d){
                    scope.$parent.task.taskcreate.relevance.relevancecollect=d
                })
                commservice.request_url(url2, 'post', {type:'app'}, function(dd){
                    scope.$parent.task.taskcreate.relevance.relevanceapplist=dd
                })
                scope.$parent.task.taskcreate.relevance.title='任务关联'
                scope.$parent.task.taskcreate.relevance.relevanceapp=''
                scope.$parent.task.taskcreate.relevance.relevanceappdes=''
                scope.$parent.task.taskcreate.relevance.relevancetype='all'
                scope.$parent.task.taskcreate.relevance.relevancetypedes='通用任务'
                scope.$parent.task.taskcreate.relevance.relevanceid=''
                scope.$parent.task.taskcreate.relevance.relevancename=''
                scope.$parent.task.taskcreate.relevance.relevanceremark=''
                scope.$parent.task.taskcreate.relevance.relevancerely='no'
                scope.$parent.task.taskcreate.relevance.relevancepath='/tmp/${relevance_id}/${task_name}/'
                scope.$parent.task.taskcreate.relevance.relevancelist=[]
                scope.$parent.task.taskcreate.relevance.relevancechecklist=[]
                scope.$parent.task.taskcreate.relevance.prepro='no'
                //预处理id;relevancelist的下标信息
                scope.$parent.task.taskcreate.relevance.preproid=''
                //prepro任务所在relevancelist的下标信息
                scope.$parent.task.taskcreate.relevance.preprolist=[]
            
                commservice.request_url(url, 'post', {}, function(html){
                    var md=angular.element(compile(html)(scope.$parent))
                    md.find('input.check').keyup(function(){
                        scope.$parent.input_check()
                    })
                    scope.$parent.task.taskcreate.relevance.dotype=''
                    md.find('div.dropdown').dropdown()

                    if(tasktype=="update"){
                        scope.$parent.task.taskcreate.relevance.dotype='update'
                        setTimeout(function(){
                            scope.$parent.task.taskcreate.relevance.title='任务关联详情['+scope.$parent.trdata['relevance_id']+']'
                            commservice.request_url('get_task_relevance_history', 'post', {name:scope.$parent.trdata['relevance_id'], type:tasktype}, function(upd){
                                if(!upd||upd.length==0){
                                    commservice.alert_message('err', '获取关联任务信息失败', '可以刷新页面重试', true)
                                    return false
                                }
                                //还原任务关联信息
                                var tdd=upd[0]
                                scope.$parent.task.taskcreate.relevance.relevanceapp=tdd['relevance_app']
                                angular.element('div#relevanceapp div.dropdown').dropdown('set selected', tdd['relevance_app'])
                                scope.$parent.task.taskcreate.relevance.relevanceappdes=tdd['relevance_app_des']
                                scope.$parent.task.taskcreate.relevance.relevancetype=tdd['relevance_type']
                                angular.element('div#relevancetype div.dropdown').dropdown('set selected', tdd['relevance_type'])
                                scope.$parent.task.taskcreate.relevance.relevancetypedes=tdd['relevance_type_des']
                                scope.$parent.task.taskcreate.relevance.relevanceid=tdd['relevance_id']
                                angular.element('div#relevanceid input').prop('disabled', true)
                                scope.$parent.task.taskcreate.relevance.relevancename=tdd['relevance_name']
                                scope.$parent.task.taskcreate.relevance.relevanceremark=tdd['relevance_remark']
                                scope.$parent.task.taskcreate.relevance.relevancerely=tdd['relevance_rely']
                                if(tdd['relevance_rely']=="yes"){
                                    angular.element('div#relevancerely').checkbox('check')
                                }else if(tdd['relevance_rely']=="no"){
                                    angular.element('div#relevancerely').checkbox('uncheck')
                                }

                                if(tdd['relevance_path']){
                                    scope.$parent.task.taskcreate.relevance.relevancepath=tdd['relevance_path']
                                }
                                scope.$parent.task.taskcreate.relevance.relevancelist=[]
                                var isprepro="no"
                                var taskinfo=commservice.json_to_obj(tdd['task_list'])
                                var tdd={}
                                for(i in taskinfo['relevancelist']){
                                    var ttt=taskinfo['relevancelist'][i]
                                    tdd={}
                                    tdd['task_id']=ttt['task_id']
                                    tdd['filename']=ttt['filename']
                                    tdd['des']=ttt['des']
                                    tdd['prepro']=ttt['prepro']
                                    if(ttt['prepro']=="yes"){
                                        var isprepro="yes"
                                    }
                                    tdd['isexcute']=ttt['isexcute']
                                    tdd['scope']=ttt['scope']
                                    tdd['preprotime']=ttt['preprotime']
                                    tdd['preprofile']=ttt['preprofile']
                                    tdd['collecttemplate']=ttt['collecttemplate']
                                    tdd['preprotype']=ttt['preprotype']
                                    tdd['id']=ttt['id']

                                    scope.$parent.task.taskcreate.relevance.relevancelist.push(tdd)
                                    scope.$parent.task.taskcreate.relevance.relevancechecklist.push(ttt['task_id'])
                                }

                                scope.$parent.task.taskcreate.relevance.prepro=isprepro
                                //预处理id;relevancelist的下标信息;update时候无预处理任务id
                                scope.$parent.task.taskcreate.relevance.preproid=''
                                //prepro任务所在relevancelist的下标信息
                                scope.$parent.task.taskcreate.relevance.preprolist=taskinfo['preprolist']
                            })
                        }, 20)
                    }
                    md.find('div#relevanceapp .search').keyup(function(){
                        var ttm=angular.element(event.target)
                        var tvl=ttm.val()
                        if(tvl==""){
                            md.find('div#relevancedes').hide()
                            return false
                        }
                        var tm='<div class="item custom" data-value="'+tvl+'">'+tvl+'</div>'
                        md.find('div#relevanceapp .menu').find('.custom').remove()
                        md.find('div#relevanceapp .dropdown .menu .item:eq(0)').before(tm)
                        md.find('div#relevanceapp .dropdown').dropdown('set value', tvl)
                        md.find('div#relevanceapp .dropdown').dropdown('set text', tvl)
            
                        var check=md.find('div#relevanceapp .menu').find('div[data-value="'+tvl+'"]')
            
                        if(check.hasClass('custom')&&tvl!=""){
                            md.find('div#relevancedes').show()
                        }else{
                            md.find('div#relevancedes').hide()
                        }
                    })
            
                    md.find('div#relevancedes input').keyup(function(){
                        var ttm=angular.element(event.target)
                        var tvl=ttm.val()
                        scope.$parent.task.taskcreate.relevance.relevanceappdes=tvl
                    })
                    md.find('div#relevancepath button').click(function(){
                        var ttm=angular.element(event.target)
                        if(ttm.is('i')){
                            ttm=ttm.parent()
                        }
                        if(ttm.prev().is(':disabled')){
                            ttm.prev().prop('disabled', false)
                            ttm.find('i').removeClass('edit checkmark')
                            ttm.find('i').addClass('checkmark')
                        }else{
                            ttm.prev().prop('disabled', true)
                            ttm.find('i').removeClass('edit checkmark')
                            ttm.find('i').addClass('edit')
                        }
                    })
            
                    md.find('div#relevancerely.checkbox').checkbox('setting', 'onUnchecked' ,function(){
                        scope.$parent.task.taskcreate.relevance.relevancerely='no'
                    })
                    md.find('div#relevancerely.checkbox').checkbox('setting', 'onChecked' ,function(){
                        scope.$parent.task.taskcreate.relevance.relevancerely='yes'
                        commservice.alert_message('warn', "注意", "你开启了任务依赖,主机所有任务将串行执行",  true)
                    })

                    md.find('div#relevancetype div.dropdown').dropdown('setting', 'onChange', function(){
                        var ttm=md.find('div#relevancetype div.dropdown')
                        var ttp=ttm.dropdown('get value')
                        var ttpdes=ttm.dropdown('get text')
                        scope.$parent.task.taskcreate.relevance.relevancetype=ttp
                        scope.$parent.task.taskcreate.relevance.relevancetypedes=ttpdes
                    })  

                    md.find('div#relevanceapp.menu div:not(.message)').click(function(){
                        var ttm=angular.element(event.target)
                        var app=ttm.attr('data-value')
                        var appdes=ttm.text().trim()
                        scope.$parent.task.taskcreate.relevance.relevanceapp=app
                        scope.$parent.task.taskcreate.relevance.relevanceappdes=appdes
                    })
                    
                    setTimeout(function(){
                        md.find('div.dropdown').dropdown('hide')
                        md.find('div#relevanceapp .dropdown').dropdown('setting', 'onChange', function(){
                            var tvl=md.find('div#relevanceapp .dropdown').dropdown('get value')[0]
                            var des=md.find('div#relevanceapp .dropdown').dropdown('get text')[0]
            
                            scope.$parent.task.taskcreate.relevance.relevanceapp=tvl
                            scope.$parent.task.taskcreate.relevance.relevanceappdes=des
                        })
                    },300) 
                    md.modal('show')
            
                    md.find('.actions .button:eq(1)').click(function(){
                        var ddd=scope.$parent.task.taskcreate.relevance
                        var message=''
                        if(ddd['relevanceapp']==""||ddd['relevanceappdes']==""){
                            message="任务分类填写不完整"
                        }
                        if(ddd['relevanceid']==""||ddd['relevancename']==""){
                            message="任务id/名称填写不完整"
                        }
                        if(ddd['relevancelist'].length==0){
                            message="未关联任务"
                        }
                        if(ddd['prepro']=="yes"){
                            if(ddd['preprolist'].length==0){
                                message="获取预处理任务信息失败"
                            }else{
                                for(i in ddd['preprolist']){
                                    if(i==0&&ddd['relevancelist'][i]['preprotime']==""){
                                        message="预处理任务先于任务执行时间为空"
                                    }else if(i!=0&&ddd['relevancelist'][i]['preprofile']==""){
                                        message="预处理任务推送文件链接填写不完整"
                                    }
                                }
                            }
                        }
                        
                        if(message!=""){
                            commservice.alert_message('err', '提交失败', message, true)
                            return false
                        }
                        delete ddd['relevanceapplist']
                        delete ddd['relevancecollect']
                        delete ddd['title']

                        commservice.request_url('task_relevance', 'post', ddd, function(ttd){
                            commservice.alert_message(ttd['status'], ttd['code'], ttd['message'])
                            if(ttd['status']=="err"){
                                return false
                            }

                            html='<tbody name="relevancehistory" list="task.taskcreate.relevancehistory" repeatdataupdate>'
                            compile(html)(scope.$parent)
                            
                            var upd='<tbody name="taskrelevancehistory" list="task.taskcreate.taskrelevancehistory" repeatdataupdate>'
                            compile(upd)(scope.$parent)
                            var rtdm=angular.element('div.taskrelevance div#taskrelevance')
                            var appdm=rtdm.find('div#relevanceapp[name="'+ddd['relevanceapp']+'"]')
                            var tpdm=appdm.next().find('div#relevancetype[name="'+ddd['relevancetype']+'"]')
                            var ttdm=tpdm.next().find('div.secondary.menu[name="'+ddd['relevanceid']+'"]')
                            if(tpdm.length!=0&&ttdm.length==0){
                                tpdm.next().find('div.secondary.menu').append(compile('<a id="relevance" class="item bread" name="'+ddd['relevanceid']+'" secondarymenu>'+ddd['relevancename']+'</a>')(scope.$parent))
                                scope.$parent.relevancebreadcrumbset(rtdm.parent())
                            }
                        })
                    })
                })
            })
        }
    }
})
mainmodule.directive('taskcreate',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            var sw=window.screen.width
            if(sw < 1400){
                element.find('.pusher').css('width', '83%')
            }
            html='<tbody name="relevancehistory" list="task.taskcreate.relevancehistory" repeatdataupdate>'
            compile(html)(scope.$parent)
            scope.$parent.relevancebreadcrumbset(element, 'servergroup')
        }
    }
})
mainmodule.directive('addinfo',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            var context=''
            var id=element.attr('id')
            element.click(function(){
                if(id=="keyadd"){
                    var addkey=scope.$parent.privilege.key
                    var title='添加key'
                    var dt={
                        'id':{
                            'name':'ID(非中文和特殊字符)',
                            'des':'ID,key的唯一标示(非中文和特殊字符)',
                            'other':'ng-model="addkey.id"'
                        },
                        'des':{
                            'name':'描述',
                            'des':'ID的描述信息',
                            'other':'ng-model="addkey.des"'
                        },
                        'value':{
                            'name':'value',
                            'des':'ID对应的key值',
                            'other':'ng-model="addkey.value"'
                        }
                    }
                }else if(id=="useradd"){
                    var addkey=scope.$parent.privilege.usergroup
                    var title='添加用户'
                    var dt={
                        'id':{
                            'name':'用户(非中文和特殊字符)',
                            'des':'用户名称(非中文和特殊字符)',
                            'other':'ng-model="addkey.username"'
                        },
                        'des':{
                            'name':'描述',
                            'des':'用户的描述信息',
                            'other':'ng-model="addkey.userdes"'
                        }
                    }
                }else if(id=="groupadd"){
                    var addkey=scope.$parent.privilege.usergroup
                    var title='添加组'
                    var dt={
                        'id':{
                            'name':'组名(非中文和特殊字符)',
                            'des':'组名称(非中文和特殊字符)',
                            'other':'ng-model="addkey.groupname"'
                        },
                        'des':{
                            'name':'描述',
                            'des':'组的描述信息',
                            'other':'ng-model="addkey.groupdes"'
                        }
                    }
                }else if(id=="accountadd"){
                    var addkey=scope.$parent.privilege.inform
                    var title='添加主账号'
                    var dt={
                        'type':{
                            'name':"选择通知类型",
                            'des':"选择通知类型",
                            'select':'<div id="accountadd" class="ui selection dropdown"><input type="hidden" name="type"><i class="dropdown icon"></i><div class="default text">选择类型</div><div class="menu"><div class="item" data-value="email">邮件</div><div class="item" data-value="wechat">微信</div></div></div>'
                            //compile ng-options有问题
                            //'select':'ng-model="addkey.type" ng-options="tp for tp in addkey.typelist"'
                        },
                        'id':{
                            'name':'账号(非中文和特殊字符)',
                            'des':'邮件账号(非中文和特殊字符)',
                            'other':'ng-model="addkey.accountname"'
                        },
                        'pwd':{
                            'name':'账号密码',
                            'des':'邮件账号密码, 若开启了授权码类认证登陆, 请填写授权码',
                            'other':'ng-model="addkey.accountpwd"'
                        },
                        'des':{
                            'name':'描述',
                            'des':'账号描述信息',
                            'other':'ng-model="addkey.accountdes"'
                        },
                        'server':{
                            'name':'服务器地址',
                            'des':'邮件服务器地址',
                            'other':'ng-model="addkey.accountserver"'
                        },
                        'SMTP_SERVER_PORT':{
                            'name':'服务器SMTP端口',
                            'des':'服务器SMTP端口,不填则使用默认端口25',
                            'other':'ng-model="addkey.accountsmtp_port" nocheck'
                        },
                        'SMTP_SSL_PORT':{
                            'name':'SMTP_SSL端口(*若不使用则不填*)',
                            'des':'服务器SMTP_SSL端口,*不使用ssl则不填*',
                            'other':'ng-model="addkey.accountsmtp_ssl_port" nocheck'
                        },
                        'wechatid':{
                            'name':'公众号ID',
                            'des':'微信公众号ID信息',
                            'other':'ng-model="addkey.accountwechatid"',
                            'fieldattr':'style="display:none"'
                        },  
                        'wechatsecret':{
                            'name':'公众号加密串',
                            'des':'微信公众号加密串secret',
                            'other':'ng-model="addkey.accountwechatsecret"',
                            'fieldattr':'style="display:none"'
                        },
                    }
                }else if(id=="serverprivilege"){
                    var title='主机组服务器规则添加'
                    scope.role=""
                    var dt={
                        'role':{
                            'name':'主机组服务器规则',
                            'des':'填写服务器文件路径(非目录), 用于权限开放, 支持正则方式(基础/扩展/perl), 如/tmp/*/test; ',
                            'other':'ng-model="role"'
                        }
                    }  
                }else if(id=="fault"){
                    var title='故障处理'
                    scope.fault={}
                    scope.fault.id=element.parent().parent().find('.id').text().trim()
                    var dt={
                        'type':{
                            'type':'dropdown',
                            'name':'处理类型',
                            'des':'选择处理类型',
                            'menu':{
                                '0':'故障状态',
                                '1':'未处理',
                                '2':'已处理'
                            }
                        },
                        'remark':{
                            'type':'textarea',
                            'name':'处理信息',
                            'des':'输入故障处理描述信息'
                        }
                    } 
                }else if(id=="contactadd"){
                    var addkey=scope.$parent.privilege.inform
                    var title='添加联系人'
                    var dt={
                        'contacttype':{
                            'name':"账号类型",
                            'des':"联系人账号类型",
                            'select':'<div id="contactadd" class="ui selection dropdown"><input type="hidden" name="type"><i class="dropdown icon"></i><div class="default text">联系人账号类型</div><div class="menu"><div class="item" data-value="email">邮件</div><div class="item" data-value="wechat">微信</div></div></div>'
                            //compile ng-options有问题
                            //'select':'ng-model="addkey.type" ng-options="tp for tp in addkey.typelist"'
                        },
                        'id':{
                            'name':'账号',
                            'des':'联系人账号名,类型为邮件时格式为xxx@xxx',
                            'other':'ng-model="addkey.contactname"'
                        },
                        'des':{
                            'name':'描述',
                            'des':'联系人描述信息',
                            'other':'ng-model="addkey.contactdes"'
                        }
                    }
                }else if(id=="assetdisplay"){
                    var addkey=scope.$parent.privilege.inform
                    var title='资产显示设置'
                    var dt={
                        'keys':{
                            'name':'选择需要显示的字段进行定制(若为空则使用默认显示配置)',
                            'des':'选择需要显示的字段'
                        }
                    }
                    var ngrepeatoption='<option value="{{x.key}}" ng-repeat="x in asset.assetmanager.accountfilter.other">{{x.des}}</option>'
                    var context='<div class="ui segment">'+commservice.get_message("显示定制", "根据业务按需定制资产显示界面;按照显示顺序选择,若为空则使用默认配置,设置完成后资产管理页面生效", 'info')+commservice.get_multiple_search_selection(id, ngrepeatoption)+'<div class="feild selectclear"><button class="negative ui button">清空选择</button></div></div>'
                }else if(id=="serverapp"){
                    var title='添加分类'
                    var dt={
                        'app':{
                            'name':'分类id(非中文和特殊字符)',
                            'des':'输入分类id名称(非中文和特殊字符)'
                        },
                        'des':{
                            'name':'分类描述',
                            'des':'输入分类id描述信息,用于前端展示'
                        }
                    }
                }else if(id=="taskcustom"){
                    scope.taskcustom={}
                    scope.taskcustom.id=''
                    scope.taskcustom.des=''
                    scope.taskcustom.remark=''
                    
                    var title='添加任务'
                    var dt={
                        'id':{
                            'name':'任务id(非中文和特殊字符)',
                            'des':'非中文字不包含特殊字符符串,建议有规律的字符串,方便模糊查询;如:nginx_deploy/nginx_update',
                            'other':'ng-model="taskcustom.id"'
                        },
                        'des':{
                            'name':'任务描述/名称',
                            'des':'输入任务描述/名称,建议有规律的字符串,方便模糊查询;如:部署nginx/升级nginx',
                            'other':'ng-model="taskcustom.des"'
                        },
                        'remark':{
                            'type':'textarea',
                            'name':'备注',
                            'des':'任务备注信息,如描述用途',
                            'other':'ng-model="taskcustom.remark"'
                        }
                    }  
                }else if(id=="collecttemplate"){
                    scope.collecttemplate={}
                    scope.collecttemplate.id=''
                    scope.collecttemplate.des=''

                    var title='添加任务信息收集模板'
                    var dt={
                        'id':{
                            'name':'模板ID(非中文和特殊字符)',
                            'des':'非中文字不包含特殊字符符串',
                            'other':'ng-model="collecttemplate.id"'
                        },
                        'des':{
                            'name':'模板描述/名称',
                            'des':'输入模板描述/名称',
                            'other':'ng-model="collecttemplate.des"'
                        },
                        'remark':{
                            'type':'textarea',
                            'name':'备注',
                            'des':'模板备注信息,如描述用途'
                        }
                    }  

                }else if(id=="groupmember"){
                    var title='添加主机成员'
                    context=commservice.get_message('成员ip信息', '搜索资产中符合当前产品线和业务的主机ip(电信/联通/内网)', 'warn')+'<div id="iplist" class="ui form"><select class="ui fluid selection search dropdown other_key"><option value="0">输入IP搜索</option></select></div>'
                }else if(id=="servergroup"){
                    var title='添加主机组'
                    var dt={
                        'modal':{
                            'type':'dropdown',
                            'name':'主机组模式(yes:需要部署客户端,通过客户端执行任务;no:不需要部署,ssh方式执行任务)',
                            'des':'主机组初始模式(yes:需要部署客户端,通过客户端执行任务;no:不需要部署,ssh方式执行任务)',
                            'menu':{
                                'yes':'yes',
                                'no':'no'
                            }
                        },
                        'group':{
                            'name':'主机组id(非中文和特殊字符)',
                            'des':'输入主机组id(非中文和特殊字符)'
                        },
                        'des':{
                            'name':'主机组id描述',
                            'des':'输入主机组id描述信息,用于前端展示'
                        },
                        'remark':{
                            'type':'textarea',
                            'name':'备注',
                            'des':'主机组备注信息'
                        }
                    }
                }

                if(!context){
                    var context='<div class="ui segment">'+commservice.get_input_form("keyform", dt)+'</div>'
                }
                var md=angular.element(compile(commservice.get_standard_modal(title, context))(scope))
                if (id=="assetdisplay"){
                    md.find('.ui#assetdisplay').dropdown({
                            allowAdditions: true,
                            apiSettings: {
                                url: 'get_assets_templeat_keys'
                            }
                        })
                    md.find('.selectclear button').click(function(){
                        var m=angular.element(event.target).parent().prev()
                        m.find('.dropdown').dropdown('clear')
                    })
                }else{
                    md.find('.ui.selection.dropdown').dropdown()
                }
                
                if(id=="accountadd"||id=="contactadd"){
                    var cdm=md.find('.ui.selection.dropdown')
                    var tp=''
                    cdm.click(function(){
                        tp=angular.element(event.target).attr('data-value')
                        var fdm=cdm.parent().parent().find(' > .field')
                        if(id=="contactadd"){
                            return false
                        }
                        if(tp=="wechat"){
                            fdm.slice(1,7).hide()
                            fdm.slice(7,9).show()
                        }else if(tp=="email"){
                            fdm.slice(1,7).show()
                            fdm.slice(7,9).hide()
                        }
                    })

                }
                if(id=="groupmember"){
                    var tdm=md.find('#iplist')
                    tdm.keyup(function(){
                        var ip=tdm.find('input').val()
                        var dt={}
                        if(!ip.match(/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/)){
                            return false
                        }
                        dt['iplist']=ip
                        dt['line']=scope.$parent.breadcrumblist['line']['key']
                        dt['product']=scope.$parent.breadcrumblist['product']['key']
                        md.find('select option:gt(0)').remove()
                        scope.$parent.commservice.request_url('getinfo_assetinfo', "post", dt, function(d){
                            scope.$parent.groupmemberlist=d
                            var str=''
                            for(l in d){
                                str+='<option app="'+d[l]['app']+'" value="'+d[l]['telecom_ip']+'">'+d[l]['telecom_ip']+'</option>'
                            }
                            md.find('select').append(str)
                        })
                    })
                }
                md.find('input[nocheck=""]').keyup(function(){
                    var tdm=angular.element(event.target)
                    if(tdm.next().is('span[ng-show]')){
                        tdm.next().remove()
                    }
                    tdm.removeAttr('required')
                })
                md.find('input:not("[nocheck]")').keyup(function(){
                    scope.$parent.input_check()
                })
                md.modal('show').find('.actions .right.button').click(function(){
                    var d={}
                    var check=false
                    if(id=="useradd"){
                        d['user']=scope.addkey.username
                        d['des']=scope.addkey.userdes
                        if(scope.addkey.username==""||scope.addkey.userdes==""){
                            check=true
                        }
                    }else if(id=="assetdisplay"){
                        var dt=md.find('#assetdisplay').dropdown('get value')
                        d['keys']=dt[dt.length-1]
                    }else if(id=="groupadd"){
                        d['group']=scope.addkey.groupname
                        d['des']=scope.addkey.groupdes
                        if(scope.addkey.groupname==""||scope.addkey.groupdes==""){
                            check=true
                        }
                    }else if(id=="keyadd"){
                        d['id']=scope.addkey.id
                        d['des']=scope.addkey.des
                        d['value']=scope.addkey.value
                        if(scope.addkey.id==""||scope.addkey.des==""||scope.addkey.value==""){
                            check=true
                        }

                    }else if(id=="accountadd"||id=="contactadd"){
                        if(tp==""){
                            commservice.alert_message('err','通知类型错误',"获取通知类型失败", true)
                            return false
                        }
                        d['type']=tp
                        if(id=="accountadd"){
                            if(tp=="email"){
                                d['name']=scope.addkey.accountname
                                d['des']=scope.addkey.accountdes
                                d['pwd']=scope.addkey.accountpwd
                                d['server']=scope.addkey.accountserver
                                d['smtp_port']=scope.addkey.accountsmtp_port
                                d['smtp_ssl_port']=scope.addkey.accountsmtp_ssl_port
                                if(scope.addkey.accountname==""||scope.addkey.accountdes==""||scope.addkey.accountpwd==""||scope.addkey.accountserver==""){
                                    check=true
                                }
                            }else if(tp=="wechat"){
                                d['id']=scope.addkey.accountwechatid
                                d['secret']=scope.addkey.accountwechatsecret
                                if(scope.addkey.accountwechatid==""||scope.addkey.accountwechatsecret==""){
                                    check=true
                                }
                            }
                        }else{
                            d['name']=scope.addkey.contactname
                            d['des']=scope.addkey.contactdes
                            if(scope.addkey.contactname==""||scope.addkey.contactdes==""){
                                check=true
                            }
                        }
                    }else if(id=="serverprivilege"){
                        d['name']=scope.role
                        d['line']=element.attr('line')
                        d['product']=element.attr('product')
                        d['app']=element.attr('app')
                        d['group']=element.attr('group')
                        check=scope.$parent.data_check(d)
                    }else if(id=="fault"){
                        d['id']=scope.fault.id
                        d['status']=md.find('select').val()
                        if(d['status']==0){
                            d['status']=''
                        }
                        d['remark']=md.find('textarea.remark').val()
                        check=scope.$parent.data_check(d)
                    }else if(id=="servergroup"){
                        d['name']=md.find('input[name="group"]').val()
                        d['des']=md.find('input[name="des"]').val()
                        d['modal']=md.find('select.dropdown#modal').val()
                        d['line']=scope.$parent.breadcrumblist['line']['key']
                        d['product']=scope.$parent.breadcrumblist['product']['key']
                        d['app']=scope.$parent.breadcrumblist['app']['key']
                        check=scope.$parent.data_check(d)
                        d['remark']=md.find('textarea.remark').val()
                    }else if(id=="groupmember"){
                        d['name']=md.find('#iplist .text').text().trim().replace(/输入IP搜索/g, '')
                        d['assetapp']=md.find('#iplist select option[value="'+d['name']+'"]').attr('app')
                        
                        d['line']=scope.$parent.breadcrumblist['line']['key']
                        d['product']=scope.$parent.breadcrumblist['product']['key']
                        d['app']=scope.$parent.breadcrumblist['app']['key']
                        d['group']=scope.$parent.breadcrumblist['server']['key']
                        check=scope.$parent.data_check(d)
                    }else if(id=="collecttemplate"){
                        d['name']=scope.collecttemplate.id
                        d['des']=scope.collecttemplate.des
                        check=scope.$parent.data_check(d)
                        d['remark']=md.find('textarea.remark').val()
                        
                    }else if(id=="taskcustom"){
                        d['name']=scope.taskcustom.id
                        d['des']=scope.taskcustom.des
                        check=scope.$parent.data_check(d)
                        d['remark']=md.find('textarea.remark').val()
                        
                    }else if(id=="serverapp"){
                        d['name']=md.find('input[name="app"]').val()
                        d['des']=md.find('input[name="des"]').val()
                        d['line']=scope.$parent.breadcrumblist['line']['key']
                        d['product']=scope.$parent.breadcrumblist['product']['key']
                        check=scope.$parent.data_check(d)
                    }
                    if(check){
                        return false
                    }
                    url="add_info_"+id+".html"

                    commservice.request_url(url,"post",d,function(dt){
                        commservice.alert_message(dt['status'],dt['message'])
                        if(dt['status']=='err'){
                            return false
                        }
                        //更新数据
                        var uphtm=''
                        if(id=="contactadd"){
                            uphtm='<div list="privilege.inform.contactlist" repeatdataupdate></div>'
                        }else if(id=="accountadd"){
                            uphtm='<div list="privilege.inform.accountlist" repeatdataupdate></div>'
                        }else if(id=="useradd"){
                            uphtm='<div list="privilege.usergroup.userlist" repeatdataupdate></div>'
                        }else if(id=="groupadd"){
                            uphtm='<div list="privilege.usergroup.grouplist" repeatdataupdate></div>'
                        }else if(id=="groupmember"){
                            var dt=scope.$parent.breadcrumblist
                            uphtm='<div name="serverdetails" list="servermanager.servergroup.serverdetails.'+dt['line']['key']+'_and_'+dt['product']['key']+'_and_'+dt['app']['key']+'_and_'+dt['server']['key']+'" repeatdataupdate></div>'
                            
                        }else if(id=="servergroup"){
                            uphtm='<div name="groupdetails" list="servermanager.servergroup.grouplist.'+d['line']+'_and_'+d['product']+'_and_'+d['app']+'" repeatdataupdate></div>'
                            //更新主机组
                            var dt=scope.$parent.breadcrumblist
                            var ddm=angular.element('.leftdm div#line[name="'+dt['line']['key']+'"]').next().find('div#product[name="'+dt['product']['key']+'"]').next().find('div#app[name="'+dt['app']['key']+'"]')
                            var ddd={}
                            ddd[d['name']]=d['des']
                            scope.$parent.currentserverlist=[ddd]
                            scope.$parent.get_accordion_content(scope.$parent.currentserverlist, ddm)

                        }else if(id=="serverapp"){
                            uphtm='<div name="appdetails" list="servermanager.servergroup.applist.'+d['line']+'_and_'+d['product']+'" repeatdataupdate></div> <repeatdataupdate name="servergroup" list="servermanager.servergroup.appgrouplist.'+d['line']+'_and_'+d['product']+'" ></repeatdataupdate>'
                        }else if(id=="collecttemplate"){
                            uphtm='<tbody list="taskmanager.collecttemplate.collecttemplatelist" repeatdataupdate></tbody>'
                        }else if(id=="serverprivilege"){
                            uphtm='<tbody name="serverprivilegedetails" list="servermanager.serverprivilege.serverprivilegedetails.'+d['line']+'_and_'+d['product']+'_and_'+d['app']+'_and_'+d['group']+'" repeatdataupdate>'
                        }else if(id=="taskcustom"){
                            uphtm='<tbody name="taskcustom" list="taskmanager.taskcustom.taskinfolist.taskinfo" repeatdataupdate></tbody>'
                            
                        }else if(id=="keyadd"){
                            uphtm='<div list="privilege.key.keylist" repeatdataupdate></div>'
                        }
                        compile(uphtm)(scope.$parent)
                    }, function(){
                        commservice.alert_message('err','添加失败',"请检查")
                    })
                })

            })
        }
    }
})

mainmodule.directive('accountfilter',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.find('div').click(function(){
                var dm=angular.element(event.target)
                var type=dm.attr('data-value')
                var fdm=element.parent().parent().parent()
                if(type=="email"){
                    fdm.find('table th,table td').show()
                    fdm.find('table .weid,table .wesecret').hide()
                    angular.forEach(fdm.find('td.type'),function(data){
                        if(angular.element(data).text().trim()=="wechat"){
                            angular.element(data).parent().hide()
                        }else{
                            angular.element(data).parent().show()
                        }
                    })
                }else if(type=="wechat"){
                    fdm.find('table th,table td').hide()
                    fdm.find('table th:eq(-1)').show()
                    fdm.find('table .weid,table .wesecret,table .statuset,table .status').show()
                    angular.forEach(fdm.find('td.type'),function(data){
                        if(angular.element(data).text().trim()=="wechat"){
                            angular.element(data).parent().show()
                            angular.element(data).parent().find('td:eq(-1)').show()
                        }else{
                            angular.element(data).parent().hide()
                        }
                    })
                }
                    
            })
        }
    }
}) 
mainmodule.directive('trhandle',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.find('button,.button').click(function(){
                var name=element.attr('key')
                var id=element.attr('id')
                if(name=="assetsinfo"){
                    var keytype=element.attr('keytype')
                    var key=['line', 'product', 'app', 'idc', 'owner', 'user', 'port', 'pwd', 'tool_path', 'status','telecom_ip']
                    scope.$parent.trdata['keytype']=keytype
                }else if(id=="taskrelevancehistory"){
                    var key=['relevance_id']
                }else if(id=="taskhistory"){
                    var key=['id', 'relevance_id', 'custom_name', 'task_type', 'task_name', 'custom_type', 'status', 'execute_time', 'c_time', 'c_user']
                }else if(id=="taskcustom"){
                    var key=['task_id', 'filename']
                }else if(id=="servergroup"){
                    var key=['app', 'app_des', 'modal', 'remark', 'group_id', 'group_des', 'asset_app', 'member']
                }else{
                    var key=[]
                }

                for(i in key){
                    scope.$parent.trdata[key[i]]=element.find('td.'+key[i]).text().trim().split('&')[0]
                }

            })
            
            attrs.$observe('key', function(){
                var name=element.attr('key')
                var pageid=element.attr('pageid')
                var pagination=element.attr('pag')
                var id=element.attr('id')
                if(name=="wechat"){
                    element.hide()
                }else if(name=="assetsinfo"||id=="taskcustom"||id=="servergroup"||id=="collecttemplatehistory"||id=="taskrelevancehistory"||id=="taskhistory"){
                    if(pageid != 1 && pagination==0){
                        element.hide()    
                    }
                }else if(name == 'email'){
                    element.show()
                }else if(pageid != 1){
                    element.hide()  
                }
            })
        }
    }   
})

mainmodule.directive('taskbarset',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            var fn=attrs.$observe('status', function(){
                
                var state=element.attr('status')
                var cl=scope.$parent.statelist[state]
                if(!cl){
                    cl='err'
                }
                if(state=="err"||!state){
                    var pt=80
                }else if(state=="ready"){
                    var pt=10
                }else if(state=="cancel"||state=="logininfoerr"||state=="timeout"||state=="filenotexists"){
                    var pt=40
                }else if(state=="running"){
                    var pt=30
                }else if(state=="offline"){
                    var pt=50
                }else if(state=="failed"){
                    var pt=70
                }else if(state=="success"||state=="done"){
                    var pt=100
                }

                //element.progress('increment')
                element.removeClass('red blue teal yellow green')
                element.addClass(cl)
                element.progress('set progress', pt)
                fn()
            })
        }
    }
})
mainmodule.directive('upload',function(){
    return {
        //同个dom自定义多个指令时候scope得一直,设置为true
        scope:true,
        restarict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile

            element.click(function(){
                var save_file=''
                if(id=="assetupload"){
                    var title='资产导入'
                    var bar_des='上传进度'
                    var form_head_des='注意:'
                    var form_head_tail='资产导入只支持csv文件格式'
                    var err_message='导入失败'
                    var key=id
                    var value=id
                    var url="assets_import"
             
                }else if(id=="serverprivilegelist"){
                    var title='服务器文件更新'
                    var bar_des='上传进度'
                    var form_head_des='注意:'
                    var form_head_tail='选择需要上传的可执行文件'
                    var err_message='上传失败'
                    var key=id
                    var trdm=element.parent().parent()
                    var url="serverprivilege_file_upload"
                    
                }else if(id=="taskcustom"){
                    var title='任务文件上传'
                    var bar_des='上传进度'
                    var form_head_des='注意:'
                    var form_head_tail='选择需要上传的可执行文件'
                    var err_message='上传失败'
                    var key=id
                    var trdm=element.parent().parent()
                    var value={}
                    var task_id=trdm.find('.task_id').text().trim()
                    
                    //scope为true
                    value['task_id']=task_id
                    value['filename']=trdm.find('.filename').text().trim()
                    value=commservice.obj_to_json(value)
                    
                    var url="task_file_upload"
                }else if(id=="loginuser"||id=="loginport"||id=="loginpwd"||id=="initoolsmanager"){
                    var logintype=element.parent().parent().prev().attr('id')
                    if(logintype=="logininitools"||logintype=="logintools"){
                        var trdm=element.parent().parent().parent().parent().parent()
                    }else if(id=="initoolsmanager"){
                        var trdm=element.parent().parent()
                    }else{
                        var trdm=element.parent().parent().parent().parent()
                    }

                    var bar_des='上传进度'
                    var form_head_des='注意:'
                    var form_head_tail=element.attr('data-content')
                    var err_message='上传失败'
                    var key=id
                    var value={}
                    value['line']=trdm.find('td.line').text().trim()
                    value['product']=trdm.find('td.product').text().trim()
                    value['app']=trdm.find('td.app').text().trim()
                    value['idc']=trdm.find('td.idc').text().trim()
                    value['owner']=trdm.find('td.owner').text().trim()
                    value['logintype']=logintype
                    if(id=="initoolsmanager"){
                        var url="modify_"+id+"_info"
                    }else{
                        var url="modify_"+value['logintype']+"_info"
                    }
                    
                    
                    value=commservice.obj_to_json(value)
                    if(id=="loginuser"){
                        var title='服务器登录用户名动态获取工具上传'
                    }else if(id=="loginport"){
                        var title='服务器登录端口动态获取工具上传'
                    }else if(id=="loginpwd"){
                        var title='服务器登录密码动态获取工具上传'
                    }else if(id=="initoolsmanager"){
                        var title='服务器初始化工具上传/更新'
                    }
                    element.parent().parent().prev().popup('hide')
                }

                var md=angular.element(compile(commservice.get_upload(title, bar_des, form_head_des, form_head_tail))(scope.$parent))
                if(id=="serverprivilegelist"){
                    md.addClass('large')
                }
                //md.modal('show').find('#progressbar').progress('increment')
                md.modal('show').find('#progressbar')
                var file=''
                var filename=''
                var uploaddone=false
                md.find('.uploadfile input').change(function(){
                    var tdm=angular.element(event.target)
                    file=tdm.val()
                    filename=file.split('\\')
                    md.find('.replaceuplaod').val(filename[filename.length-1])
                })
                
                md.find('.upload').click(function(){
                    if(!file){
                        commservice.alert_message('err','上传失败', "请先选择文件", true)
                        return false
                    }

                    var i=window.setInterval(function(){
                        var percent=Number(md.find('#progressbar').attr('data-percent'))
                        if(percent < 90){
                            md.find('#progressbar').progress('increment')
                        }
                    },1000)
                    md.find('#progressbar').progress({percent: 5})
                    commservice.uploadfile(md.find('.uploadfile'), {k:key, v:value}, function(d){
                        window.clearInterval(i)
                        uploaddone=true
                        
                        commservice.alert_message(d['code'], d['status'], d['message'])
                        if(d['code']=="err"){
                            return false
                        }
                        save_file=d['save_file']
                        md.find('#progressbar').progress({percent: 100})
                    }, function(d){
                        window.clearInterval(i)
                        commservice.alert_message('-1', 'err', '请求失败')
                    })
                })
                
                md.find('.actions .button:eq(1)').click(function(){
                    if(!file||!uploaddone||!filename){
                        commservice.alert_message('err',err_message, "请先上传文件", true)
                        return false
                    }else{
                        if(id=="assetupload"){
                            var data={filename:filename[filename.length-1]}
                        }else if(id=="taskcustom"){
                            var data={}
                            data['task_id']=task_id
                            data['save_file']=save_file
                            
                        }else if(id=="loginuser"||id=="loginport"||id=="loginpwd"||id=="initoolsmanager"){
                            var data={}
                            data['save_file']=save_file
                            data['id']=id
                            data['data']=value
                        }else if(id=="serverprivilegelist"){
                            var data={
                                'id':scope.$parent.serverprivilegeid ,
                                'ip':scope.$parent.serverprivilegeipadd ,
                                'save_file':save_file,
                                'file':trdm.find('td:eq(0)').text().trim()
                            }
                        }

                        commservice.request_url(url, 'post', data, function(d){
                            if(d['status']=="err"){
                                commservice.alert_message(d['code'], d['status'], d['message'])
                                return  false
                            }else if(id=="serverprivilegelist"){
                                commservice.alert_message(d['code'], d['status'], '更新成功', true)
                            }
                            if(id=="loginuser"){
                                trdm.find('td.user').text(filename[filename.length-1])
                            }
                            if(id=="loginport"){
                                trdm.find('td.port').text(filename[filename.length-1])
                            }
                            if(id=="loginpwd"){
                                trdm.find('td.pwd').text(filename[filename.length-1])
                            }
                            if(id=="taskcustom"){
                                var fn=save_file.split('/')
                                trdm.find('.filename').text(fn[fn.length-1])
                            }
                            if(id=="initoolsmanager"){
                                trdm.find('td.tool_path').text('')
                                trdm.find('td.tool_path i').remove()
                                trdm.find('td.tool_path').append(scope.$parent.compile('<i id="download" class="tool_path" tdicon></i>')(scope.$parent)).find('i').after(filename[filename.length-1])
                            }
                        }, function(){
                            commservice.alert_message(-1, '请求失败')
                        })
                    }
                })
            })
        }
    }
})

mainmodule.directive('pagination',function(){
    return{
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            var name=element.attr('name')
            var pid=element.find('.prev')
            var nid=element.find('.next')
            var currid=1
            //出去next和prev的
            var allid=element.find('a').length - 2
            pid.addClass('disabled')
            var check=scope.$parent.asset.assetmanager
            var tabledm=element.parent().parent().parent()
            element.parent().css({
                'padding':'5px 0px'
            })

            element.find('a').click(function(){
                var tabledm=element.parent().parent().parent()
                var tdm=angular.element(event.target)
                if(tdm.is('i')){
                    tdm=tdm.parent()
                    tabledm=element.parent().parent().parent().parent()
                }
                var thid=tdm.text().trim()
                if(tdm.is('.disabled')||thid==currid){
                    return false
                }
                if(tabledm.is('tbody')){
                    tabledm.find('tr').hide()
                }else{
                    tabledm.find('tr:gt(0)').hide()
                }
                
                //tabledm.find('tr:gt(0)').hide()
                
                if(tdm.is('.prev')){
                    currid-=1
                    var activedm=element.find('a.active').prev()
                    if(activedm.is('div.disabled')){
                        activedm=activedm.prev()
                    }
                }else if(tdm.is('.next')){
                    currid+=1
                    var activedm=element.find('a.active').next()
                    if(activedm.is('div.disabled')){
                        activedm=activedm.next()
                    }
                }else{
                    currid=tdm.text().trim()
                    var activedm=tdm
                }

                element.find('.active').removeClass('active')
                if(tabledm.find('tr[pageid="'+currid+'"]').length==0){
                    //后台获取数据
                    scope.$parent.searchinfo(id, name, currid)
                }else{
                    tabledm.find('tr[pageid="'+currid+'"]').show()
                }
                
                activedm.addClass('active')
                if(tdm.prev().is('div.disabled')){
                    activedm.prev().prev().show()
                }else{
                    activedm.prev().show()
                }
                if(tdm.next().is('div.disabled')){
                    activedm.next().next().show()
                }else{
                    activedm.next().show()
                }
                
                if(currid>=4&&currid <= allid - 1){
                    if(activedm.prev().is('div.disabled')){
                        var tpdm=activedm.prev().prev().prev()
                    }else{
                        var tpdm=activedm.prev().prev()
                        if(tpdm.is('div.disabled')){
                            tpdm=tpdm.prev()
                        }
                    }
                    if(activedm.next().is('div.disabled')){
                        var tndm=activedm.next().next().next()
                    }else{
                        var tndm=activedm.next().next()
                        if(tndm.is('div.disabled')){
                            tndm=tndm.next()
                        }
                    }
                    if(currid >= 4 && currid <= allid && tpdm.text().trim() != 1 && tndm.text().trim() != allid){
                        if(!tpdm.is('.prev')){
                            tpdm.hide()
                        }
                        if(!tndm.is('.next')){
                            tndm.hide()
                        }
                    }
                    if(tndm.text().trim() == allid||tndm.text().trim()== allid -1){
                        tpdm.hide()
                    }
                }

                if(currid==1){
                    pid.addClass('disabled')
                    nid.removeClass('disabled')
                }else if(currid==allid){
                    nid.addClass('disabled')
                    pid.removeClass('disabled')
                }else{
                    pid.removeClass('disabled')
                    nid.removeClass('disabled')
                }
            })
        }
    }
})

mainmodule.directive('searchinfo',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                var commservice=scope.$parent.commservice
                var compile=scope.$parent.compile
                var id=element.attr('id')
                var name=element.attr('name')

                scope.$parent.searchinfo(id, name)
            })
        }
    }
})

mainmodule.directive('dropmeninfo',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            scope.$parent.asset.assetmanager.dropmeninfoinit()
            delete scope.$parent.breadcrumblist
            scope.$parent.breadcrumblist={}
            
            var type=element.attr('id')
            var id=element.attr('name')
            var name=element.attr('childrenname')
            var dm=''
            var other_key=''
            var check=scope.$parent.asset.assetmanager
            
            if(type=="accountfilter"){
                if(id=="other"){
                    var dm=element
                    dm.keyup(function(){
                        setTimeout(function(){
                            if(dm.find('.menu .item:not(.filtered)').length==1){
                                other_key=dm.find('input').val().trim()
                                if(check.isfirst(name)){
                                    scope.$parent.asset.assetmanager.accountfilter.tatisticsother_key=other_key
                                }else if(check.issecond(name)){
                                    scope.$parent.asset.assetmanager.accountfilter.historyother_key=other_key
                                }else if(check.isthird(name)){
                                    scope.$parent.asset.assetmanager.accountfilter.other_key=other_key
                                }
                                
                                if(other_key.match(/{/)){
                                    other_key=other_key.split(':')[0]
                                }
                                if(!other_key.match(/:/)){
                                    dm.trigger('click')
                                }
                            }
                        },500)
                    })
                    //这里遗留点击获取信息问题
                }else{
                    var dm=element.parent()
                }
            }
            if(!dm){
                return false
            }
            dm.click(function(){
                if(id=="other"){
                    if(!other_key){
                        if(!angular.element(event.target).is('input,.default.text')){
                            return false
                        } 
                    }

                }else{
                    if(!angular.element(event.target).is(dm)){
                        return false
                    }
                }
                var url='get_dropmeninfo_'+type
                var data={}
                var adt=scope.$parent.asset.assetmanager.accountfilter
                data['type']=id
                if(check.isfirst(name)){
                    data['line']=adt.tatisticslinevalue
                    data['product']=adt.tatisticsproductvalue
                    data['app']=adt.tatisticsappvalue
                    data['idc']=adt.tatisticsidcvalue
                    if(id=="other"){
                        data['key']=adt.tatisticsother_key
                    }
                }else if(check.issecond(name)){
                    data['line']=adt.historylinevalue
                    data['product']=adt.historyproductvalue
                    data['app']=adt.historyappvalue
                    data['idc']=adt.historyidcvalue
                    if(id=="other"){
                        data['key']=adt.historyother_key
                    }
                }else if(check.isthird(name)){
                    data['line']=adt.linevalue
                    data['product']=adt.productvalue
                    data['app']=adt.appvalue
                    data['idc']=adt.idcvalue
                    if(id=="other"){
                        data['key']=adt.other_key
                    }
                }

                if(id=="other" && !other_key){
                    return false
                }else{
                    if(id=="other"){
                        dm.find('.dropdown').addClass('loading')
                    }else{
                        dm.addClass('loading')
                    }
                }
                commservice.request_url(url, 'post', data, function(d){
                    if(d['status']=="err"){
                        commservice.alert_message(d['code'], d['status'], d['message'])
                    }

                    if(id=="line"){
                        if(check.isfirst(name)){
                            scope.$parent.asset.assetmanager.accountfilter.tatisticsline=d
                        }else if(check.issecond(name)){
                            scope.$parent.asset.assetmanager.accountfilter.historyline=d
                        }else if(check.isthird(name)){
                            scope.$parent.asset.assetmanager.accountfilter.line=d
                        }
                        
                    }else if(id=="product"){
                        if(check.isfirst(name)){
                            scope.$parent.asset.assetmanager.accountfilter.tatisticsproduct=d
                        }else if(check.issecond(name)){
                            scope.$parent.asset.assetmanager.accountfilter.historyproduct=d
                        }else if(check.isthird(name)){
                            scope.$parent.asset.assetmanager.accountfilter.product=d
                        }
                        
                    }else if(id=="app"){
                        if(check.isfirst(name)){
                            scope.$parent.asset.assetmanager.accountfilter.tatisticsapp=d
                        }else if(check.issecond(name)){
                            scope.$parent.asset.assetmanager.accountfilter.historyapp=d
                        }else if(check.isthird(name)){
                            scope.$parent.asset.assetmanager.accountfilter.app=d
                        }

                    }else if(id=="idc"){
                        if(check.isfirst(name)){
                            scope.$parent.asset.assetmanager.accountfilter.tatisticsidc=d
                        }else if(check.issecond(name)){
                            scope.$parent.asset.assetmanager.accountfilter.historyidc=d
                        }else if(check.isthird(name)){
                            scope.$parent.asset.assetmanager.accountfilter.idc=d
                        }
                        
                    }else if(id=="other"){
                        if(check.isfirst(name)){
                            scope.$parent.asset.assetmanager.accountfilter.tatisticsother_key=''
                            scope.$parent.asset.assetmanager.accountfilter.tatisticsother=d
                        }else if(check.issecond(name)){
                            scope.$parent.asset.assetmanager.accountfilter.historyother_key=''
                            scope.$parent.asset.assetmanager.accountfilter.historyother=d
                        }else if(check.isthird(name)){
                            scope.$parent.asset.assetmanager.accountfilter.other_key=''
                            scope.$parent.asset.assetmanager.accountfilter.other=d
                        }
                        dm.find('.menu').dropdown('show')
                        dm.find('.dropdown').removeClass('loading')
                    }
                    dm.removeClass('loading')
                })
            })
            dm.parent().find('input').change(function(){
                var tmd=angular.element(event.target)
                var td=tmd.attr('value')
                if(td=='0'){
                    td=''
                }
                if(id=="line"){
                    if(check.isfirst(name)){
                        scope.$parent.asset.assetmanager.accountfilter.tatisticslinevalue=td
                    }else if(check.issecond(name)){
                        scope.$parent.asset.assetmanager.accountfilter.historylinevalue=td
                    }else if(check.isthird(name)){
                        scope.$parent.asset.assetmanager.accountfilter.linevalue=td
                    }
                    
                }else if(id=="product"){
                    if(check.isfirst(name)){
                        scope.$parent.asset.assetmanager.accountfilter.tatisticsproductvalue=td
                    }else if(check.issecond(name)){
                        scope.$parent.asset.assetmanager.accountfilter.historyproductvalue=td
                    }else if(check.isthird(name)){
                        scope.$parent.asset.assetmanager.accountfilter.productvalue=td
                    }
                    
                    
                }else if(id=="app"){
                    if(check.isfirst(name)){
                        scope.$parent.asset.assetmanager.accountfilter.tatisticsappvalue=td
                    }else if(check.issecond(name)){
                        scope.$parent.asset.assetmanager.accountfilter.historyappvalue=td
                    }else if(check.isthird(name)){
                        scope.$parent.asset.assetmanager.accountfilter.appvalue=td
                    }
                }else if(id=="idc"){    
                    if(check.isfirst(name)){
                        scope.$parent.asset.assetmanager.accountfilter.tatisticsidcvalue=td
                    }else if(check.issecond(name)){
                        scope.$parent.asset.assetmanager.accountfilter.historyidcvalue=td
                    }else if(check.isthird(name)){
                        scope.$parent.asset.assetmanager.accountfilter.idcvalue=td
                    }
                    
                }
            })
        }
    }
})
mainmodule.directive('download',function(){
    return {
        scope:{},
        restarict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            element.click(function(){
                var id=element.attr('id')
                url=id+"_download"
                var data={}
                if(id=="assetscvs"||id=="assethistory"||id=="tatistics"){
                    var dm=element.parent().next()
                    data['line']=dm.find('input.line').val().trim()
                    data['product']=dm.find('input.product').val().trim()
                    data['app']=dm.find('input.app').val().trim()
                    data['idc']=dm.find('input.idc').val().trim()
                    data['other_key']=dm.find('div.other .text').text().trim()
                    if (!data['other_key'].match(/:/)){
                        data['other_key']=""
                    }
                    data['iplist']=dm.find('textarea.iplist').val().trim().replace(/\n/g, ',')
                    
                }else if(id=="serverprivilegelist"){
                    var trdm=element.parent().parent()
                    data['id']=scope.$parent.serverprivilegeid
                    data['ip']=scope.$parent.serverprivilegeipadd
                    data['file']=trdm.find('td:eq(0)').text().trim()
                    
                }else if(id=="taskcustom"){
                    var trdm=element.parent().parent()
                    data['task_id']=trdm.find('.task_id').text().trim()
                    data['filename']=trdm.find('.filename').text().trim()
                    if(!data['filename']){
                        scope.$parent.alert_message('err', '下载失败', '任务文件为空')
                        return false
                    }
                }else if(id=="assettemplate"){
                    
                }
                element.addClass('loading')
                commservice.request_url(url, 'post', data, function(d){
                    element.removeClass('loading')
                    if(d['status']=="err"){
                        commservice.alert_message(d['code'], d['status'], d['message'])
                        return false
                    }
                    if(d==""){
                        return false
                    }
                    if(id=="serverprivilegelist"){
                        var ck=0
                        var a=window.setInterval(function(){
                            data['downloadfile']=d
                            commservice.request_url('serverprivilegefile_check', 'post', data, function(dd){
                                if(dd['code'] == -2){
                                    ck+=1
                                }else{
                                    window.clearInterval(a)
                                    return commservice.page_jump(d)
                                }
                                if(ck >= 30){
                                    window.clearInterval(a)
                                    return commservice.alert_message('err', '超时', '文件下载超时', true)
                                }
                            })
                        }, 3000)
                    }else{
                        commservice.page_jump(d)
                    }
                })
            })
        }
    }
})

mainmodule.directive('textareaset',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var name=element.attr('name')
            var id=element.attr('id')
            //这里的line-height 是.ui.selection.dropdown的高度
            element.find('textarea').css('line-height','1em')
            element.find('textarea').keyup(function(){
                var dom=angular.element(event.target)
                if(name=="assetfilter"){
                    var tv=dom.val().trim().replace(/\n/g, ',')
                    if(id=="tatistics"){
                        scope.$parent.asset.assetmanager.accountfilter.tatisticsiplist=tv
                    }else if(id=="servergroup"){
                        scope.$parent.servergroupsearchlist=tv
                    }else if(id=="history"){
                        scope.$parent.asset.assetmanager.accountfilter.historyiplist=tv
                    }else{
                        scope.$parent.asset.assetmanager.accountfilter.iplist=tv
                    }
                }
            })
            element.find('textarea').focus(function(){
                var dom=angular.element(event.target)
                if(name=="assetfilter"){
                    var wd='185px'
                    dom.css({
                        'height': '20em',
                        'position': 'absolute',
                        //'z-index': '9999',
                        'width':wd
                    })
                    element.next().css({
                        'left':'187px'
                    })
                    dom.blur(function(){
                        dom.val(dom.val().trim())
                        dom.css({
                            'position': 'relative',
                            'width':'100%',
                            'height': 'inherit'
                        })
                        element.next().css({
                            'left':'0px'
                        })
                    })
                }
            })

        }
    }
})
mainmodule.directive('trdetailbutton',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.click(function(){
                var id=element.attr('id')
                var pdm=element.parent().parent()
                var url=id+'_detail'
                var commservice=scope.$parent.commservice
                var compile=scope.$parent.compile
                var d={}
                if(id=="assethistory"){
                    var tid=pdm.find('td.id').text().trim()
                    d['id']=tid
                }else if(id=="loginmanager"){
                    var tip=pdm.find('td.telecom_ip').text().trim()
                    d['iplist']=tip
                }
                commservice.request_url(url, 'post', d, function(dt){
                    var data={}
                    var head=''
                    var trbody=''
                        
                    if(id=="assethistory"){
                        title='id:['+tid+']资产变更详情'
                        data['head']={
                                'Name':'名称', 
                                'old_info':'变更前信息', 
                                'new_info':'变更为'
                            }

                        data['old_info']=commservice.json_to_obj(dt['data'][0]['old_info'])[0]
                        if(!dt['data'][0]['new_info']){
                            data['new_info']=[]
                        }else{
                            data['new_info']=commservice.json_to_obj(dt['data'][0]['new_info'])[0]
                        }
                        for(k in data['head']){
                            head+='<th rowspan="1" class="'+k+'">'+data['head'][k]+'</th>'
                        }
                        for(i in dt['key']){
                            trbody+='<tr>'
                            for(ii in dt['key'][i]){
                                if(ii!="id"){
                                    if(data['new_info'][ii]==undefined){
                                        var newinfo=''
                                        var color=''
                                    }else{
                                        var newinfo=data['new_info'][ii]
                                        var color='style="color:red"'
                                    }
                                    trbody+='<td class="'+ii+'">'+dt['key'][i][ii]+'</td><td class="old" '+color+'>'+data['old_info'][ii]+'</td><td class="new" '+color+'>'+newinfo+'</td>'
                                }
                            }
                            trbody+="</tr>"
                        }
                        
                    }else if(id=="account"){
                        title='账号详情'
                        data['head']={
                                'Name':'名称', 
                                'value':'值'
                            }
                        for(k in data['head']){
                            head+='<th rowspan="1" class="'+k+'">'+data['head'][k]+'</th>'
                        }
                        var emailkey=['name', 'des', 'pwd', 'type', 'email_server', 'smtp_ssl_port', 'smtp_port', 'status']
                        for (i in emailkey){
                            trbody+='<tr>'
                            trbody+='<td>'+element.parent().parent().parent().parent().find('th.'+emailkey[i]+'').text().trim()+"</td>"
                            trbody+='<td>'+element.parent().parent().find('td.'+emailkey[i]+'').text().trim()+"</td>"
                            trbody+="</tr>"
                        }
                        
                    }else if(id=="loginmanager"){
                        title='ip:['+tip+']服务器详情'
                        data['head']={
                                'Name':'名称', 
                                'value':'值'
                            }
                        data['value']=dt['data'][0]
                        for(k in data['head']){
                            head+='<th rowspan="1" class="'+k+'">'+data['head'][k]+'</th>'
                        }
                        for(i in dt['key']){
                            trbody+='<tr>'
                            for(ii in dt['key'][i]){
                                trbody+='<td class="'+ii+'">'+dt['key'][i][ii]+'</td><td class="value">'+data['value'][ii]+'</td>'
                            }
                            trbody+="</tr>"
                        }
                    }
                    angular.element(commservice.get_structured_comp_table(head, trbody, {'title':title}, 'ui large modal')).modal('show')
                })
                
            })
        }
    }
})
mainmodule.directive('serverinit',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.find('.menu .item').click(function(){
                var tdm=angular.element(event.target)
                var fdm=element.parent().parent()
                var tv=tdm.attr('data-value')
                if(tv==2||tv==3){
                    fdm.find('.line,.product,.app,.idc').parent().addClass('disabled')
                    fdm.find('.other_key').addClass('disabled')
                }else{
                    fdm.find('.line,.product,.app,.idc').parent().removeClass('disabled')
                    fdm.find('.other_key').removeClass('disabled')
                }
            })
        }
    }
})
mainmodule.directive('batchopertion',function(){
    return {
        scope:true,
        restarict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            element.click(function(){
                var id=element.attr('id')
                if(id=="serverinit"){
                    setTimeout(function(){
                        var fdm=element.parent().parent().parent()
                        var title='确认选择以下服务器进行初始化?'
                        var checkbd=''
                        var asset=scope.$parent.trdata
                        if(asset['status']=='success'){
                            commservice.alert_message('err', '初始化失败', '已经初始化成功')
                            return false
                        }
                        var tip=element.parent().parent().find('td.telecom_ip').text().trim()
                        scope.$parent.check_iplist=[]

                        angular.forEach(fdm.find('tr:visible'), function(data){
                            var dm=angular.element(data)
                            var ip=dm.find('.telecom_ip').text().trim()
                            var line=dm.find('.line').text().trim()
                            var product=dm.find('.product').text().trim()
                            var app=dm.find('.app').text().trim()
                            var idc=dm.find('.idc').text().trim()
                            var owner=dm.find('.owner').text().trim()

                            if(line==asset['line']&&product==asset['product']&&app==asset['app']&&idc==asset['idc']&&owner==asset['owner']){
                                if(ip==tip){
                                    var checked='checked'
                                    if(scope.$parent.check_iplist.indexOf(ip)==-1){
                                        scope.$parent.check_iplist.push(ip)
                                    }
                                }else{
                                    var checked=''
                                }
                                checkbd+='<div class="item"><div class="ui child checkbox"><input type="checkbox" name="'+ip+'" '+checked+'><label>'+ip+'</label></div></div>'
                            }
                        })
                        var tdm=angular.element(compile(commservice.get_standard_modal(title, commservice.get_celled_checkbox_list('全选', checkbd, 'check_iplist')))(scope.$parent)).modal('show')
                        tdm.find('.actions .button:eq(1)').click(function(){
                            setTimeout(function(){
                                var url='getresult_serverinit'
                                if(scope.$parent.check_iplist.length==0){
                                    return false
                                }
                                commservice.request_url(url, 'post', {line:asset['line'],product:asset['product'],app:asset['app'],idc:asset['idc'],owner:asset['owner'],iplist:scope.$parent.check_iplist}, function(dd){
                                    if(dd['status']=='err'){
                                        commservice.alert_message(dd['status'], dd['code'], dd['message'])
                                        return false
                                    }
                                    var data=commservice.json_to_obj(dd['data'])
                                    scope.$parent.getresult(id, data)
                                })
                            }, 500)
                        })
                    }, 500)
                }
            })
        }
    }
})
mainmodule.directive('tdcheck',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            attrs.$observe('class', function(){
                var cls=element.attr('class')
                if(id=="serverinit"){
                    if(cls!='telecom_ip'&&cls!='tool_path'&&cls!='status'&&cls!='c_time'&&cls!='c_user'){
                        element.hide()
                    }
                }
            })
        }
    }
})
mainmodule.directive('checkboxlist',function(){
    return {
        scope:{
            keylist:'='
        },
        restrict:'A',
        link:function(scope, element, attrs){
            var do_list=function(ischecked, name){
                if(ischecked == true){
                    if(scope.keylist.indexOf(name)==-1){
                        scope.keylist.push(name)
                    }
                }else{
                    if(scope.keylist.indexOf(name)!=-1){
                        scope.keylist.splice(scope.keylist.indexOf(name), 1)
                    }
                }
            }
            element.find('input[type="checkbox"]').click(function(){
                var ddm=angular.element(event.target)
                var ischecked=ddm.prop('checked')
                if(ddm.attr('name')=="all"){
                    angular.forEach(element.find('div.list input[type="checkbox"]'), function(data){
                        var tdm=angular.element(data)
                        var name=tdm.attr('name')
                        do_list(ischecked, name)
                        tdm.prop('checked', ischecked)
                    })
                }else{
                    var name=ddm.attr('name')
                    do_list(ischecked, name)
                }
                scope.$parent.$apply()
            })
        }
    }
})
mainmodule.directive('message',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            element.find('.close').on('click', function() {
                element.find('.close').closest('.message').transition('fade')
            })
            if(id=="closed"){
                setTimeout(function(){
                    element.find('.close').trigger('click')
                }, 4000)
            }
        }
    }
})

mainmodule.directive('datacontent',function(){
    return{
        //同个dom自定义多个指令时候scope得一直,设置为true
        scope:true,
        restrict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('popuptype')
            if(id=="flowing"){
                element.popup({on:'click'})
            }else{
                element.popup()
            }
            
        }
    }
})
mainmodule.directive('domafterhandle',function(){
    return {
        scope:{
            key:'='
        },
        restrict:'A',
        link:function(scope, element, attrs){
            var id=element.attr('id')
            var stype=element.attr('stype')
            attrs.$observe('key', function(){
                if(id=="servergroup"||id=="taskrelevance"){
                    var pdm=element.parent()
                    pdm.find('.active.section').removeClass('active')
                    if(scope.key=='server'||scope.key=='relevanceappa'){
                        element.after('<div  name="'+scope.$parent.breadcrumblist[scope.key]['key']+'" id="'+scope.key+'" class="active section">'+scope.$parent.breadcrumblist[scope.key]['des']+'</div>')
                    }else{
                        element.after('<a  name="'+scope.$parent.breadcrumblist[scope.key]['key']+'" id="'+scope.key+'" class="active section">'+scope.$parent.breadcrumblist[scope.key]['des']+'</div>')
                    }
                }else if(id=="app"){
                    scope.$parent.get_accordion_content(scope.key['group'], element, stype)
                }
            })
        }
    }
})
mainmodule.directive('taskclset',function(){
    return {
        scope:true,
        restrict:'A',
        link:function(scope, element, attrs){
            attrs.$observe('status', function(){
                var type=element.attr('type')
                var cl=element.attr('status')
                if(type=='group'){
                    var dom=element.next()
                }else{
                    var dom=element
                }

                dom.css('color', cl)
            })
        }
    }
})

mainmodule.directive('dropdown',function(){
    return {
        scope:true,
        restrict:'A',
        link:function(scope, element, attrs){
            element.dropdown()
        }
    }
})
mainmodule.directive('secondarymenu',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            attrs.$observe('status', function(){
                var state=element.attr('status')
                var id=element.attr('id')
                var line=element.attr('line')
                var product=element.attr('product')
                var app=element.attr('app')
                var group=element.attr('group')
                var name=element.attr('name')
                
                if(id=="taskservers"){
                    var statelist=scope.$parent.statelist
                    var cl=statelist[state]
                    
                    if(name == 'localhost'){
                        element.css('color', cl)
                        return false
                    }
                    if(!scope.$parent.$parent.taskcolor){
                        scope.$parent.$parent.taskcolor={}
                    }
                    var k=[line, product, app, group]
                    var sk=''
                    var tcl=cl
                    element.css('color', cl)
                    
                    for(i in k){
                        var ttm=element.parent()
                        var selector=['error', 'offline', 'failed', 'ready', 'logininfoerr', 'timeout', 'filenotexists']
                        if(['success', 'done', 'running'].indexOf(state)!=-1){
                            for(j in selector){       
                                if(ttm.find('a[status="'+selector[j]+'"]').length!=0){
                                    tcl=statelist[selector[j]]
                                    break
                                }
                            }
                        }
                        sk+=k[i]+"_and_"
                        scope.$parent.$parent.taskcolor[sk.match(/^(.*)_and_$/)[1]]=tcl
                    }
                }
            })
            element.click(function(){
                var id=element.attr('id')
                var datadm=angular.element('.pusher .datadm')
                var type=element.attr('tasktype')
                var name=element.attr('name')
                element.parent().find('a').removeClass('active')
                element.addClass('active')
                if(id=="relevance"&&type=="relevance"){
                    setTimeout(function(){
                        var gdt=scope.$parent.breadcrumblist
                        datadm.load('get_groupselect.html', {line:gdt['relevanceline']['key'], product:gdt['relevanceproduct']['key'], app:name, gettype:'taskcreate'} , function(){
                            compile(datadm)(scope.$parent)
                            datadm.find('#executetime').find('div.item:eq(0)').click(function(){
                                scope.$parent.task.groupselect.executetime='00-00-00 00:00:00'
                                scope.$parent.$apply(scope.$parent.task.groupselect)
                            })
                            datadm.find('#executetime').find('div.calendar').calendar('setting', 'onChange', function(){
                                setTimeout(function(){
                                    var tm=datadm.find('#executetime').find('div.calendar input').val()
                                    scope.$parent.task.groupselect.executetime=tm
                                    scope.$parent.$apply(scope.$parent.task.groupselect)
                                }, 20)
                            })
                        })
                    }, 20)
                }else if(id=="taskservers"){
                    scope.$parent.$parent.taskserverip=element.attr('name')
                    var dt={}
                    dt['line']=element.attr('line')
                    dt['product']=element.attr('product')
                    dt['app']=element.attr('app')
                    dt['group']=element.attr('group')
                    dt['ip']=scope.$parent.$parent.taskserverip
                    dt['task_name']=scope.$parent.task_name
                    scope.$parent.task.taskhistory.tasklog=[]
                    scope.$parent.$apply(scope.$parent.task.taskhistory.tasklog)
                    commservice.request_url('get_ngrepeat_data_taskservers', 'post', dt, function(d){
                        scope.$parent.task.taskhistory.serversinfo=[]
                        setTimeout(function(){
                            scope.$parent.task.taskhistory.serversinfo=d['serverinfo']
                            scope.$parent.$apply(scope.$parent.task.taskhistory.serversinfo)
                        }, 5)
                    })
                }
            })
        }
    }
})
mainmodule.directive('nag',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.nag('show')
        }
    }
})
mainmodule.directive('taskcreatenextstep',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            element.unbind('click').click(function(){
                var data=scope.$parent.task.groupselect
                var commservice=scope.$parent.commservice
                var compile=scope.$parent.compile
                var message=''
                var messaget=''
                if(commservice.isempty(data['grouplist'])){
                    message='未选择主机信息'
                    messaget='请先选择'
                }
                if(data['executetime']==""){
                    message='未设置任务执行时间'
                    messaget='请先设置'
                }
                if(message){
                    commservice.alert_message('err', message, messaget, true)
                    return false
                }
                commservice.request_url('get_taskcreate_confirm.html', 'post', {data:data, breadcrumblist:scope.$parent.breadcrumblist}, function(html){
                    scope.$parent.task.taskcreate.parameter={}
                    scope.$parent.task.taskcreate.parameter.p1=''
                    scope.$parent.task.taskcreate.parameter.p2=''
                    scope.$parent.task.taskcreate.parameter.p3=''
                    scope.$parent.task.taskcreate.parameter.p4=''
                    var tdm=angular.element(compile(html)(scope.$parent))
                    tdm.find('.actions').find('.right.button').click(function(){
                        element.addClass('disabled')
                        commservice.request_url('task_create', 'post', {data:data, parameter:scope.$parent.task.taskcreate.parameter, breadcrumblist:scope.$parent.breadcrumblist}, function(d){
                            element.removeClass('disabled')
                            commservice.alert_message(d['status'], d['code'], d['message'])
                            if(d['status']=="err"){
                                return false
                            }
                            scope.$parent.task.groupselect.grouplist={}
                            scope.$parent.task.groupselect.tasktypecustom=''
                            scope.$parent.task.groupselect.taskalias=''                            
                            scope.$parent.task.groupselect.executetime=''                            

                            angular.element('.datadm ul.divided.list').find('div.checkbox.checked').checkbox('uncheck')
                        })
                    })
                    tdm.modal('show')
                })
            })
        }
    }
})
mainmodule.directive('groupsearch',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            var gdata=scope.$parent.breadcrumblist
            var group_id=''
            var group_des=''
            var gdm=''
            var bdm=''
            var mdm=''
            
            attrs.$observe('keyname', function(){
                group_id=element.attr('keyname')
            })
            scope.groupvalueset=function(des, dp, gid, mid){
                var ckdt=scope.$parent.task.groupselect.grouplist
                var line=gdata['relevanceline']['key']
                var product=gdata['relevanceproduct']['key']
                var app=gdata['relevanceappa']['key']
                if(!(line in ckdt)){
                   scope.$parent.task.groupselect.grouplist[line]={}
                }
                if(!(product in ckdt[line])){
                   scope.$parent.task.groupselect.grouplist[line][product]={}
                }
                if(!(app in ckdt[line][product])){
                   scope.$parent.task.groupselect.grouplist[line][product][app]={}
                }

                if(gid!=undefined){
                    if(!(gid in ckdt[line][product][app])||des=="group"){
                        scope.$parent.task.groupselect.grouplist[line][product][app][gid]=[]
                    }
                    
                    if(gid in ckdt[line][product][app]&&!dp&&!mid){
                        delete scope.$parent.task.groupselect.grouplist[line][product][app][gid]
                    }
                }

                if(mid!=undefined){
                    if(scope.$parent.task.groupselect.grouplist[line][product][app][gid].indexOf(mid) ==-1){
                        scope.$parent.task.groupselect.grouplist[line][product][app][gid].push(mid)
                    }
    
                    if(scope.$parent.task.groupselect.grouplist[line][product][app][gid].indexOf(mid) !=-1&&!dp){
                       
                        scope.$parent.task.groupselect.grouplist[line][product][app][gid].splice(scope.$parent.task.groupselect.grouplist[line][product][app][gid].indexOf(mid), 1)

                        if(scope.$parent.task.groupselect.grouplist[line][product][app][gid].length==0){
                            delete scope.$parent.task.groupselect.grouplist[line][product][app][gid]
                        }
                    }
                }
                if(commservice.isempty(scope.$parent.task.groupselect.grouplist[line][product][app])){
                    delete scope.$parent.task.groupselect.grouplist[line][product][app]
                } 
                if(commservice.isempty(scope.$parent.task.groupselect.grouplist[line][product])){
                    delete scope.$parent.task.groupselect.grouplist[line][product]
                }
                if(commservice.isempty(scope.$parent.task.groupselect.grouplist[line])){
                    delete scope.$parent.task.groupselect.grouplist[line]
                }
            }

            element.mouseout(function(){
                element.find('div#groupmembersearch').hide()
            })
            element.mouseover(function(){
                gdm=element.find('.accordion div#group')
                bdm=element.find('div#groupmembersearch')
                mdm=element.find('.ui.celled.list#members')
                group_des=element.find('div#group[name="'+group_id+'"]').find('label').text().trim()
                var modal=element.find('div#group[name="'+group_id+'"]').find('a.item').text().trim()
                
                bdm.removeClass('hide disabled').show()
                gdm.find('div.checkbox').checkbox('setting', 'onChange', function(){
                    var dddm=gdm.find('div.checkbox')
                    if(dddm.checkbox('is checked')){
                        bdm.find('.button').addClass('disabled')
                        mdm.find('div.item').find('div.checkbox').checkbox('uncheck').addClass('disabled')
                    }else{
                        bdm.find('.button').removeClass('disabled')  
                        mdm.find('div.item').find('div.checkbox').checkbox('uncheck').removeClass('disabled')
                    }
                    if(commservice.isempty(scope.$parent.task.groupselect.groupinfo)||!('groupinfo' in scope.$parent.task.groupselect)){
                        scope.$parent.task.groupselect.groupinfo={}
                    }
                    scope.$parent.task.groupselect.groupinfo[group_id]={}
                    scope.$parent.task.groupselect.groupinfo[group_id]=group_des
                    if(scope.$parent.task.groupselect.groupmodalrefer==undefined||scope.$parent.task.groupselect.groupmodalrefer==''){
                        scope.$parent.task.groupselect.groupmodalrefer=modal
                    }

                    if(modal!=scope.$parent.task.groupselect.groupmodalrefer){
                        commservice.alert_message('warn', '请注意', '你选择了不同模式的主机执行任务')
                    }
                    scope.groupvalueset('group', dddm.checkbox('is checked'), group_id)
                })
                bdm.unbind('click').click(function(){
                    if(bdm.find('.button').is('.disabled')){
                        return false
                    }
                    var ret=gdm.find('div.checkbox').checkbox('is checked')
                    var title="搜索主机组成员["+group_id+"]"
                    scope.iplist=''
                    var dt={
                        'iplist':{
                            'type':'textarea',
                            'name':'搜索主机组成员',
                            'des':'搜索主机组成员ip,换行分割',
                            'other':'ng-model="iplist"'
                        }
                    }  
                    var context='<div class="ui segment">'+commservice.get_input_form("keyform", dt)+'</div>'
                    var md=angular.element(compile(commservice.get_standard_modal(title, context))(scope))
                    md.modal('show')
                    md.find('.actions').find('.button:eq(1)').click(function(){
                        if(!scope.iplist){
                            return false
                        }
                        var iplist=scope.iplist.replace(/\n/g, ',')
                        var url='get_ngrepeat_data_serverdetails'
                        var dt={}
        
                        dt['line']=scope.$parent.breadcrumblist['relevanceline']['key']
                        dt['product']=scope.$parent.breadcrumblist['relevanceproduct']['key']
                        dt['app']=scope.$parent.breadcrumblist['relevanceappa']['key']
                        dt['group']=group_id
                        dt['gettype']="taskcreate"
                        dt['list']=iplist
                        
                        commservice.request_url(url, 'post', dt, function(rd){
                            if(!rd){
                                commservice.alert_message('err', '主机组成员获取失败', '请检查成员ip', true)
                                return false
                            }
                            if(rd.length!=iplist.split(',').length){
                                commservice.alert_message('warn', '请注意', '当前主机组获取的成员信息不完全', true)
                            }
                            if(ret){
                                var cls='disabled'
                            }else{
                                var cls=''
                            }
                            var html=''
                            for(i in rd){
                                html+='<div class="item" style="padding-top:2px;padding-bottom: 2px"><div class="ui checkbox '+cls+'"><input type="checkbox" name="'+rd[i]['member']+'"><label>'+rd[i]['member']+'</label></div><a class="ui mini image label brown" style="margin-left:20px;float:right">'+rd[i]['asset_app']+'<div class="detail">'+rd[i]['modal']+'</div></a></div>'
                            }
                            mdm.find('div:eq(1)').find('div').remove()
                            mdm.append(html)
                            compile(mdm.find('div:eq(1)'))(scope.$parent)
                            element.find('div.checkbox').checkbox('setting', 'onChange', function(){
                                var tttdm=angular.element(event.target)
                                if(tttdm.is('input')||tttdm.is('label')){
                                    tttdm=tttdm.parent()
                                }
                                var udm=element.find('div.checkbox')
                                var member=tttdm.find('input').attr('name')

                                scope.groupvalueset('member', tttdm.checkbox('is checked'), group_id, member)
                            })
                            element.find('.accordion').accordion('open', 0)
                        })
                    })
                })
            })
        }
    }
})

mainmodule.directive('servergroup',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var tdm=element
            var rightdm=element.find('.pusher .rightdm')
            var commservice=scope.$parent.commservice
            var compile=scope.$parent.compile
            scope.$parent.breadcrumblist={}
            scope.$parent.currentserverlist=[]
            
            //bodydm.find('.accordion').accordion({selector: {trigger: '.title'}})
            tdm.find('.sidebar.menu > div.accordion').accordion({selector: {trigger: '.title'}})

            scope.$parent.servergroupevent=function(ddm){
                if(ddm==undefined){
                    var ddm=tdm.find('#line,#product,#app,#server')
                }
                ddm.unbind('click').click(function(){
                    var dm=angular.element(event.target)
                    var leftdm=angular.element('.leftdm')
                    var rightdm=angular.element('.pusher .rightdm')
                    var id=dm.attr('id')
                    var name=dm.attr('name')
                    var des=dm.text().trim()
                    var pdm=dm.parent().parent()
                    var stype=dm.attr('stype')
                    var dt={}

                    if(id=="line"){
                        leftdm.find('div#line').css('color','')
                        rightdm.html('')
                        scope.$parent.breadcrumblist={}
                        scope.$parent.$apply()
                    }else if(id=="product"){
                        var url='get_app_servergroup'
                        leftdm.find('div#product').css('color','')
                        rightdm.html('')
                        delete  scope.$parent.breadcrumblist['app']
                        delete  scope.$parent.breadcrumblist['server']
                        if(!('line' in scope.$parent.breadcrumblist)){
                            scope.$parent.breadcrumblist['line']={key:pdm.prev().attr('name'), des:pdm.prev().text().trim()} 
                        }
                        dt['line']=pdm.prev().attr('name')
                        dt['product']=name
                    }else if(id=="app"){
                        var url='get_group_servergroup'
                        leftdm.find('div#app').css('color','')
                        delete  scope.$parent.breadcrumblist['server']
                        if(!('product' in scope.$parent.breadcrumblist)){
                            pdm=pdm.parent().parent()
                            scope.$parent.breadcrumblist['product']={key:pdm.prev().attr('name'), des:pdm.prev().text().trim()}
                        }
                        
                        if(!('line' in scope.$parent.breadcrumblist)){
                            pdm=pdm.parent().parent()
                            scope.$parent.breadcrumblist['line']={key:pdm.prev().attr('name'), des:pdm.prev().text().trim()}  
                        }
                        dt['product']=scope.$parent.breadcrumblist['product']['key']
                        dt['line']=scope.$parent.breadcrumblist['line']['key']
                        dt['app']=name
                        
                    }else if(id=="server"){
                        if(stype=='hostprivilege'){
                            var url='get_server_privilege_config'
                        }else{
                            var url='get_member_servergroup'
                        }
                        
                        leftdm.find('a#server').css('color','')
                        if(!('product' in scope.$parent.breadcrumblist)){
                            var dddm=pdm.parent().parent()
                            scope.$parent.breadcrumblist['product']={key:dddm.prev().attr('name'), des:dddm.prev().text().trim()}   
                        }
                        if(!('app' in scope.$parent.breadcrumblist)){
                            scope.$parent.breadcrumblist['app']={key:pdm.prev().attr('name'), des:pdm.prev().text().trim()}
                        }
                        pdm.find('.item').removeClass('active')
                        dm.addClass('active')
                        dt['product']=scope.$parent.breadcrumblist['product']['key']
                        dt['line']=scope.$parent.breadcrumblist['line']['key']
                        dt['app']=scope.$parent.breadcrumblist['app']['key']
                        dt['group']=name
                    }
                    dm.css({
                        color:'brown'
                    })
                    delete scope.$parent.breadcrumblist[id]
                    scope.$parent.$apply(scope.$parent.breadcrumblist)
                    scope.$parent.breadcrumblist[id]={key:name, des:des}
                    scope.$parent.$apply(scope.$parent.breadcrumblist)
                    if(id!="line"){
                        if((stype=='hostprivilege'||stype=='hostprivilegelist')&&id!='server'){
                            return
                        }else if(stype=='hostprivilegelist'){
                            dt['stype']=stype
                        }
                        
                        commservice.request_url(url, 'post', dt, function(d){
                            if(d['status']=="err"){
                                return commservice.alert_message(d['status'], d['code'], d['message'])
                            }
                            rightdm.html(compile(d)(scope.$parent))
                        })
                    }
                })
            }
            scope.$parent.servergroupevent()
        }
    }
})
mainmodule.directive('menuactive',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var commservice=scope.$parent.commservice
            element.find('.dropdown.item').hover(function(){
                if(angular.element(event.target).is('.dropdown.item')){
                   var tdm=angular.element(event.target)
                   element.find('.dropdown.item').removeClass('replaceactive')
                   tdm.addClass('replaceactive')
                }
            }); 
            element.find('.dropdown.item .childrenmenu').click(function(){
                scope.$parent.asset.assetmanager.dropmeninfoinit()
                delete scope.$parent.breadcrumblist
                scope.$parent.breadcrumblist={}
                var tdm=angular.element(event.target)
                var bodydm=angular.element('.body')
                var id=tdm.attr('id')
                if(!id){
                    commservice.alert_message('err',"请求失败",'获取ID失败',true)
                    return false
                }
                var loaddom=commservice.body_loading()
                commservice.request_url('get_'+id+'_main_page','get',{},function(d){
                    loaddom.remove()
                    bodydm.html(scope.$parent.compile(d)(scope.$parent))
                    bodydm.find('.secondary.menu .item').tab()
                    bodydm.find('.ui.selection.dropdown').dropdown()
                    bodydm.find('.datacontent').popup()
                    var totalh=document.body.clientHeight
                    var h1=angular.element('.global > div.head').height()
                    var h2=angular.element('.global > div.divider').height()
                    var nh=50
                    bodydm.find('> .segment').css('height', totalh - h1 - h2 - nh)
                    angular.element('table').tablesort()
                })
			})
        }
    }
})
mainmodule.directive('embed',function(){
    return {
        scope:{},
        restrict:'A',
        link:function(scope, element, attrs){
            var autoplay=element.attr('autoplay')
            element.embed()
            if(autoplay=="yes"){
                element.embed({'autoplay':true})
            }
        }
    }
})
