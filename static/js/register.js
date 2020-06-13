
$('#id_avatar').change(function () {
    let myFileReaderObj = new FileReader();
    let fileObj = $(this)[0].files[0];
    myFileReaderObj.readAsDataURL(fileObj);
    myFileReaderObj.onload = function () {
        $('#img_avatar').attr('src', myFileReaderObj.result)
    }
});


$('#register_btn').click(function () {
    let formDataObj = new FormData();
    $.each($('#myform').serializeArray(), function (index, obj) {
        formDataObj.append(obj.name, obj.value);
    });
    formDataObj.append('avatar', $('#id_avatar')[0].files[0]);

    $.ajax({
        url:'/register/',
        type: 'post',
        data: formDataObj,
        contentType: false,
        processData: false,
        success: function (args) {
            if (args.code === 1000){
                $('#myRegModal').modal('hide');
                swal("恭喜！", "账号注册成功，请登录", "success");

            }else{
                $.each(args.msg, function (field, errors) {
                    $(`#id_${field}`).next().text(errors[0]).parent().addClass('has-error');
                })
            }
        }
    })
});

$('input').click(function () {
    $(this).next().text('').parent().removeClass('has-error');
});