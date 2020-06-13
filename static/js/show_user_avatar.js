$(function () {

    //输入用户名，提示头像信息事件
    $("#id_username").change(function () {

        $.ajax({
            url: "/get_user_avatar/",
            type: "post",
            data: {
                'username': $("#id_username").val(),
            },
            success: function (args) {
                if (args.avatar) {
                    $("#login_show_avatar").attr("src", '/media/' + args.avatar);
                }
            }
        })
    });


});