// 点击验证码图片刷新验证码
$('#code_img').click(function () {
    let oldVal = $(this).attr('src');
    $(this).attr('src', oldVal += '?');
    // $(this).attr('src', '{% url "get_code" %}?')
});

// ajax提交数据
$('#login_btn').click(function () {
    $.ajax({
        url:'/login/',
        type: 'post',
        data:{
            'username': $('#username').val(),
            'password': $('#password').val(),
            'code': $('#code').val()
        },
        success: function (args) {
            if (args.code === 1000){
                $('#myModal').modal('hide');
                window.location.reload();
            }else if(args.code === 3000){
                $('#error_msg').text(args.msg);
            }
            else{
                console.log(args.msg);
                $.each(args.msg, function (field, errors) {
                    $(`#${field}`).next().text(errors[0]).parent().addClass('has-error');
                })
            }
        }
    })
});