from django import forms
from app01 import models


class RegForm(forms.Form):
    username = forms.CharField(label='用户名',
                               error_messages={'required': '用户名不能为空'},
                               widget=forms.widgets.TextInput())

    password = forms.CharField(label='密码', min_length=6, max_length=12,
                               error_messages={
                                   'required': '密码不能为空',
                                   'min_length': '密码不能少于6位',
                                   'max_length': '密码不能多于12位'},
                               widget=forms.widgets.PasswordInput())

    re_password = forms.CharField(label='确认密码', min_length=6, max_length=12,
                                  error_messages={
                                      'required': '确认密码不能为空',
                                      'min_length': '确认密码不能少于6位',
                                      'max_length': '确认密码不能多于12位'},
                                  widget=forms.widgets.PasswordInput())

    email = forms.EmailField(label='邮箱',
                             error_messages={
                                 'required': '邮箱不能为空',
                                 'invalid': '邮箱格式不正确'},
                             widget=forms.widgets.EmailInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # 单例模式
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if models.UserInfo.objects.filter(username=username):
            self.add_error('username', '用户名已经存在')
        return username

    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password != re_password:
            self.add_error('re_password', '两次密码输入不一致')
        return self.cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名',
                               error_messages={'required': '用户名不能为空'},
                               widget=forms.widgets.TextInput())

    password = forms.CharField(label='密码', min_length=3, max_length=12,
                               error_messages={
                                   'required': '密码不能为空',
                                   'min_length': '密码不能少于6位',
                                   'max_length': '密码不能多于12位'},
                               widget=forms.widgets.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class ArticleAddForm(forms.Form):
    title = forms.CharField(label='标题', error_messages={'required': '标题不能为空'})
    content = forms.CharField(label='文章内容', error_messages={'required': '文章内容不能为空'})


class ArticleEditForm(ArticleAddForm):
    content = forms.CharField(label='文章内容',
                              widget=forms.widgets.Textarea(),
                              error_messages={'required': '文章内容不能为空'})
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
