/*------------------------------------------------
对新增服务器的表单界面做了导向流的功能, 并实现使用modal窗口快速添加关联数据
内部实现是三个函数：
_quick_add： 打开xxx资源的添加窗口
_change_form_to_modal: 由于复用了原表单页面交互，需要将表单适配成modal可用
reload_options：在添加完成后，需要将新增的数据添加到选择框里去
----------------------------------------------------
 */
var QUICK_ADD_RESOURCES ={
    "server_device": {
        "name":"server_device",
        "div_name":"server_device",
        "modal_height": 400   //快速添加modal弹窗的高度(px) 可选，默认400
    },
    "server_role": {
        "name":"server_role",
        "div_name":"role",
        "modal_height": 750,
        "func_form_customize": function(sub_form){
            sub_form.find(".ace_editor").parent(".col-lg-8")
               .addClass("col-lg-10").addClass("col-md-10")
               .removeClass("col-lg-8").addClass("col-md-8")
        }   //可选，用于子表单的一些调整，以适用于modal
    },
    "server_group":{
        "name":"server_group",
        "div_name":"group",
        "modal_height": 450
    },
    "idc":{
        "name":"idc",
        "div_name":"group",
        "modal_height": 450
    },
    "project":{
        "name":"project",
        "div_name":"group",
        "modal_height": 450
    },
    "user":{
        "name":"user",
        "div_name":"group",
        "modal_height": 450
    },
    "group":{
        "name":"group",
        "div_name":"group",
        "modal_height": 450
    },
    "permission":{
        "name":"permission",
        "div_name":"group",
        "modal_height": 450
    },
}

/*
 * 打开快速添加弹窗
 * param resource: 资源的信息字典，包括group, name，和div_name
*                  group主要用于组装资源路径，比如/cmdb/server_device/
*                  div_name是这个资源在表单里的div的命名，一般是简写，比如server_group就是group
*  param scope_div: 在快捷添加成功后，需要重新加载select控件，那么去哪里找到这个对应的资源的select控件呢？
*                   所以指定作用范围，避免影响到全网页的其他html控件, 比如可以传入form表单范围
*
 */
function quick_add(scope_div, resource_name){
    var resource = QUICK_ADD_RESOURCES[resource_name]
    $.ajax({
        url: '/cmdb/' + resource.name + '/add/0/',
        data: {},
        type: 'GET',
        dataType: 'html',
        success: function(form_html){
            //var r_obj = _change_form_to_modal(scope_div, resource, form_html)

            bootbox.dialog({
                message: form_html,
                title: "快捷添加数据项",
                size: "large"
                //callback: function(result){ alert(123) }
            })
        }
    })
}

function quick_edit(scope_div, resource_name, resource_id){
    var resource = QUICK_ADD_RESOURCES[resource_name]
    $.ajax({
        url: '/cmdb/' + resource_name + '/modify/' + resource_id + "/",
        data: {},
        type: 'GET',
        dataType: 'html',
        success: function(form_html){
            //var r_obj = _change_form_to_modal(scope_div, resource, form_html)

            bootbox.dialog({
                message: form_html,
                title: "快捷编辑数据项",
                size: "large"
                //callback: function(result){ alert(123) }
            })
        }
    })
}

