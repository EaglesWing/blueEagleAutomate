var loginmodule=angular.module('loginmodule',['commmodule'])
loginmodule.controller('loginctrl', function($scope, commservice){
    $scope.user=''
    $scope.pwd=''
    $scope.newpwd=""
    $scope.newpwda=""
    $scope.newpwdb=""
    $scope.checked=true
    $scope.type=''
    $scope.commservice=commservice
   
    $scope.add_input=function(){
        
    }
    $scope.input_check=function(){
        commservice.field_input_check(angular.element(event.target).parent())
    }
    $scope.do_login=function(){
        event.stopPropagation()
        var btdm=angular.element('.fluid.ui.animated.fade.primary.button')
        if($scope.type=="pwdmodiy"&&$scope.newpwda!=$scope.newpwdb){
            commservice.alert_message('err',"密码输入错误",'新密码和确认密码不一致')
            return false
        }else if($scope.pwd==""||$scope.user==""){
            commservice.alert_message('err','error',"请先输入用户名/密码")
            return false
        }
        if(btdm.hasClass('loading')){
            return false
        }
        btdm.addClass('loading')

        if($scope.type=="pwdmodiy"){
            var data={user:$scope.user,password:$scope.pwd,pwdmodiy:$scope.newpwda}
        }else if($scope.type=="relogin"){
            var data={user:$scope.user,password:$scope.pwd,newpwd:$scope.newpwd,remember:$scope.checked}
        }else{
            var data={user:$scope.user,password:$scope.pwd,remember:$scope.checked}
        }

        commservice.request_url('templates/login.html','post',data,function(d){
            btdm.removeClass('loading')
            if(d['code']==0){
                commservice.page_jump("templates/main.html")
            }else{
                commservice.alert_message('err',d['code'],d['message'])
            }
            
            if(d['code']==-2){
                $scope.add_input()
                $scope.type='relogin'
            }
        },function(d){
            btdm.removeClass('loading')
        })
    }
})

loginmodule.directive('logindct', function(){
    return {
        scope:{},
        restrict:'A',
        controller:function($compile, $scope, $element, $attrs){
            $scope.$parent.add_input=function(a){
                $scope.$parent.type="pwdmodiy"
                if(a){
                    $element.find('input[name="newpwda"]').parent().show()
                    $element.find('input[name="newpwdb"]').parent().show()
                }else{
                    $element.find('input[name="newpwd"]').parent().show()
                }
            }
            $element.find('input#pwd').keyup(function(){
                var code=event.keyCode;
                if(code==13){
                    $scope.$parent.do_login()
                }
            })
            $element.find('.pwdmodfiy').click(function(){
                $scope.$parent.add_input('userpwdmodiy')
            })
        }
    }
})
