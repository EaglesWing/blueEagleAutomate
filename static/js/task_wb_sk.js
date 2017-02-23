function left_color_set(task_check){
    if(task_check==undefined){
        var task_check={}
        $('.wb_sk_left #task_zone').each(function(){
            var task_name=$('head title').text().trim()
            var zone_name=$(this).attr('class')
            var task_status=$(this).attr('zone_status')
            var pro=$(this).parent().parent().parent().parent().attr('class').split(' ')[0]
            var agent=$(this).parent().parent().attr('class').split(' ')[0]
            
            if(!(pro in task_check)){
                task_check[pro]={}
            }
            
            if(!(agent in task_check[pro])){
                task_check[pro][agent]={}
            }
            
            if(!(task_status in task_check[pro][agent])){
                task_check[pro][agent][task_status]=[]
            }
            
            task_check[pro][agent][task_status].push(zone_name)
            
        })
    }

    for(pr in task_check){
        for(ag in task_check[pr]){
            var pro_ag=$('.'+pr+'[id="task_pro"] .'+ag+'[id="task_agent"]')
            var failed_c='#c9302c'
            var ready_c='#fcf8e3'
            var running_c='#faf2cc'
            var success_c='#5cb85c'
            if('failed' in task_check[pr][ag]){
                //有failed 业务和代理显示红色
                var color=failed_c
            }else if('ready' in task_check[pr][ag]){
                //有ready 业务和代理显示黄色
                var color=ready_c
            }else if('running' in task_check[pr][ag]){
                //有running 业务和代理显示蓝色
                var color=running_c
            }else if('success' in task_check[pr][ag]){
                //有ready 业务和代理显示绿色
                var color=success_c
            }
            
            pro_ag.each(function(){
                $(this).find(" > a ").css('background-color',color)
                $(this).parent().parent().find(' > a ').css('background-color',color)
            })
            
            for(st in task_check[pr][ag]){
                if(st=="failed"){
                    var color=failed_c
                }
                if(st=="ready"){
                    var color=ready_c
                }
                if(st=="running"){
                    var color=running_c
                }
                if(st=="success"){
                    var color=success_c
                }
                for(z in task_check[pr][ag][st]){
                    pro_ag.find('.'+task_check[pr][ag][st][z]+'[id="task_zone"]').find(" > a ").css('background-color',color)
                }
                
            }
        }
    }
}

function right_color_set(){
    //获取所有任务信息
    var task_status_list={}
    $('#task_server_l > li').next().find('li').each(function(){
        var task_status=$(this).attr('task_status')
        var name=$(this).parent().prev().attr('name')
        var task_name=$(this).attr('name')
        
        if(!(name in task_status_list)){
            task_status_list[name]={}
        }
        if(!(task_status in task_status_list[name])){
            task_status_list[name][task_status]=[]
        }
        task_status_list[name][task_status].push(task_name)
    })

    function get_right_color(d){
        var color=''
        var dt={}
        if(typeof(d)=="string"){
            dt[d]=''
            d=dt
        }
        if('failed' in d){
            color='danger'
        }else if('ready' in d){
            color='warning'
        }else if('running' in d){
            color='info'
        }else if('success' in d){
            color='success'
        }
        return color
    }
    //处理任务信息显示对应颜色
    for(nm in task_status_list){
        var color=get_right_color(task_status_list[nm])
        $('#task_server_l').find('li[name="'+nm+'"]').removeClass('list-group-item-success list-group-item-info list-group-item-warning list-group-item-danger').addClass('list-group-item-'+color)
        for(st in task_status_list[nm]){
            for(d in task_status_list[nm][st]){
                var color=get_right_color(st)
                $('#task_server_l').find('li[name="'+task_status_list[nm][st][d]+'"]').removeClass('list-group-item-success list-group-item-info list-group-item-warning list-group-item-danger').addClass('list-group-item-'+color)
            }
        }
    }
    
}