//将添加页面的表单嵌入到modal时，有很多地方需要hack一下
function _change_form_to_modal(scope_div, resource, form_html){
    var _modal_height = resource.modal_height || 400 //默认高度

    var r_obj = $(form_html)
    var sub_form = r_obj.find("form")
    //sub_form.append('<a id="fast_submit" class="btn btn-primary pull-right"><i class="glyphicon glyphicon-plus"></i> 确定添加</a>')

    //对子表单做一些定制的小调整
    if(resource.func_form_customize){
        resource.func_form_customize(sub_form)
    }

    //在modal里也强制锁定关联项的选择框 (比如添加主机时服务器角色和分组的modal里的项目选择框是不可选的)
    var top_level_proj = scope_div.find("select[name=project]")
    var selected_proj_id = parseInt(top_level_proj.val())

    if(resource.name != "project"){
        var sub_proj = sub_form.find("select[name=project]")
        sub_proj.select2().val(selected_proj_id).trigger("change")
                //.prop("disabled", true);//这里select2 4.0有个bug，disabled后form获取不了这个参数，但是目前又不支持readonly
        //有一种办法是在form提交事件之前把所有select重新enable，这里暂时采用把鼠标禁用的方式
        window.setTimeout(function(){
            sub_proj.siblings(".select2").css('pointer-events','none'), 500
        })
    }

    //快速新增的按钮的响应
    sub_form.find("#fast_submit").on("click", function(){
        before_submit();
        $.ajax({
           type: "POST",
           url: '/' + resource.group + '/' + resource.name + "/add_modify/0/",
           data: sub_form.serialize(),
           success: function(resp)
           {
                // 表单验证失败
                if(resp.indexOf(resource.div_name + "data_0") > -1){
                    r_obj.html(
                        _change_form_to_modal(scope_div, resource, resp)
                    )
                }else{
                    reload_options(scope_div, resource.name, true);
                    bootbox.alert("添加数据项成功", function(){
                        bootbox.hideAll();
                    })
                }
           },
            error:function(data){
                alert("系统异常，请联系开发")
            }
         });
    })
    return sub_form
}

//快捷添加数据项后，重新加载下拉框选项，并且按倒序排列，将最新的放在最上面
//select_new_added：是否自动选中新增的选项
function reload_options(scope_div, resource_name, select_new_added){
    var data = {"format":"json"}
    var resource = QUICK_ADD_RESOURCES[resource_name]

    //如果选中了项目，则在加载数据选项时，需要加入项目的过滤条件
    var project_div = scope_div.find("select[name=project]")
    var selected_proj_name = project_div.select2("data")[0].text.trim()
    if(resource.name != "project"){
        data.search_field = "project__name"
        data.search_text = selected_proj_name
    }

    $.ajax({
        url: '/' + resource.group + '/' + resource.name + '/show/',
        data: data,
        type: 'GET',
        dataType: 'json',
        success: function(data){
            var options = []
            for(var i = 0; i < data.length; i++){
                var obj = data[i];
                options.push({
                    "id": obj.id,
                    "text": obj.name.value
                })
            }

            var origin_select = $(scope_div).find("select[name=" +resource.div_name+ "]")
            var old_selection = origin_select.val();

            origin_select.empty().select2({
                "data":options,
                "width":origin_select.siblings(".select2").css("width")
            })

            if(select_new_added && options.length > 0){
                //如果是多选框
                if(old_selection instanceof Array){
                    old_selection.push(data[0].id)
                    origin_select.val(old_selection).trigger("change")
                }else{
                    origin_select.val(data[0].id).trigger("change")
                }
            }
        }
    })
}

//删除数据
function delete_one_data(model, id){
    var resource = QUICK_ADD_RESOURCES[model];

    bootbox.confirm("你确定要删除?", function(result) {
        if(result){
             $.ajax({
                 url: '/cmdb/' + resource.name + '/delete/'+ id + "/",
                 type: 'GET',
                  success: function() {
                      window.location = '/cmdb/' + resource.name + '/show';
                  }
             })
        }
    });
}


function clean_error_msg(form){
    form.find(".form-group").removeClass("has-error")
    form.find(".errormsg").hide()
}

function show_error_msg(form, errors){
    $.each(errors, function(field, errors){
        var err_group = $("[name=" +field+ "]").parents(".form-group")
        err_group.addClass("has-error")
        var err_msg = $("<div/>")
        err_msg.addClass("errormsg").css("color", "red").append(errors)
        err_group.find('.control-group').append(err_msg)
    })
}