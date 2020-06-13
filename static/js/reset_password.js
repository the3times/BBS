$('#resetpwd_btn').click(function () {
    $.ajax({
        url:'/reset_password/',
        type: 'post',
        data:{
            'old_password': $('#old_password').val(),
            'new_password': $('#new_password').val(),
            're_password': $('#re_password').val(),
        },
        success: function (args) {
            if (args.code === 1000){
                $('#mySetPwdModal').modal('hide');
                swal("恭喜！", "密码修改成功, 请重新登录", "success");
            }else{
                $('#setpwd_error_msg').text(args.msg);
            }
        }
    })
});