function task_single_handle_callback(d,des){
    if(d==-1){
        body_alert_evenet('err',des+"失败")
        return false
    }
    if(d==-2){
        body_alert_evenet('err',"参数错误")
        return false
    }
    
    if(des=="exec_task_single"){
        console.log('exec_task_single done')
    }else if(des=='down_task_log'){
        console.log('down_task_log done')
    }
}

function load_right_html(data){
    $('.wb_sk_right').load('task_list_info',data,function(){
        //已开启websocket
        var request={}
        var wd=$('.wb_sk_right #task_server_l').css('width').split('px')[0]
        try{
            var tli_left=$('.wb_sk_right #task_l_info #task_l_info_li').css('left').split('px')[0]
        }catch(e){
            var tli_left=25
        }
        
        
        $('#task_server_l > li').next().find('#task_l_info_li[execute_type="yes"]').unbind('click').click(function(){
            event.stopPropagation()
            var task_status=$(this).attr('task_status')
            if(task_status=="success"||task_status=="done"){
                return false
            }
            var script_name=$(this).attr('name')
            var server_info=$(this).parent().prev().attr('name')
            var this_log=$('.task_log_list').find('div[class="'+server_info+'"]').find('div[class="'+script_name+'"]')
            request['request']='get_task_log'
            request['task_name']=data['task_name']
            request['zone_name']=data['zone_name']
            request['script_name']=script_name
            request['server_info']=server_info
            
            if(script_name!=""){
                this_log.parent().show()
                this_log.children().remove()
                ws.send(obj_to_json(request))
                
            }
        })
        $('#task_server_l > li').next().find('#task_l_info_li #single_task_reexec,#task_l_info_li #download_log').unbind('click').click(function(){
            event.stopPropagation()
            if($(this).prop('disabled')==true){
                return false
            }

            if($(this).attr('id')=="single_task_reexec"){
                var des='exec_task_single'
                $(this).parent().parent().attr('task_status','running')
                $('.task_details_list .'+data['zone_name']).attr('zone_status','running')
            
                right_color_set()
                left_color_set()
            
            }else if($(this).attr('id')=="download_log"){
                var des='down_task_log'
            }else{
                return false
            }
            var script_name=$(this).parent().parent().attr('name')
            var server_info=$(this).parent().parent().parent().prev().attr('name')
            p=build_ajax_data('task_single_handle','post','json',{des:des,task_name:data['task_name'],zone_name:data['zone_name'],script_name:script_name,server_info:server_info})

            if(des=='down_task_log'){
                do_ajax(p,page_jump)
            }else if(des=='exec_task_single'){
                do_ajax(p,get_function_callback(task_single_handle_callback,des))
            }
        })

        $('#task_server_l #task_l_info #task_l_info_li').css('width',Number(wd) - Number(tli_left) - 20+"px")
        
        $('.wb_sk_right #task_l_info').find('li[execute_type="no"]').find('#download_log').prop('disabled',true)
        //执行完成了的任务才能下载日志和单步重新运行脚本
        $('.wb_sk_right #task_l_info').find('li:not([task_status="success"],[task_status="failed"])').find('#download_log,#single_task_reexec').prop('disabled',true)

        //log目录移动
        $('#task_server_l #task_log_d').each(function(){
            $(this).appendTo('.task_log_list')
        })
        $('.wb_sk_right #task_server_l > li').unbind('click').click(function(){
            $('#task_server_l > li').each(function(){
                $(this).next().hide()
                $(this).find(' > span').removeClass('glyphicon-menu-up').addClass('glyphicon-menu-down')
            })
            $(this).next().show()
            $(this).find(' > span').removeClass('glyphicon-menu-down').addClass('glyphicon-menu-up')
        })
        
        right_color_set()
    })
}

