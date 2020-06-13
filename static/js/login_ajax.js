$('#code_img').click(function () {
    let oldValue = $(this).attr('src');
    $(this).attr('src', oldValue+'?')
});

$('#login_btn').click(function () {
    $.ajax({
        url:'/login/',
        type: 'post',
        data:{
            'username': $('#id_username').val(),
            'password': $('#id_password').val(),
            'code': $('#id_code').val()
        },
        success: function (args) {
            if (args.code === 1000){
                $('#myModal').modal('hide');
                window.location.href = args.url;
            }else if(args.code === 3000){
                $('#error_msg').text(args.msg);
            }
            else{
                console.log(args.msg);
                $.each(args.msg, function (field, errors) {
                    $(`#id_${field}`).next().text(errors[0]).parent().addClass('has-error');
                })
            }
        }
    })
});