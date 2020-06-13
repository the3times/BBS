from django.shortcuts import render, HttpResponse, redirect, reverse
from django.http import JsonResponse
from django.views import View
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db import transaction

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random, string, json
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
            print(form_obj.errors)

        return JsonResponse(back_info)


class LoginView(View):
    def get(self, request):
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
                    back_info['url'] = reverse('index')
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


def get_user_avatar(request):
    if request.is_ajax() and request.method == 'POST':
        back_info = {'avatar': ''}
        username = request.POST.get('username')
        user_obj = models.UserInfo.objects.filter(username=username).first()
        if user_obj:
            back_info['avatar'] = user_obj.avatar.name  # 'avatar/default.png'
        return JsonResponse(back_info)
    else:
        return render(request, 'error404.html')


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
    else:
        return render(request, 'error404.html')


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
    print(code)
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

    return render(request, 'blog.html', locals())


def article_detail(request, username, article_id):
    # 判断文章是否存在
    article_obj = models.Article.objects.filter(pk=article_id,
                                                blog__userinfo__username=username).first()
    # username对应的主键为article_id的文章不存在
    if not article_obj:
        return render(request, 'error404.html')
    comment_list = models.Comment.objects.filter(article__pk=article_id)
    blog = article_obj.blog

    return render(request, 'article_detail.html', locals())


def up_and_down(request):
    if request.is_ajax() and request.method == 'POST':
        back_info = {'code': 1000}
        article_id = request.POST.get('article_id')
        is_up = json.loads(request.POST.get('is_up'))   # 反序列化成布尔型
        print(article_id, is_up)
        # 判断当前用户是否登录
        if request.user.is_authenticated:
            # 判断当前用户是否点赞自己的文章
            if not models.Article.objects.filter(pk=article_id, blog__userinfo=request.user):
                # 判断用户是否已经给这篇文章点过赞了
                if not models.UpDown.objects.filter(user=request.user, article__pk=article_id):
                    with transaction.atomic():
                        if is_up:
                            models.Article.objects.filter(pk=article_id).update(up_counts=F('up_counts')+1)
                        else:
                            models.Article.objects.filter(pk=article_id).update(down_counts=F('down_counts')+1)
                        models.UpDown.objects.create(user=request.user, article_id=article_id, is_up=is_up)
                        back_info['msg'] = '成功点赞' if is_up else '成功点踩'
                else:
                    action = models.UpDown.objects.filter(user=request.user, article__pk=article_id).first().is_up
                    back_info['code'] = 1002
                    back_info['msg'] = '您已经点赞了' if action else '您已经点踩了'
            else:
                back_info['code'] = 1003
                back_info['msg'] = '不能给自己点赞哦'
        else:
            back_info['code'] = 1004
            back_info['msg'] = '不<a href="/login/">登录</a>不让点'
        return JsonResponse(back_info)
    else:
        return render(request, 'error404.html')


@login_required
def article_comment(request):
    if request.is_ajax():
        back_info = {'code': 1000}
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')

        if not content:
            back_info['code'] = 2000
            back_info['msg'] = '评论内容不能为空'
            return JsonResponse(back_info)
        with transaction.atomic():
            models.Article.objects.filter(pk=article_id).update(comment_counts=F('comment_counts')+1)
            models.Comment.objects.create(user=request.user, article_id=article_id, content=content, parent_id=parent_id)
            back_info['msg'] = '评论成功'
            return JsonResponse(back_info)
    else:
        return render(request, 'error404.html')