function get_web_server_info(d){
    if(d['url']==undefined){
        body_alert_evenet('err',"获取websocket url失败")
    }else{
        function task_log_handle_open(d){
            console.log('websocket conn success.')
            
        }
        function task_log_handle_message(d){
            var d=json_to_obj(d)
            if(d['request']!="task_log_response"){
                return false
            }

            var task_name=d['task_name']
            var zone_name=d['zone_name']
            var script_name=d['script_name']
            var server_info=d['server_info']
            var log=d['response']

  
            $('.task_log_list').find('div[class="'+server_info+'"]').find('div[class="'+script_name+'"]').each(function(){
                var log_list=log.split('\n')
                var p=''
                for(l in log_list){
                    p+="<p style='padding:0px;margin:0px'>"+log_list[l]+"</p>"
                }
                $('.task_log_list #task_log_d').hide()
                //$(this).children().remove()
                $(this).append(p)
                $(this).parent().show() 
                
            })

        }
        function task_log_handle_err(d){
            console.log('websocket conn err.')
            return false
        }
        var url=d['url']
        //创建起websocket，后续使用
        ws=web_socket(url,get_function_callback(task_log_handle_open),get_function_callback(task_log_handle_message),get_function_callback(task_log_handle_err))
        
        var wd=$('.wb_sk_left #task_list_details').css('width').split('px')[0]
        var pr_left=$('.wb_sk_left #task_pro').css('left').split('px')[0]
        var agent_left=Number(pr_left) * 2
        var zone_left=Number(pr_left) * 3
        
                                                                                                            
        $('.wb_sk_left #task_pro').css('width',Number(wd) - Number(pr_left)+"px").unbind('click').click(function(){
            event.stopPropagation()
            $('.wb_sk_left #task_pro').hide()
            $(this).show().find('ul').show()
        })
        $('.wb_sk_left #task_agent').css('width',Number(wd) - Number(agent_left)+"px").unbind('click').click(function(){
            event.stopPropagation()
            $('.wb_sk_left #task_agent #task_zone').hide()
            $(this).show().find(' ul #task_zone').show()
        })
        $('.wb_sk_left #task_zone').each(function(){
            var task_name=$('head title').text().trim()
            var zone_name=$(this).attr('class')
            var task_status=$(this).attr('zone_status')
            var pro=$(this).parent().parent().parent().parent().attr('class').split(' ')[0]
            var agent=$(this).parent().parent().attr('class').split(' ')[0]

            $(this).css('width',Number(wd) - Number(zone_left)+"px").unbind('click').click(function(){
                event.stopPropagation()
                var task_name=$('head title').text().trim()
                var zone_name=$(this).attr('class')
                var tz_wd=$(this).width()
                
                if($(this).find('ul[class="slave_list"]')){
                    //合区场景
                    $(this).find('li').css({'left':'25px','width':tz_wd-25+"px"}).show()
                    $(this).find('li').unbind('click').click(function(){
                        event.stopPropagation()
                        var zone_name=$(this).attr('class')
                        load_right_html({task_name:task_name,zone_name:zone_name})
                    })
                }
                load_right_html({task_name:task_name,zone_name:zone_name})
            })
        })
        //设置左边状态颜色
        left_color_set()
    }
}

$(function(){
    
    //获取服务器信息，创建websocket
    p=build_ajax_data('get_web_server_info','post','json')
    do_ajax(p,get_function_callback(get_web_server_info))
    var task_status_list_check_id=''
    function get_task_status_info_callback(d){
        var task_status=d['task_status']['list_status']
        var task_list_status=d['task_status']['status']

        left_color_set(task_list_status)

        for(tp in task_status){
            for(k in task_status[tp]){
                $('#task_server_l > li[server_type="'+tp+'"]').next().find('li[name="'+k+'"]').attr('task_status',task_status[tp][k])
            }
        }
        
        right_color_set()

    }
    function color_set(){
        if(task_status_list_check_id==''){
            task_status_list_check_id=window.setInterval(color_set,9000)
        }else{
            if($('.task_details_list').length==0){
                window.clearInterval(task_status_list_check_id)
                task_status_list_check_id=''
                return false
            }
        }
        var task_name=$('head title').text().trim()
        p=build_ajax_data('get_task_status_info','post','json',{task_name:task_name})
        do_ajax(p,get_function_callback(get_task_status_info_callback))
    }
    color_set()
})