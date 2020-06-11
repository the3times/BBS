from django.shortcuts import render, HttpResponse, redirect, reverse
from django.http import JsonResponse
from django.views import View
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random, string
from app01 import myforms, models


class RegView(View):
    def get(self, request):
        form_obj = myforms.RegForm()
        return render(request, 'register.html', locals())

    def post(self, request):
        back_info = {'code': 1000}
        form_obj = myforms.RegForm(request.POST)
        if form_obj.is_valid():
            cleaned_data = form_obj.cleaned_data
            cleaned_data.pop('re_password')
            avatar = request.FILES.get('avatar')
            if avatar: cleaned_data['avatar'] = avatar
            models.UserInfo.objects.create_user(**cleaned_data)
            back_info['url'] = reverse('index')
        else:
            back_info['code'] = 2000
            back_info['msg'] = form_obj.errors

        return JsonResponse(back_info)


class LoginView(View):
    def get(self, request):
        form_obj = myforms.LoginForm()
        return render(request, 'login.html', locals())

    def post(self, request):
        back_info = {'code': 1000}
        form_obj = myforms.LoginForm(request.POST)
        if form_obj.is_valid():
            code = request.POST.get('code')
            if code.lower() == request.session.get('code').lower():
                user_obj = auth.authenticate(request, **form_obj.cleaned_data)
                if user_obj:
                    auth.login(request, user_obj)
                    back_info['msg'] = '登录成功'
                    back_info['url'] = reverse('login')
                else:
                    back_info['code'] = 3000
                    back_info['msg'] = '用户名或密码错误'
            else:
                back_info['code'] = 3000
                back_info['msg'] = '验证码错误'
        else:
            back_info['code'] = 2000
            back_info['msg'] = form_obj.errors
        return JsonResponse(back_info)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')


@login_required
def reset_password(request):
    if request.is_ajax():
        back_info = {'code': 1000}
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        re_password = request.POST.get('re_password')
        if not request.user.check_password(old_password):
            back_info['code'] = 2000
            back_info['msg'] = '原密码错误'
        else:
            if new_password and re_password and new_password == re_password:
                request.user.set_password(re_password)
                request.user.save()
            else:
                back_info['code'] = 2000
                back_info['msg'] = '两次密码输入不一致或密码输入为空'
        return JsonResponse(back_info)


def get_code(request):

    def get_random():
        rgb_list = []
        for _ in range(3):
            rgb_list.append(random.randint(0, 255))
        return tuple(rgb_list)

    img_obj = Image.new('RGB', (380, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/font.ttf', 30)  # 字体样式 大小
    digits_letters = string.digits + string.ascii_letters
    code = ''.join(random.choices(digits_letters, k=5))
    for i in range(5):
        tmp = code[i]
        img_draw.text((i*60+60, -2), tmp, get_random(), img_font)

    request.session['code'] = code.lower()
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def index(request):
    article_queryset = models.Article.objects.all()
    form_obj = myforms.RegForm()
    return render(request, 'index.html', locals())


def blog(request, username, **kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'error404.html')
    blog = user_obj.blog
    article_queryset = models.Article.objects.filter(blog=blog)
    # 按照标签、分类、归档条件查询文章的情况
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'tag':
            article_queryset = article_queryset.filter(tags__pk=param).all()
        elif condition == 'category':
            article_queryset = article_queryset.filter(category__pk=param).all()
        else:
            year, month = param.split('-')
            article_queryset = article_queryset.filter(publish_time__year=year,
                                                       publish_time__month=month).all()
    # 标签、分类、归档ORM查询
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article__pk')).values('pk', 'name', 'c')
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article__pk')).values('pk', 'name', 'c')
    # 日期归档查询使用django提供的TruncMonth自动按月截取，形成一个虚拟字段用于日期分组
    archive_list = models.Article.objects.filter(blog=blog).\
    annotate(month=TruncMonth('publish_time')).values('month').\
        annotate(c=Count('pk')).order_by('-month').values('month', 'c')

    return render(request, 'blog.html', locals())
